"""Quarantine schema-error metadata without retaining raw source payloads."""
from hashlib import sha256
from datetime import datetime, timezone
from pydantic import ValidationError

def quarantine_record(message, error: Exception) -> dict:
    raw = message.value() or b""
    fields = []
    if isinstance(error, ValidationError):
        for item in error.errors():
            fields.append(".".join(str(x) for x in item["loc"])[:120])
    return {"schema_version": 1, "source_topic": message.topic(),
            "partition": message.partition(), "offset": message.offset(),
            "error_type": "invalid_schema", "invalid_fields": fields[:15],
            "payload_size_bytes": len(raw), "payload_sha256": sha256(raw).hexdigest(),
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "note": "Original payload intentionally omitted to avoid sensitive value exposure"}
