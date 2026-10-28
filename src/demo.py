"""Run an offline end-to-end event->validation->model->SQL->metrics demo."""
import argparse
import json
from datetime import datetime, timedelta, timezone
from producer.simulator import generate_event
from src.models.detector import OnlineDetector
from src.service import ingest
from src.sinks.store import Store

def run_demo(events: int = 1000, db: str = "sqlite:///./streamwatch.db", seed: int = 42) -> dict:
    if events < 1:
        raise ValueError("events must be positive")
    store = Store(db)
    detector = OnlineDetector()
    base = datetime.now(timezone.utc) - timedelta(seconds=events / 5)
    inserted = flagged = 0
    for i in range(events):
        event = generate_event(i, seed=seed, base_time=base)
        saved, is_anomaly = ingest(event, store, detector)
        inserted += int(saved)
        flagged += int(is_anomaly)
    return {"mode": "offline synthetic", "inserted": inserted, "flagged": flagged,
            "summary": store.summary(max(60, int(events/300)+1)),
            "note": "End-to-end measurements depend on local hardware; labels are simulated."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--events", type=int, default=1000)
    p.add_argument("--db", default="sqlite:///./streamwatch.db")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    print(json.dumps(run_demo(args.events, args.db, args.seed), indent=2))
