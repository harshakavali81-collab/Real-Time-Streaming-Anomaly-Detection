# Local runbook

## Boot

~~~bash
docker compose up --build -d
docker compose ps
curl http://localhost:8000/api/health
curl http://localhost:8000/api/summary
~~~

Open dashboard at http://localhost:8080. It shows connected SQL-backed values when Docker services are running and an explicitly labelled separate browser-only synthetic preview on request.

## Troubleshooting

- No events: docker compose logs --tail=80 producer consumer, verify Kafka topic and connection.
- API unavailable: docker compose logs api postgres; inspect SQL connection and port 8000.
- No alerts: wait for warmup of 25 events per service; anomalies are probabilistic.
- Metrics missing: open Prometheus targets and inspect consumer:9100 inside Compose network.
- Triage returns 401: supply bearer token if API_TOKEN is configured.
- Worker crashes: inspect logs, correct schema/DB issues; uncommitted source offset can replay.

## Benchmark and quality

~~~bash
python -m pytest -q
python -m scripts.benchmark --events 1000
python -m src.demo --events 1000 --db sqlite:///./streamwatch.db
~~~

The benchmark is single-process in-memory SQLite, **not** Kafka throughput. For real stream measurements record hardware, event rate, broker lag, DB inserts, run duration, repeated trials, percentile timing and data integrity.

## Safe shutdown

docker compose down keeps volumes. docker compose down -v destroys *all local broker and SQL demo state*. Never use destructive commands on a production environment.


## New operational workflows

[Operations guide](OPERATIONS.md) documents the actual Docker integration smoke, redacted dead-letter records, startup model-state restore, Grafana observability and retention. Example on a local workstation with the API_TOKEN configured in both Compose and the shell:

~~~bash
python -m scripts.smoke
python -m scripts.retention --days 30
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build -d
~~~

The default Python quality workflow verifies unit and offline checks; the separate integration workflow runs the broker, SQL database and API as containers. See [successful integration run](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/actions/runs/40656391915).
