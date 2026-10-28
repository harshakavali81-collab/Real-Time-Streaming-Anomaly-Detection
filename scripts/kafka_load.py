"""Controlled local Kafka producer load. Output is broker ack performance only.

It is NOT throughput of the ML worker, SQL database, or full end-to-end service.
Only use against an authorized local/test broker.
"""
import argparse
import json
import time
import uuid
from confluent_kafka import Producer
from producer.simulator import generate_event

def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[min(len(ordered)-1, int((len(ordered)-1)*p))], 3)

def measure(events: int = 1000, rate: float = 50.0,
            bootstrap: str = "localhost:19092", seed: int = 42,
            anomaly_rate: float = .08) -> dict:
    if not 1 <= events <= 1_000_000:
        raise ValueError("events must be 1 to 1,000,000")
    if not 0 < rate <= 10000:
        raise ValueError("rate must be >0 and <=10000 events/sec")
    if not 0 <= anomaly_rate <= 1:
        raise ValueError("anomaly_rate must be 0..1")
    producer = Producer({"bootstrap.servers": bootstrap, "acks":"all",
                         "enable.idempotence": True})
    run_id = uuid.uuid4().hex[:12]
    ack_ms = []
    failures = []
    t0 = time.perf_counter()
    interval = 1.0/rate
    for index in range(events):
        event = generate_event(index, seed=seed, anomaly_rate=anomaly_rate).model_copy(
            update={"event_id": f"load-{run_id}-{index}"})
        start = time.perf_counter()
        def delivered(err, message, submitted=start):
            if err:
                failures.append(str(err))
            else:
                ack_ms.append((time.perf_counter()-submitted)*1000)
        while True:
            try:
                producer.produce("telemetry.events.v1", key=event.service.encode(),
                                 value=event.model_dump_json().encode(),
                                 on_delivery=delivered)
                break
            except BufferError:
                producer.poll(.1)  # prevent unbounded local queue memory
        producer.poll(0)
        deadline = t0+(index+1)*interval
        remaining = deadline-time.perf_counter()
        if remaining > 0:
            time.sleep(remaining)
    unflushed = producer.flush(40)
    elapsed = time.perf_counter()-t0
    return {"mode":"local synthetic Kafka producer; delivery acknowledgements only",
            "bootstrap":bootstrap, "events_attempted":events, "acknowledged":len(ack_ms),
            "delivery_failures":len(failures), "unflushed":unflushed,
            "elapsed_seconds":round(elapsed,3),
            "acknowledged_per_second":round(len(ack_ms)/elapsed,2),
            "broker_ack_p50_ms":percentile(ack_ms,.50),
            "broker_ack_p95_ms":percentile(ack_ms,.95),
            "data_source":"seeded synthetic telemetry",
            "warning":"NOT consumer throughput, SQL latency, end-to-end SLA or independent model validation"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--events",type=int,default=1000)
    parser.add_argument("--rate",type=float,default=50)
    parser.add_argument("--broker",default="localhost:19092")
    parser.add_argument("--seed",type=int,default=42)
    parser.add_argument("--anomaly-rate",type=float,default=.08)
    args=parser.parse_args()
    print(json.dumps(measure(args.events,args.rate,args.broker,args.seed,args.anomaly_rate),indent=2))
