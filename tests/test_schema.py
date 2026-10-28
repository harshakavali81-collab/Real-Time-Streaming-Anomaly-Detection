from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from producer.simulator import generate_event
from src.schema import TelemetryEvent
from src.features.transform import to_vector

def test_simulator_reproducible():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert generate_event(24, base_time=base) == generate_event(24, base_time=base)

def test_anomaly_probability_bounds():
    with pytest.raises(ValueError):
        generate_event(1, anomaly_rate=1.5)

def test_infinite_values_rejected():
    e = generate_event(1)
    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate({**e.model_dump(), "latency_ms": float("inf")})

def test_timezone_required():
    e = generate_event(1)
    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate({**e.model_dump(), "timestamp": "2026-03-04T00:00:00"})

def test_forbid_extra_fields():
    e = generate_event(1)
    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate({**e.model_dump(), "hidden": "unexpected"})

def test_feature_vector_has_four_finite_values():
    vector = to_vector(generate_event(8))
    assert len(vector) == 4
    assert all(x >= 0 for x in vector)
