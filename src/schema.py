"""Strict versioned event contract for producers and consumers."""
from datetime import datetime
from math import isfinite
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    event_id: str = Field(min_length=8, max_length=80, pattern=r"^[a-zA-Z0-9-]+$")
    service: Literal["checkout", "payments", "search", "identity"]
    timestamp: datetime
    latency_ms: float = Field(ge=0, le=120000)
    cpu_pct: float = Field(ge=0, le=100)
    error_rate: float = Field(ge=0, le=1)
    rps: float = Field(ge=0, le=100000)
    ground_truth: bool | None = None
    source: Literal["simulator", "external"] = "simulator"

    @field_validator("timestamp")
    @classmethod
    def validate_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value

    @field_validator("latency_ms", "cpu_pct", "error_rate", "rps")
    @classmethod
    def validate_finite(cls, value: float) -> float:
        if not isfinite(value):
            raise ValueError("non-finite values are prohibited")
        return value
