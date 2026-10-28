"""Deterministic feature engineering; no future information is used."""
from math import log1p
from src.schema import TelemetryEvent

FEATURE_NAMES = ("log_latency", "cpu_ratio", "error_rate", "log_rps")

def to_vector(event: TelemetryEvent) -> list[float]:
    return [log1p(event.latency_ms), event.cpu_pct / 100.0, event.error_rate, log1p(event.rps)]
