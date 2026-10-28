# Threat model — synthetic event streaming prototype

**Scope:** local single-node Kafka-compatible broker, producer, Python worker, PostgreSQL, FastAPI, optional Grafana and React dashboard. This analysis is educational, not an external penetration test or security certification.

| Boundary | Threat | Existing mitigation | Required for deployment |
|---|---|---|---|
| Producer → Kafka | Spoofed events, flooding, malicious payloads | Strict JSON schema, capped numeric ranges, keyed events, synthetic generator | mTLS/SASL, ACLs, client quotas, schema registry |
| Kafka → worker | Malformed events crash worker | Dedicated DLQ metadata, manual commit after successful delivery | Robust retry/backoff, poison-message quotas, DLQ access logging |
| Worker → model | Poisoned baselines, drift and hidden false negatives | Warmup, per-service z-score, skip flagged values, synthetic evaluation | Trusted source authentication, drift tests, labelled validation, model registry |
| Worker → SQL | Duplicate replay or inconsistent state | Unique event ID, SQL transaction, model restoration from persisted decisions | Coordinated partitions, checkpointed model state, HA database, migrations |
| API → browser | Unauthorized triage changes | Optional development bearer token, required production token, constrained statuses | OIDC authentication, RBAC, CSRF review, TLS, rate limits and per-actor audits |
| Browser → CSV | Sensitive data exported | No real data in current simulator | Restrict access, redaction policy, data minimization |
| Invalid DLQ | PII leaks to error logs | No raw payload or exception text; only hash, paths, length and routing | No low-entropy hashes for actual confidential payloads, encrypted retention |
| Docker/Grafana | Default/demo credentials exposed | Host ports bound to 127.0.0.1 | Reverse proxy, TLS, secret manager, hardened admin/anonymous access disabled |
| Prometheus | False sense of monitoring | Local worker and alert-rule indicators | Alertmanager delivery, response ownership, incident drills |
| Build chain | Vulnerable/pulled dependencies | Pinned image tags, GitHub CI, Dependabot | Image digest pinning, SBOM, dependency audit, image scans, release signing |

## Priority order for production readiness

1. Restrict ingress to authenticated sources (Kafka SASL/mTLS and scoped ACLs).
2. Add authenticated and authorized users for all sensitive API routes; secure cookies/headers, HTTPS, rate limits.
3. Replace demo passwords and anonymous Grafana; store secrets in a managed service.
4. Add migrations, encrypted backups, tested restore procedures and data retention contracts.
5. Add durable partition-keyed ML state, rebalance-safe commit semantics, multi-worker correctness and replay tests.
6. Use a vetted, labelled operational dataset; establish alert-quality and drift measurements.
7. Add structured log redaction, tracing, distributed monitors, alert escalation and an incident response process.
8. Conduct sustained load, chaos, penetration and independent operational reviews.

No item here is represented as deployed merely because a corresponding plan exists.
