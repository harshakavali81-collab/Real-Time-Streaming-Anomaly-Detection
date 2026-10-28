# 12-minute engineering demonstration checklist

All data is fictional; values below are suggested actions rather than benchmark results.

1. Open the GitHub README and show the 10 original SVG architecture/flow assets.
2. Explain service data contract and why error-rate fields have strict ranges.
3. Run Python tests and point to the current GitHub Actions run.
4. Start local Docker Compose and show API readiness.
5. Watch synthetic events arrive in the React dashboard.
6. Filter four services; inspect per-service z-score alerts after warmup.
7. Demonstrate human investigation state and audit history API.
8. Inject a schema-invalid message and inspect privacy-conscious DLQ metadata.
9. Replay one event ID and verify only one SQL row persists.
10. Restart the worker and explain restoration of previously persisted model decisions.
11. Open Prometheus; optionally start Grafana with the separate Compose overlay.
12. Compare offline Python throughput, Kafka producer acknowledgements and true full-stack measurement limits.

## Interview explanation

I created an event pipeline with a Kafka-compatible broker, schema validation, SQL deduplication, online per-service anomaly scoring, monitoring and human investigation. The integration test verifies real message transfer through containers. I can also explain what is *not* solved: distributed model-state consistency, long-running load performance, real incident labels, operational identity and production infrastructure.

## Recordings and screenshots

When producing recruiter videos/screenshots, overlay the words SYNTHETIC LOCAL DEMO. Avoid showing secrets, raw payloads or personal data. Present only measurements from the recorded environment and link to logs or dated evidence.
