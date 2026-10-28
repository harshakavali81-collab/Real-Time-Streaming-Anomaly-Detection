"""Investigation severity is a triage heuristic, not an incident diagnosis."""
def severity(score: float, anomaly: bool) -> str:
    if not anomaly:
        return "normal"
    return "critical" if score >= 5.5 else "high" if score >= 4.3 else "medium"
