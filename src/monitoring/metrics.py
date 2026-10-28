"""Worker-local Prometheus exporter (not aggregated across processes)."""
from prometheus_client import Counter, Histogram, Gauge

PROCESSED = Counter("streamwatch_processed_total", "Persisted valid events", ["service"])
ANOMALIES = Counter("streamwatch_anomalies_total", "Flagged events", ["service"])
INVALID = Counter("streamwatch_invalid_total", "Quarantined invalid events")
INFERENCE = Histogram("streamwatch_inference_seconds", "Scoring and persistence time")
CONSUMER_UP = Gauge("streamwatch_consumer_up", "Consumer loop is running")
