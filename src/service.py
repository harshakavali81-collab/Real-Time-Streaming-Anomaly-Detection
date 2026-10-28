"""Shared ingestion route for Kafka workers and repeatable offline demos."""
from time import perf_counter
from src.models.detector import OnlineDetector
from src.schema import TelemetryEvent
from src.sinks.store import Store

def ingest(event: TelemetryEvent, store: Store, detector: OnlineDetector) -> tuple[bool, bool]:
    if store.exists(event.event_id):
        return False, False
    begin = perf_counter()
    prediction = detector.score(event)
    saved = store.save(event, prediction)
    if saved:
        # Includes scoring and the first database commit; excludes timing update.
        store.record_processing_latency(event.event_id, (perf_counter() - begin) * 1000)
    return saved, prediction.anomaly if saved else False
