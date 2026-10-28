# GitHub Actions validation evidence — 28 October 2026

**Workflow:** [quality-and-build successful run #40655375232](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/actions/runs/40655375232)

**Verified revision:** ace4b2117103674c6af6c4ea267d786fb38c42ac

This evidence describes the completed CI job above. It is not a claim of live production deployment or that every later commit has the same result.

## Automated checks

| Validation | Actual GitHub Actions result |
|---|---|
| Python pytest | **21 passed**, 9 non-failing dependency/deprecation warnings |
| Offline generated event → detector → SQL demonstration | Passed with 240 simulated events |
| Single-process Python/SQLite benchmark script | Completed |
| Docker Compose YAML/config validation | Passed |
| React/Vite npm build | Passed |

## Measured *offline* benchmark

GitHub Actions executed: python -m scripts.benchmark --events 250

| Field | Logged value | Interpretation |
|---|---:|---|
| Observations | 250 | Seeded *synthetic* simulator events |
| Wall time | 0.2116 s | End-to-end local loop elapsed time |
| Average processing throughput | **1181.41 events/s** | One runner, Python + in-memory SQLite; **not Kafka throughput** |
| Flagged observations | 14 | Model decisions on 250 generated events |
| Synthetic precision | **1.0000** | Of detected simulated anomalies, all 14 were labelled anomalous |
| Synthetic recall | **0.5000** | 14 true anomalies detected out of 28 simulated anomalies |
| True positive / false positive / false negative | 14 / 0 / 14 | Simulator label comparison |
| Reported p95 processing_ms | 0.02 ms | Code-side scoring-time sample captured **before the SQL write**; not p95 full pipeline latency |

**Important scope note:** The benchmark intentionally bypasses Kafka, networking, Postgres, browser render and concurrent workers. The reported throughput is a small-sample CI machine observation, NOT a production SLO, peak throughput, Kafka processing speed or validated general performance. Runner speed, sampling, instrument location and data distribution affect all figures. This is an illustrative evaluation of a synthetic distribution, not independent field model validation.

## Further verification required

To publish full-stream metrics, run the complete Docker Compose stack with a pinned producer load and capture: broker ingress and consumer lag, persisted row counts, end-to-end p50/p95/p99 on clock-synchronized hosts, malformed-record DLQ counts, restart replay outcomes and real deployed monitoring logs. Rerun on independent seeds, drift patterns and authorized real-world labels before evaluating operational detection.

Source references: [benchmark code](../scripts/benchmark.py), [tests](../tests), [evaluation methodology](EVALUATION.md), [model card](MODEL_CARD.md).
