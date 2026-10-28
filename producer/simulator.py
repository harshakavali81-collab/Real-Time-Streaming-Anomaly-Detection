"""Ground-truth-labelled, seeded and explicitly synthetic telemetry generator."""
import random
from datetime import datetime, timedelta, timezone
from src.schema import TelemetryEvent

SERVICES = ("checkout", "payments", "search", "identity")
BASELINES = {
    "checkout": (170, 45, .008, 85),
    "payments": (230, 58, .012, 54),
    "search": (75, 34, .004, 210),
    "identity": (120, 40, .006, 100),
}

def generate_event(index: int, seed: int = 42, anomaly_rate: float = .08,
                   base_time: datetime | None = None, interval_seconds: float = .2) -> TelemetryEvent:
    if not 0 <= anomaly_rate <= 1:
        raise ValueError("anomaly_rate must be between 0 and 1")
    rng = random.Random(seed * 9973 + index * 7919)
    service = SERVICES[index % len(SERVICES)]
    latency, cpu, errors, rps = BASELINES[service]
    anomalous = rng.random() < anomaly_rate
    x_latency = max(1.0, rng.gauss(latency, latency*.11))
    x_cpu = min(100.0, max(0.0, rng.gauss(cpu, 4)))
    x_error = min(1.0, max(0.0, rng.gauss(errors, .003)))
    x_rps = max(0.0, rng.gauss(rps, rps*.08))
    if anomalous:
        kind = index % 3
        if kind == 0:
            x_latency *= 6.0
        elif kind == 1:
            x_cpu = min(100, x_cpu + 52)
            x_error = min(1, x_error + .27)
        else:
            x_error = min(1, x_error + .38)
            x_rps *= 2.3
    now = base_time or datetime.now(timezone.utc)
    timestamp = now + timedelta(seconds=index * interval_seconds) if base_time else now
    return TelemetryEvent(
        event_id=f"evt-{seed:06d}-{index:08d}", service=service, timestamp=timestamp,
        latency_ms=round(x_latency, 3), cpu_pct=round(x_cpu, 3),
        error_rate=round(x_error, 5), rps=round(x_rps, 2),
        ground_truth=anomalous, source="simulator"
    )
