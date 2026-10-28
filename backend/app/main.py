"""Read-only monitoring endpoints and an optionally authenticated triage mutation."""
import os
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.sinks.store import Store

ALLOWED_STATUSES = {"new", "investigating", "resolved", "dismissed"}

class StatusUpdate(BaseModel):
    status: str

def authorize(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("API_TOKEN", "")
    if expected and authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Bearer token required")

def create_app(store: Store | None = None) -> FastAPI:
    app = FastAPI(title="StreamWatch AI", version="1.0.0",
                  description="Local-first monitoring API for synthetic event pipelines")
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "PATCH"],
                           allow_headers=["Authorization", "Content-Type"])
    @app.on_event("startup")
    def open_store():
        app.state.store = store or Store()
    def db() -> Store:
        return app.state.store
    @app.get("/api/health")
    def health():
        return {"status": "ok", "mode": "synthetic-demo", "data_source": "configured database"}
    @app.get("/api/summary")
    def summary(minutes: int = Query(60, ge=1, le=1440), connection: Store = Depends(db)):
        return connection.summary(minutes)
    @app.get("/api/events")
    def events(limit: int = Query(100, ge=1, le=500), anomalies_only: bool = False,
               status: str | None = None, connection: Store = Depends(db)):
        if status and status not in ALLOWED_STATUSES:
            raise HTTPException(422, detail="Unknown status")
        return {"items": connection.list_events(limit, anomalies_only, status)}
    @app.get("/api/trends")
    def trends(minutes: int = Query(60, ge=1, le=1440), connection: Store = Depends(db)):
        return {"items": connection.trends(minutes)}
    @app.patch("/api/events/{event_id}/status", dependencies=[Depends(authorize)])
    def update_status(event_id: str, item: StatusUpdate, connection: Store = Depends(db)):
        if item.status not in ALLOWED_STATUSES:
            raise HTTPException(422, detail="Invalid status")
        record = connection.update_status(event_id, item.status)
        if record is None:
            raise HTTPException(404, detail="Anomalous event not found")
        return record
    return app

app = create_app()
