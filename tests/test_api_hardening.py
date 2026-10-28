"""Production auth, readiness and filtering."""
import pytest
from fastapi.testclient import TestClient
from producer.simulator import generate_event
from src.models.detector import Detection
from backend.app.main import create_app

def test_production_must_have_token(monkeypatch, store):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("API_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="API_TOKEN"):
        with TestClient(create_app(store)):
            pass

def test_production_auth_and_audit(monkeypatch, store):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("API_TOKEN", "test-secret")
    event = generate_event(3)
    store.save(event, Detection(5.4, True, "error deviation"))
    with TestClient(create_app(store)) as client:
        url = f"/api/events/{event.event_id}/status"
        assert client.patch(url, json={"status": "investigating"}).status_code == 401
        assert client.patch(url, json={"status": "investigating"},
                            headers={"Authorization":"Bearer wrong"}).status_code == 401
        result = client.patch(url, json={"status": "investigating"},
                              headers={"Authorization":"Bearer test-secret"})
        assert result.status_code == 200
        audit = client.get(f"/api/events/{event.event_id}/history").json()["items"]
        assert audit[0]["actor"] == "token-authenticated"

def test_ready_filters_pagination(store):
    event = generate_event(1)
    store.save(event, Detection(0.0, False, "learning baseline"))
    with TestClient(create_app(store)) as client:
        assert client.get("/api/ready").json()["status"] == "ready"
        assert client.get("/api/events?service=invalid").status_code == 422
        assert client.get("/api/events?offset=-1").status_code == 422
        assert len(client.get("/api/events?service=payments").json()["items"]) == 1
        assert len(client.get("/api/events?service=checkout").json()["items"]) == 0
        assert len(client.get("/api/events?offset=1").json()["items"]) == 0
        assert client.get("/api/events/does-not-exist/history").json()["items"] == []
