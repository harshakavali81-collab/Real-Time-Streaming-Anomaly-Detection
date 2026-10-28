# StreamWatch AI — Operations and observability

This project demonstrates operational controls against synthetic telemetry in a single-node local environment.

## Start the stack and verify Kafka

~~~bash
docker compose up --build -d
docker compose ps
~~~

To execute the broker/worker/SQL/API smoke manually, configure the **same non-empty API_TOKEN** for both the Compose API service and the CLI environment before running:

~~~bash
python -m scripts.smoke
~~~

The [GitHub integration workflow](../.github/workflows/streaming-integration.yml) does this in CI and checks actual Redpanda deliveries, idempotent database writes, a dead-letter case and authenticated investigation audit. No live business telemetry is used.

## Grafana and Prometheus

~~~bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build -d
~~~

Open http://localhost:3000 for the optional Grafana dashboard; Prometheus is http://localhost:9090, and its rule evaluations can be inspected under /alerts. Grafana is a local-only anonymous-viewer demo with a development password and must not be exposed to the Internet. Panels chart persisted event rate, anomalies, worker latency, invalid events and worker health.

The shipped Prometheus rule groups check worker absence/unavailability and rising invalid-message counts. **No Alertmanager receiver, email, pager, or real-world incident notification exists.**

## Model recovery after restarts

The online model restores service-specific Welford statistics from already persisted scoring outcomes. Only non-anomalous records update the normal feature baseline, while all valid historical records increment observation count. Previously seen Kafka IDs do not relearn samples.

This uses a SQL replay proportional to stored history and a **single-worker assumption**. Horizontal scale requires durable partition-owned model checkpoints, atomic message+state handling and compatible model version migrations.

## DLQ minimization

The consumer stores schema-invalid field paths, offset, partition, source topic, byte count and payload SHA-256. It no longer saves raw rejected event contents. The digest may still reveal low-entropy inputs to an adversary. Authentication and broker retention remain necessary before external use.

## Retention — preview before deletion

~~~bash
python -m scripts.retention --days 30
python -m scripts.retention --days 30 --execute
~~~

The default is dry-run. Execute deletes old SQL event rows **and the associated investigation audit history**. Organizations may require records to be preserved by legal retention rules: back them up before deletion. Within Docker, use docker compose exec consumer python -m scripts.retention --days 30, adding --execute only intentionally.

## Authorization and readiness

- GET /api/ready tests a SQL SELECT 1 before returning success.
- APP_ENV=production without API_TOKEN rejects startup.
- PATCH /api/events/{event_id}/status requires bearer authorization when configured.
- GET /api/events/{event_id}/history returns timestamped review transitions.
- Audit actor labels indicate only token classification, **not a validated human identity**.

The current API GET routes are not behind a complete tenant identity system. A real multi-user service must add identity, TLS, authentication for all sensitive endpoints, strict roles, backup policy, rate limiting, data ownership and audited access.

## Remaining release requirements

Independent sustained streaming load tests, real source permissions, public cloud hosting, HTTPS, Kafka ACLs, distributed state, production-grade observability, domain validation of model predictions, incident drills and documented human operations have not been completed.

The integration workflow additionally verifies Prometheus rule loading and Grafana dashboard provisioning through a black-box check. See [observability verification](OBSERVABILITY_VERIFICATION.md).
