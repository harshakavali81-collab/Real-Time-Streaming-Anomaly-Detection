"""Monitoring API: validated read endpoints, durable triage audit and fail-closed production config."""
import hmac
import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.sinks.store import Store

ALLOWED_STATUSES = {"new", "investigating", "resolved", "dismissed"}
ALLOWED_SERVICES = {"checkout", "payments", "search", "identity"}

class StatusUpdate(BaseModel):
    status: str

def authorize(authorization: str | None = Header(default=None)) -> str:
    expected = os.getenv("API_TOKEN", "")
    if not expected:
        if os.getenv("APP_ENV", "development") == "production":
            raise HTTPException(status_code=503, detail="Production authentication not configured")
        return "local-demo"
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Bearer token required")
    return "token-authenticated"

def create_app(store: Store | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if os.getenv("APP_ENV", "development") == "production" and not os.getenv("API_TOKEN"):
            raise RuntimeError("API_TOKEN must be configured for production mode")
        app.state.store = store if store is not None else Store()
        yield

    app = FastAPI(title="StreamWatch AI", version="1.1.0",
                  description="Local-first monitoring API for synthetic event pipelines",
                  lifespan=lifespan)
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "PATCH"],
                           allow_headers=["Authorization", "Content-Type"])
    def db() -> Store:
        return app.state.store

    @app.get("/api/health")
    def health():
        return {"status": "ok", "mode": "local-prototype",
                "data_source": "configured database"}

    @app.get("/api/ready")
    def readiness(connection: Store = Depends(db)):
        try:
            from sqlalchemy import text
            with connection.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            raise HTTPException(status_code=503, detail="Database unavailable")
        return {"status": "ready", "database": "reachable"}

    @app.get("/api/summary")
    def summary(minutes: int = Query(60, ge=1, le=1440),
                connection: Store = Depends(db)):
        return connection.summary(minutes)

    @app.get("/api/events")
    def events(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0, le=100000),
               anomalies_only: bool = False, status: str | None = None,
               service: str | None = None, connection: Store = Depends(db)):
        if status and status not in ALLOWED_STATUSES:
            raise HTTPException(422, detail="Unknown status")
        if service and service not in ALLOWED_SERVICES:
            raise HTTPException(422, detail="Unknown service")
        return {"items": connection.list_events(limit, anomalies_only, status, service, offset),
                "offset": offset, "limit": limit}

    @app.get("/api/trends")
    def trends(minutes: int = Query(60, ge=1, le=1440),
               connection: Store = Depends(db)):
        return {"items": connection.trends(minutes)}

    @app.get("/api/events/{event_id}/history")
    def history(event_id: str, connection: Store = Depends(db)):
        return {"items": connection.audit_history(event_id)}

    @app.patch("/api/events/{event_id}/status")
    def update_status(event_id: str, item: StatusUpdate, actor: str = Depends(authorize),
                      connection: Store = Depends(db)):
        if item.status not in ALLOWED_STATUSES:
            raise HTTPException(422, detail="Invalid status")
        record = connection.update_status(event_id, item.status, actor)
        if record is None:
            raise HTTPException(404, detail="Anomalous event not found")
        return record

    return app

app = create_app()
