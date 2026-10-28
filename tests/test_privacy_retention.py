"""DLQ data minimization, safe retention and audit referential behavior."""
from hashlib import sha256
from time import time
from sqlalchemy import update
from producer.simulator import generate_event
from src.models.detector import Detection
from src.alerts.dlq import quarantine_record
from src.sinks.store import EventRow

def test_dlq_never_contains_raw_personal_data():
    private = b'{"email":"hidden@example.com","password":"sensitive"}'
    class Message:
        def topic(self): return "telemetry.events.v1"
        def partition(self): return 0
        def offset(self): return 88
        def value(self): return private
    record = quarantine_record(Message(), ValueError("hidden@example.com"))
    assert record["payload_sha256"] == sha256(private).hexdigest()
    assert record["payload_size_bytes"] == len(private)
    assert "hidden@example.com" not in str(record)
    assert "password" not in str(record)
    assert "payload" not in record

def test_retention_dry_run_and_associated_audit(store):
    stale, fresh = generate_event(1, seed=99), generate_event(2, seed=99)
    store.save(stale, Detection(6,True,"spike"))
    store.save(fresh, Detection(6,True,"spike"))
    store.update_status(stale.event_id,"investigating")
    store.update_status(fresh.event_id,"resolved")
    with store.Session.begin() as s:
        s.execute(update(EventRow).where(EventRow.event_id == stale.event_id)
                  .values(stored_ts=time()-70*86400))
    cutoff=time()-30*86400
    assert store.prune_before(cutoff) == {"dry_run":True,"matching_events":1,"matching_audit_records":1}
    assert store.exists(stale.event_id)
    store.prune_before(cutoff,execute=True)
    assert not store.exists(stale.event_id)
    assert store.exists(fresh.event_id)
    assert store.audit_history(stale.event_id)==[]
    assert len(store.audit_history(fresh.event_id))==1
