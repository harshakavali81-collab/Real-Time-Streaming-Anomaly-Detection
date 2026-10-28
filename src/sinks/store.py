"""Idempotent SQL sink with investigation state and rolling monitoring queries."""
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy import Boolean, Float, Index, Integer, JSON, String, create_engine, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from src.schema import TelemetryEvent
from src.models.detector import Detection
from src.alerts.rules import severity

class Base(DeclarativeBase):
    pass

class EventRow(Base):
    __tablename__ = "events"
    event_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    service: Mapped[str] = mapped_column(String(32), nullable=False)
    event_ts: Mapped[float] = mapped_column(Float, nullable=False)
    stored_ts: Mapped[float] = mapped_column(Float, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    anomaly: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    reason: Mapped[str] = mapped_column(String(150), nullable=False)
    model: Mapped[str] = mapped_column(String(48), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    ground_truth: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    processing_ms: Mapped[float] = mapped_column(Float, nullable=False)
    e2e_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)

Index("ix_events_stored_ts", EventRow.stored_ts)
Index("ix_events_triage", EventRow.anomaly, EventRow.status, EventRow.stored_ts)

def public_row(row: EventRow) -> dict:
    return {
        "event_id": row.event_id, "service": row.service,
        "timestamp": datetime.fromtimestamp(row.event_ts, timezone.utc).isoformat(),
        "score": row.score, "anomaly": row.anomaly, "severity": row.severity,
        "reason": row.reason, "model": row.model, "status": row.status,
        "features": row.features, "source": row.source,
        "processing_ms": row.processing_ms, "e2e_latency_ms": row.e2e_latency_ms,
        "ground_truth": row.ground_truth
    }

class Store:
    def __init__(self, url: str | None = None):
        self.url = url or os.getenv("DATABASE_URL", "sqlite:///./streamwatch.db")
        params = {"connect_args": {"check_same_thread": False}} if self.url.startswith("sqlite") else {}
        self.engine = create_engine(self.url, pool_pre_ping=True, **params)
        self.Session = sessionmaker(self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    def exists(self, event_id: str) -> bool:
        with self.Session() as session:
            return session.get(EventRow, event_id) is not None

    def save(self, event: TelemetryEvent, detection: Detection, processing_ms: float = 0) -> bool:
        now = time.time()
        with self.Session.begin() as session:
            if session.get(EventRow, event.event_id):
                return False
            row = EventRow(
                event_id=event.event_id, service=event.service,
                event_ts=event.timestamp.timestamp(), stored_ts=now,
                score=detection.score, anomaly=detection.anomaly,
                severity=severity(detection.score, detection.anomaly),
                reason=detection.reason, model=detection.model,
                status="new", features={"latency_ms": event.latency_ms,
                                        "cpu_pct": event.cpu_pct, "error_rate": event.error_rate,
                                        "rps": event.rps},
                ground_truth=event.ground_truth, source=event.source,
                processing_ms=processing_ms, e2e_latency_ms=max(0, (now-event.timestamp.timestamp())*1000)
            )
            session.add(row)
        return True

    def list_events(self, limit: int = 100, anomaly_only: bool = False, status: str | None = None) -> list[dict]:
        statement = select(EventRow)
        if anomaly_only:
            statement = statement.where(EventRow.anomaly.is_(True))
        if status:
            statement = statement.where(EventRow.status == status)
        statement = statement.order_by(EventRow.stored_ts.desc()).limit(limit)
        with self.Session() as session:
            return [public_row(row) for row in session.scalars(statement)]

    def update_status(self, event_id: str, status: str) -> dict | None:
        with self.Session.begin() as session:
            row = session.get(EventRow, event_id)
            if row is None or not row.anomaly:
                return None
            row.status = status
            session.flush()
            result = public_row(row)
        return result

    def summary(self, window_minutes: int = 60) -> dict:
        since = time.time() - window_minutes * 60
        with self.Session() as session:
            rows = list(session.scalars(select(EventRow).where(EventRow.stored_ts >= since)))
        anomalies = [r for r in rows if r.anomaly]
        pending = sum(r.status in ("new", "investigating") for r in anomalies)
        lat = sorted(r.e2e_latency_ms for r in rows)
        proc = sorted(r.processing_ms for r in rows)
        def pct(data: list[float], quantile: float) -> float | None:
            if not data:
                return None
            return round(data[min(len(data)-1, int((len(data)-1)*quantile))], 2)
        labelled = [r for r in rows if r.ground_truth is not None and r.source == "simulator"]
        tp = sum(r.anomaly and r.ground_truth for r in labelled)
        fp = sum(r.anomaly and not r.ground_truth for r in labelled)
        fn = sum((not r.anomaly) and r.ground_truth for r in labelled)
        return {"window_minutes": window_minutes, "events": len(rows), "anomalies": len(anomalies),
                "pending": pending, "rate_per_minute": round(len(rows)/window_minutes, 2),
                "anomaly_rate": round(len(anomalies)/len(rows), 4) if rows else 0,
                "p50_e2e_ms": pct(lat, .5), "p95_e2e_ms": pct(lat, .95),
                "p95_processing_ms": pct(proc, .95),
                "evaluation": {"dataset": "simulator labels only", "labelled": len(labelled),
                               "precision": round(tp/(tp+fp), 4) if tp+fp else None,
                               "recall": round(tp/(tp+fn), 4) if tp+fn else None,
                               "tp": tp, "fp": fp, "fn": fn}}

    def trends(self, window_minutes: int = 60) -> list[dict]:
        since = time.time() - window_minutes * 60
        with self.Session() as session:
            rows = session.scalars(select(EventRow).where(EventRow.stored_ts >= since).order_by(EventRow.stored_ts.asc()))
            buckets = defaultdict(lambda: {"events": 0, "anomalies": 0, "latencies": [], "scores": []})
            for row in rows:
                key = int(row.stored_ts // 60) * 60
                group = buckets[key]
                group["events"] += 1
                group["anomalies"] += int(row.anomaly)
                group["latencies"].append(row.e2e_latency_ms)
                group["scores"].append(row.score)
        return [{"minute": datetime.fromtimestamp(key, timezone.utc).isoformat(),
                 "events": value["events"], "anomalies": value["anomalies"],
                 "avg_score": round(sum(value["scores"])/len(value["scores"]), 2),
                 "avg_latency_ms": round(sum(value["latencies"])/len(value["latencies"]), 2)}
                for key, value in sorted(buckets.items())]
