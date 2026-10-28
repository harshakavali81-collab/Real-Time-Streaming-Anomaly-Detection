from fastapi.testclient import TestClient
from producer.simulator import generate_event
from src.models.detector import Detection
from backend.app.main import create_app

def test_health_and_summary(store):
    with TestClient(create_app(store)) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/summary").json()["events"] == 0
        assert client.get("/api/trends").json()["items"] == []

def test_event_list_and_triage(store, monkeypatch):
    monkeypatch.setenv("API_TOKEN", "test-secret")
    e = generate_event(0)
    store.save(e, Detection(5.9, True, "latency deviation"))
    with TestClient(create_app(store)) as client:
        assert len(client.get("/api/events?anomalies_only=true").json()["items"]) == 1
        path = "/api/events/" + e.event_id + "/status"
        assert client.patch(path, json={"status": "resolved"}).status_code == 401
        assert client.patch(path, json={"status": "invalid"},
                            headers={"Authorization": "Bearer test-secret"}).status_code == 422
        response = client.patch(path, json={"status": "resolved"},
                                headers={"Authorization": "Bearer test-secret"})
        assert response.status_code == 200
        assert response.json()["status"] == "resolved"

def test_filters_reject_out_of_range(store):
    with TestClient(create_app(store)) as client:
        assert client.get("/api/events?limit=999999").status_code == 422
        assert client.get("/api/summary?minutes=0").status_code == 422
