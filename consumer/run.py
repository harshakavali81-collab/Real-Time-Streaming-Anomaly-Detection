"""Kafka at-least-once consumer. Commit offsets only after SQL/DLQ acknowledgement."""
import json
import logging
import os
from confluent_kafka import Consumer, KafkaError, Producer
from pydantic import ValidationError
from prometheus_client import start_http_server
from src.models.detector import OnlineDetector
from src.monitoring.metrics import PROCESSED, ANOMALIES, INVALID, INFERENCE, CONSUMER_UP
from src.schema import TelemetryEvent
from src.service import ingest
from src.alerts.dlq import quarantine_record
from src.sinks.store import Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger(__name__)

def run() -> None:
    broker = os.getenv("KAFKA_BOOTSTRAP", "localhost:19092")
    topic = os.getenv("KAFKA_TOPIC", "telemetry.events.v1")
    dlq = os.getenv("KAFKA_DLQ_TOPIC", "telemetry.invalid.v1")
    consumer = Consumer({
        "bootstrap.servers": broker,
        "group.id": os.getenv("KAFKA_GROUP", "streamwatch-worker-v1"),
        "enable.auto.commit": False,
        "auto.offset.reset": "earliest"
    })
    publisher = Producer({"bootstrap.servers": broker, "enable.idempotence": True})
    store = Store()
    detector = OnlineDetector(
        warmup=int(os.getenv("WARMUP_EVENTS", "25")),
        threshold=float(os.getenv("ANOMALY_THRESHOLD", "3.6"))
    )
    restored = store.restore_detector(detector)
    LOG.info("Restored %s persisted anomaly-model observations", restored)
    start_http_server(int(os.getenv("WORKER_METRICS_PORT", "9100")))
    consumer.subscribe([topic])
    CONSUMER_UP.set(1)
    LOG.info("Consuming %s; invalid events go to %s", topic, dlq)
    try:
        while True:
            msg = consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                LOG.error("Kafka consumer error: %s", msg.error())
                continue
            try:
                event = TelemetryEvent.model_validate_json(msg.value())
            except (ValidationError, ValueError) as err:
                # Never acknowledge malformed payloads unless DLQ delivery succeeded.
                result = quarantine_record(msg, err)
                failures = []
                publisher.produce(dlq, value=json.dumps(result).encode(),
                                  on_delivery=lambda error, _: failures.append(str(error)) if error else None)
                remaining = publisher.flush(15)
                if remaining or failures:
                    LOG.error("DLQ publish failed; NOT committing Kafka offset: %s", failures)
                    raise RuntimeError("DLQ delivery failed")
                INVALID.inc()
                consumer.commit(message=msg, asynchronous=False)
                continue
            with INFERENCE.time():
                saved, flagged = ingest(event, store, detector)
            if saved:
                PROCESSED.labels(event.service).inc()
                if flagged:
                    ANOMALIES.labels(event.service).inc()
            consumer.commit(message=msg, asynchronous=False)
    except KeyboardInterrupt:
        LOG.info("Consumer interrupted")
    finally:
        CONSUMER_UP.set(0)
        consumer.close()
        publisher.flush(10)

if __name__ == "__main__":
    run()
