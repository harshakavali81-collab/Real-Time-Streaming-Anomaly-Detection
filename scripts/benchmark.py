"""Local SINGLE-PROCESS synthetic benchmark. Not Kafka throughput or production SLA."""
import argparse
import json
from time import perf_counter
from producer.simulator import generate_event
from src.models.detector import OnlineDetector
from src.service import ingest
from src.sinks.store import Store

def measure(n: int = 1000) -> dict:
    if n < 1:
        raise ValueError("n must be positive")
    store = Store("sqlite:///:memory:")
    model = OnlineDetector()
    start = perf_counter()
    anomalies = 0
    for i in range(n):
        saved, flagged = ingest(generate_event(i, anomaly_rate=0.08), store, model)
        assert saved
        anomalies += int(flagged)
    duration = perf_counter()-start
    return {"benchmark_type": "single-process Python + SQLite in-memory",
            "sample_source": "seeded synthetic simulator", "events": n,
            "wall_seconds": round(duration, 4),
            "observed_events_per_second": round(n/duration, 2),
            "anomalies": anomalies,
            "processing_p95_ms": store.summary()["p95_processing_ms"],
            "evaluation": store.summary()["evaluation"],
            "warning": "No Kafka broker, network, concurrency or real data in this benchmark."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--events", type=int, default=1000)
    args = p.parse_args()
    print(json.dumps(measure(args.events), indent=2))
