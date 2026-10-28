"""Recovery and durable audit invariants tested on SQLite."""
from producer.simulator import generate_event
from src.models.detector import OnlineDetector, Detection
from src.service import ingest
from src.sinks.store import Store

def test_restore_exact_model_statistics(tmp_path):
    db = Store("sqlite:///" + str(tmp_path / "resume.db"))
    old = OnlineDetector(warmup=8)
    for i in range(55):
        assert ingest(generate_event(i, seed=100, anomaly_rate=.2), db, old)[0]
    restored = OnlineDetector(warmup=8)
    assert db.restore_detector(restored) == 55
    assert old.profiles.keys() == restored.profiles.keys()
    for service in old.profiles:
        a, b = old.profiles[service], restored.profiles[service]
        assert a.observed == b.observed
        for stat, other in zip(a.stats, b.stats):
            assert stat.count == other.count
            assert abs(stat.mean - other.mean) < 1e-12
            assert abs(stat.m2 - other.m2) < 1e-10
    future = generate_event(57, seed=100, anomaly_rate=.2)
    assert old.score(future) == restored.score(future)

def test_replay_does_not_relearn_existing_event(store):
    model = OnlineDetector()
    event = generate_event(2, seed=900)
    assert ingest(event, store, model)[0]
    fresh = OnlineDetector()
    assert store.restore_detector(fresh) == 1
    assert ingest(event, store, fresh) == (False, False)
    assert fresh.profiles[event.service].observed == 1

def test_audit_transitions_persist(store):
    event = generate_event(11, seed=40, anomaly_rate=1)
    store.save(event, Detection(6.1, True, "cpu deviation"))
    store.update_status(event.event_id, "investigating", "token-authenticated")
    store.update_status(event.event_id, "investigating", "token-authenticated")
    store.update_status(event.event_id, "resolved", "token-authenticated")
    audit = store.audit_history(event.event_id)
    assert len(audit) == 2
    assert audit[0]["previous_status"] == "investigating"
    assert audit[0]["new_status"] == "resolved"
    assert audit[1]["previous_status"] == "new"
    assert all(a["actor"] == "token-authenticated" for a in audit)
    assert Store(store.url).audit_history(event.event_id) == audit

def test_processing_latency_includes_initial_sql_commit(store):
    import time
    class SlowStore:
        def exists(self, key):
            return store.exists(key)
        def save(self, *args):
            time.sleep(.015)
            return store.save(*args)
        def record_processing_latency(self, *args):
            return store.record_processing_latency(*args)
    assert ingest(generate_event(1, seed=999), SlowStore(), OnlineDetector())[0]
    assert store.list_events()[0]["processing_ms"] >= 14
