"""Optional offline IsolationForest experiment on seeded synthetic events.

Outputs are never described as real-world validated performance.
"""
import argparse
import json
from pathlib import Path
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_fscore_support
from producer.simulator import generate_event
from src.features.transform import to_vector

def train(output: str = "artifacts/isolation_forest.joblib", n: int = 4000, seed: int = 42) -> dict:
    # Chronological train/test split; training is normal-only SIMULATED data.
    if n < 200:
        raise ValueError("n must be >= 200")
    events = [generate_event(i, seed=seed, anomaly_rate=0.08) for i in range(n)]
    split = int(n * 0.75)
    normal_train = [to_vector(e) for e in events[:split] if e.ground_truth is False]
    test_x = [to_vector(e) for e in events[split:]]
    truth = [bool(e.ground_truth) for e in events[split:]]
    model = IsolationForest(n_estimators=120, contamination=0.08, random_state=seed, n_jobs=1)
    model.fit(normal_train)
    predicted = [v == -1 for v in model.predict(test_x)]
    p, r, f1, _ = precision_recall_fscore_support(truth, predicted, average="binary", zero_division=0)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, destination)
    metrics = {"dataset": "synthetic", "samples": n, "train_normal": len(normal_train),
               "test_samples": len(test_x), "precision": round(float(p), 4),
               "recall": round(float(r), 4), "f1": round(float(f1), 4),
               "note": "Offline experiment only; production worker defaults to online z-score"}
    destination.with_suffix(".metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/isolation_forest.joblib")
    parser.add_argument("--samples", type=int, default=4000)
    args = parser.parse_args()
    print(json.dumps(train(args.output, args.samples), indent=2))
