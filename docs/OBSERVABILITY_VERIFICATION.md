# Prometheus and Grafana observability smoke

The optional Grafana overlay is tested in the dedicated docker-streaming-integration GitHub Actions workflow after Kafka ingestion and DLQ behavior have passed.

## Checks performed

1. The Prometheus REST endpoint responds successfully.
2. The configured streamwatch-local-alerts rule group is loaded.
3. Grafana responds with healthy database status.
4. Provisioning has created a searchable StreamWatch dashboard.

## Local reproduction

~~~bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build -d
python -m scripts.observability_smoke
~~~

Expected: a JSON PASS result printed after rules and dashboard become queryable.

The overlay uses a local-only demo password and anonymous viewer permissions. **Never expose it to the public Internet.**

CI rule-provisioning success does not prove on-call notifications, live SLA monitoring, distributed tracing, Grafana dashboards on real external data, or production security.

## Verified CI result

[Docker integration run #40657460536](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/actions/runs/40657460536) completed successfully on 28 October 2026, returning PASS with Prometheus rule group loaded, Grafana database OK and a discoverable StreamWatch AI dashboard. This was an ephemeral local synthetic Docker environment, not a publicly hosted monitoring deployment.
