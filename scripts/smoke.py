"""Black-box local Kafka/Redpanda/SQL/API/DLQ integration verification."""
import json
import os
import sys
import time
import uuid
from urllib.request import Request, urlopen
from confluent_kafka import Consumer, Producer
from producer.simulator import generate_event

API = os.getenv("SMOKE_API_URL", "http://localhost:8000")
BROKER = os.getenv("SMOKE_BROKER", "localhost:19092")
TOKEN = os.getenv("API_TOKEN", "")
if not TOKEN:
    raise RuntimeError("Configure API_TOKEN in Docker stack and smoke environment")

def request(path, method="GET", body=None, auth=False):
    headers = {"Content-Type":"application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + TOKEN
    req = Request(API+path, data=json.dumps(body).encode() if body is not None else None,
                  method=method, headers=headers)
    with urlopen(req, timeout=8) as response:
        return json.load(response)

def wait_until(fn, timeout=160, label="condition"):
    limit = time.monotonic() + timeout
    error = None
    while time.monotonic() < limit:
        try:
            result = fn()
            if result:
                return result
        except Exception as exc:
            error = exc
        time.sleep(1.0)
    raise AssertionError(f"Timeout waiting for {label}; last error={error}")

def main():
    assert wait_until(lambda: request("/api/ready"), label="API readiness")["database"] == "reachable"
    def has_messages():
        data = request("/api/summary")
        return data if data["events"] >= 45 else None
    summary = wait_until(has_messages, label="45 persisted Kafka events")
    print("Kafka → SQL persisted:", summary["events"])
    producer = Producer({"bootstrap.servers": BROKER, "acks":"all"})
    identity = uuid.uuid4().hex
    event = generate_event(600, seed=9999).model_copy(update={"event_id": identity})
    for _ in range(2):
        producer.produce("telemetry.events.v1", value=event.model_dump_json().encode(),
                         key=event.service.encode())
    assert producer.flush(20) == 0
    def inserted():
        rows = request("/api/events?limit=500")["items"]
        return [x for x in rows if x["event_id"] == identity] or None
    found = wait_until(inserted, label="deduplicated producer replay")
    assert len(found) == 1

    dlq = Consumer({"bootstrap.servers":BROKER, "group.id":"smoke-"+uuid.uuid4().hex,
                    "auto.offset.reset":"earliest", "enable.auto.commit":False})
    dlq.subscribe(["telemetry.invalid.v1"])
    try:
        producer.produce("telemetry.events.v1", value=b'{"schema_version":1,"invalid":true}')
        assert producer.flush(20) == 0
        def read_dlq():
            message = dlq.poll(1)
            if message is None or message.error():
                return None
            payload = json.loads(message.value())
            return payload if '"invalid"' in payload.get("payload", "") else None
        entry = wait_until(read_dlq, timeout=75, label="invalid Kafka event DLQ")
        assert entry["source_topic"] == "telemetry.events.v1"
    finally:
        dlq.close()

    def find_alert():
        rows = request("/api/events?anomalies_only=true&limit=200")["items"]
        return rows[0] if rows else None
    alert = wait_until(find_alert, label="anomaly persisted to SQL")
    path = f"/api/events/{alert['event_id']}/status"
    result = request(path, "PATCH", {"status":"investigating"}, auth=True)
    assert result["status"] == "investigating"
    changes = request(f"/api/events/{alert['event_id']}/history")["items"]
    assert any(c["new_status"] == "investigating" for c in changes)
    print(json.dumps({"result":"PASS", "source":"synthetic through actual local Kafka",
                      "events_at_checkpoint":summary["events"],
                      "deduplicated":True,"dlq":True,"authenticated_audit":True}, indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("SMOKE FAIL:", repr(exc), file=sys.stderr)
        raise
