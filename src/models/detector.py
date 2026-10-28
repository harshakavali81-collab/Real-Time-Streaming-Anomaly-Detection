"""Per-service online anomaly detector with warmup and outlier-resistant updates."""
from dataclasses import dataclass, field
from math import sqrt
from src.schema import TelemetryEvent
from src.features.transform import to_vector

@dataclass
class RunningStat:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def observe(self, value: float) -> None:
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        self.m2 += delta * (value - self.mean)

    def z(self, value: float) -> float:
        if self.count < 2:
            return 0.0
        variance = self.m2 / (self.count - 1)
        # Floors prevent normal near-constant signals from being oversensitive.
        return abs(value - self.mean) / max(sqrt(variance), 0.04)

@dataclass
class ServiceProfile:
    stats: list[RunningStat] = field(default_factory=lambda: [RunningStat() for _ in range(4)])
    observed: int = 0

@dataclass(frozen=True)
class Detection:
    score: float
    anomaly: bool
    reason: str
    model: str = "online-zscore-v1"

class OnlineDetector:
    def __init__(self, warmup: int = 25, threshold: float = 3.6):
        if warmup < 2 or threshold <= 0:
            raise ValueError("warmup must be >=2 and threshold positive")
        self.warmup = warmup
        self.threshold = threshold
        self.profiles: dict[str, ServiceProfile] = {}

    def restore_observation(self, service: str, values: list[float], anomaly: bool) -> None:
        """Rehydrate a previously persisted decision without scoring it again.

        The DB is authoritative; rejected/duplicate messages never become training rows.
        Single consumer worker per service is required for consistent state.
        """
        profile = self.profiles.setdefault(service, ServiceProfile())
        if len(values) != 4:
            raise ValueError("expected four versioned features")
        if not anomaly:
            for stat, value in zip(profile.stats, values):
                stat.observe(value)
        profile.observed += 1

    def score(self, event: TelemetryEvent) -> Detection:
        profile = self.profiles.setdefault(event.service, ServiceProfile())
        values = to_vector(event)
        zscores = [stat.z(value) for stat, value in zip(profile.stats, values)]
        # Maximum deviation makes the reason interpretable to investigators.
        score = max(zscores) if profile.observed >= self.warmup else 0.0
        flag = score >= self.threshold
        names = ("latency", "cpu", "errors", "requests")
        reason = (f"{names[zscores.index(max(zscores))]} deviation" if flag else
                  ("learning baseline" if profile.observed < self.warmup else "within baseline"))
        # Skip flagged samples to reduce poisoning; this is still only a statistical baseline.
        if not flag:
            for stat, value in zip(profile.stats, values):
                stat.observe(value)
        profile.observed += 1
        return Detection(round(score, 4), flag, reason)
