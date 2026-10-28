"""Publishes JSON telemetry to Redpanda/Kafka; explicit synthetic source only."""
import logging
import os
import time
import uuid
from confluent_kafka import Producer
from producer.simulator import generate_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger(__name__)

def main() -> None:
    broker = os.getenv("KAFKA_BOOTSTRAP", "localhost:19092")
    topic = os.getenv("KAFKA_TOPIC", "telemetry.events.v1")
    rate = float(os.getenv("EVENTS_PER_SECOND", "5"))
    if not 0 < rate <= 10000:
        raise ValueError("EVENTS_PER_SECOND must be >0 and <=10000")
    anomaly_rate = float(os.getenv("SIMULATED_ANOMALY_RATE", "0.08"))
    producer = Producer({"bootstrap.servers": broker,
                         "client.id": "streamwatch-sim-producer",
                         "enable.idempotence": True, "acks": "all"})
    def delivery(err, msg):
        if err:
            LOG.error("Failed to deliver event: %s", err)
    sequence = 0
    LOG.info("Starting SYNTHETIC producer; broker=%s topic=%s rate=%.2f/s", broker, topic, rate)
    try:
        while True:
            event = generate_event(sequence, anomaly_rate=anomaly_rate).model_copy(
                update={"event_id": uuid.uuid4().hex}
            )
            while True:
                try:
                    producer.produce(topic, key=event.service.encode(),
                                     value=event.model_dump_json().encode(),
                                     on_delivery=delivery)
                    break
                except BufferError:
                    producer.poll(.1)  # bounded retry under broker backpressure
            producer.poll(0)
            sequence += 1
            time.sleep(1.0 / rate)
    except KeyboardInterrupt:
        LOG.info("Shutting down producer")
    finally:
        remaining = producer.flush(15)
        if remaining:
            LOG.error("%s messages not delivered before shutdown", remaining)

if __name__ == "__main__":
    main()
