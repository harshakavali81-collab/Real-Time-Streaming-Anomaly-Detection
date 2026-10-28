# Production deployment blueprint (not deployed)

The repository has a verified ephemeral Docker integration test, but **no public production cloud backend**. The working Compose file is intentionally bound to localhost. This blueprint distinguishes source readiness from operational authorization.

## Phased path

### Phase 1 — local demonstration (supported)

- Docker Desktop/Engine with Compose, all services on one computer.
- Synthetic producer events only.
- Redpanda single broker, PostgreSQL single database, FastAPI/React localhost.
- Prometheus local alert rules, optional Grafana.
- Unit, end-to-end and Docker integration CI.

### Phase 2 — staging (requires infrastructure)

- Dedicated private VPC/network, private broker (multi-node), managed PostgreSQL.
- Credential vault and rotation, authenticated Kafka transport, ACLs and network policies.
- Container image registry, immutable digests, infrastructure-as-code and migrations.
- Restricted staging domain with HTTPS, OIDC user identity, role-based API permissions.
- Backups, retention, tracing, alert routing to approved operators.

### Phase 3 — independently validated production (requires organization)

- Authorized and governed real telemetry agreements and purpose limitation.
- Time-series seasonality, drift, backpressure and production risk-model evaluation.
- Partition-coordinated persistent model state, recovery after rebalances and worker scale.
- Service SLOs measured at agreed traffic levels, latency percentiles, data retention.
- Disaster-recovery exercises, load/chaos tests, security reviews and operational approval.

## Release acceptance gates

| Gate | Current status |
|---|---|
| Source present in public GitHub repo | Implemented |
| Python and frontend CI | Verified on successful runs |
| Kafka → SQL → API integration smoke | Verified on GitHub Actions synthetic stack |
| Private staging environment | Not deployed |
| Production auth/identity and managed secrets | Not implemented |
| Real-source governance and model quality sign-off | Not available |
| Sustained streaming SLO and DR test | Not performed |
| Public HTTPS/backend and alert delivery | Not deployed |

## What a public static portfolio page proves

GitHub Pages can publish a static synthetic illustration and documentation. It cannot itself run a Kafka cluster, Python consumer, persistent PostgreSQL database or protected operational monitoring backend. Treat the browser preview as a separate educational experience.
