# Metrics and reproducible evaluation

| Metric | Definition | Scope |
|---|---|---|
| Stored events | SQL records within a rolling time window | Database, not Kafka ingress |
| Throughput | stored rows / selected minutes | Rolling average, not peak |
| P50/P95 end-to-end | event timestamp → DB insert | Subject to clock skew, queuing |
| P95 processing | scoring + SQL call wall time | Worker, not broker network |
| Precision / recall | TP/(TP+FP), TP/(TP+FN) | Simulator-labelled rows ONLY |
| Flag rate | flagged / stored | Distribution-dependent |
| Kafka consumer lag | per-partition unconsumed offset gap | Must be measured at broker |
| Prometheus worker metrics | counters, histogram, availability gauge | Process-local, resets on restart |

## Reproduction plan

1. Run automated tests and capture their actual outcome.
2. Record hardware, Python/Node versions and event injection settings.
3. Run the offline benchmark at several sample sizes and repeat runs.
4. Run Compose with controlled synthetic producer settings; measure broker lag, SQL row counts and timestamps.
5. Inject invalid events to verify DLQ routing; restart worker and check replay and baselines.
6. Report actual observed precision/recall and prevalence; vary seed, threshold and drift.
7. Publish documented dates and limitations alongside numeric measurements.

![Illustrative anomaly scores](assets/06-anomaly-score-timeline.svg)

![Illustrative event counts](assets/07-event-throughput.svg)

Charts above are **visual examples**, not numbers observed in a verified live Kafka run.
