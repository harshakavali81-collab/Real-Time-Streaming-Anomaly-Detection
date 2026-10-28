from producer.simulator import generate_event
from src.models.detector import Detection, OnlineDetector
from src.service import ingest

def test_insert_idempotent(store):
    e = generate_event(1)
    saved, flagged = ingest(e, store, OnlineDetector())
    assert saved and not flagged
    saved, flagged = ingest(e, store, OnlineDetector())
    assert not saved and not flagged
    assert store.summary()["events"] == 1

def test_alert_lifecycle(store):
    e = generate_event(18)
    assert store.save(e, Detection(6.2, True, "latency deviation"))
    row = store.list_events(anomaly_only=True)[0]
    assert row["severity"] == "critical"
    assert row["status"] == "new"
    assert store.update_status(e.event_id, "investigating")["status"] == "investigating"
    assert store.update_status(e.event_id, "resolved")["status"] == "resolved"
    assert store.summary()["pending"] == 0

def test_not_found_status(store):
    assert store.update_status("not-exists", "resolved") is None

def test_normal_not_triageable(store):
    e = generate_event(8)
    store.save(e, Detection(0.4, False, "within baseline"))
    assert store.update_status(e.event_id, "resolved") is None

def test_summary_label_metrics(store):
    a = generate_event(10, anomaly_rate=1)
    b = generate_event(11, anomaly_rate=0)
    store.save(a, Detection(5, True, "spike"))
    store.save(b, Detection(1, False, "normal"))
    m = store.summary()
    assert m["evaluation"]["precision"] == 1
    assert m["evaluation"]["recall"] == 1
    assert m["evaluation"]["labelled"] == 2

def test_trends(store):
    e = generate_event(0)
    store.save(e, Detection(0, False, "baseline"))
    trend = store.trends()
    assert len(trend) == 1
    assert trend[0]["events"] == 1
