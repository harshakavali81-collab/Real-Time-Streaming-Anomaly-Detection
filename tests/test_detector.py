from producer.simulator import generate_event
from src.models.detector import OnlineDetector, RunningStat

def test_running_stat_correct_mean_and_z():
    stat = RunningStat()
    for n in (4, 6, 8):
        stat.observe(n)
    assert stat.mean == 6
    assert stat.z(50) > 10

def test_detector_warmup():
    d = OnlineDetector(warmup=8)
    for i in range(8):
        result = d.score(generate_event(i*4, anomaly_rate=0))
        assert not result.anomaly

def test_detector_spike_and_no_poisoning():
    d = OnlineDetector(warmup=10, threshold=3.6)
    for i in range(15):
        d.score(generate_event(i*4, anomaly_rate=0))
    before = d.profiles["checkout"].stats[0].count
    event = generate_event(64, anomaly_rate=0).model_copy(update={"latency_ms": 8500})
    outcome = d.score(event)
    assert outcome.anomaly
    assert "latency" in outcome.reason
    assert d.profiles["checkout"].stats[0].count == before

def test_invalid_threshold():
    import pytest
    with pytest.raises(ValueError):
        OnlineDetector(warmup=1)
