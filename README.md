<div align="center">

![StreamWatch AI](docs/assets/01-streamwatch-cover.svg)

# StreamWatch AI
### Real-Time Streaming · Anomaly Detection · Investigation Intelligence

**Redpanda/Kafka → Python Validation & ML → PostgreSQL → FastAPI → React**

[![CI](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/actions/workflows/ci.yml/badge.svg)](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-3773a5)
![Frontend](https://img.shields.io/badge/React-Vite-7298ff)
![License](https://img.shields.io/badge/License-MIT-70ddbd)
![Data](https://img.shields.io/badge/Data-seeded%20synthetic-f2ba78)

[Architecture](docs/ARCHITECTURE.md) · [Visual gallery](docs/VISUAL_GALLERY.md) · [Model card](docs/MODEL_CARD.md) · [Runbook](docs/RUNBOOK.md) · [Portfolio case study](docs/PORTFOLIO_CASE_STUDY.md)

</div>

> **Evidence boundary:** A complete-source educational **prototype** using explicitly simulated events. This is not a publicly deployed production monitoring service. Browser preview graphs are illustrative. No fabricated Kafka throughput, model accuracy or public performance is claimed.

## Problem and solution

Microservices emit latency, CPU, error-rate and request-volume events. Operators need a structured way to identify unusual signals, investigate findings, and measure system behavior. StreamWatch AI demonstrates event publishing, strict validation, at-least-once consumption, online detection, durable SQL persistence, monitoring and human review.

**Designed for:** ML Engineer, Data Engineer, MLOps Engineer, Backend Engineer, Software Engineer.

## Features and implementation

| Layer | Working implementation |
|---|---|
| Event generator | Seeded synthetic telemetry for checkout, payments, search and identity |
| Broker | Kafka-compatible Redpanda via Docker Compose; message keys by service |
| Consumer | Pydantic event validation, invalid payload dead-letter queue, manual offset commits |
| Features | Log latency, CPU ratio, error rate, log RPS |
| Online model | Per-service Welford z-score detector, warmup, outlier-resistant updates, interpretable reasons |
| Optional offline ML | Isolation Forest trained and tested on chronological synthetic data |
| SQL persistence | PostgreSQL or SQLite, unique event IDs, severity, investigation status |
| FastAPI | Rolling metrics, summary, event filters, trends and controlled triage |
| React app | KPI cards, charting, filters, alert review, CSV export and explicit synthetic preview |
| Monitoring | Prometheus worker counters, histogram and consumer-up signal |
| Quality | Unit tests, API tests, offline end-to-end test, Python benchmark and frontend build CI |
| Visuals | Ten original SVG architecture / data / charts / workflow assets |

![Pipeline](docs/assets/02-end-to-end-architecture.svg)

## Full local streaming stack

Requires Docker Desktop / Docker Engine + Compose, and around 4 GB RAM.

~~~bash
git clone https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection.git
cd Real-Time-Streaming-Anomaly-Detection
docker compose up --build -d
docker compose ps
~~~

Open the **React dashboard** at http://localhost:8080, API docs at http://localhost:8000/docs and **Prometheus** at http://localhost:9090. The Kafka external development port is localhost:19092.

~~~bash
docker compose logs -f producer consumer
docker compose down
# Destructive; delete local demo volumes ONLY when intended:
docker compose down -v
~~~

Docker binds development ports to loopback. Development SQL credentials are placeholders. Real cloud deployment requires TLS, authenticated broker access, identity controls, secret management, durable model state and availability engineering.

## Offline end-to-end demo (no Kafka needed)

~~~bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.demo --events 1000 --db sqlite:///./streamwatch.db
uvicorn backend.app.main:app --reload
# A second terminal:
cd frontend
npm install
npm run dev
~~~

Open http://localhost:5173. Vite proxies the API path to :8000. Offline mode exercises simulator → Pydantic → feature engineering → detector → SQL → API, but bypasses the broker and **must not be represented as Kafka load testing**.

## Validate, train and benchmark

~~~bash
python -m pytest -q
python -m src.models.train --samples 4000
python -m scripts.benchmark --events 1000
cd frontend && npm run build
~~~

The benchmark calculates real wall-time observations **on the machine running it** using in-memory SQLite and one Python process. It does not emulate external Kafka network/consumer lag or prove an SLA. Offline Isolation Forest is not deployed in the default consumer; live worker uses the per-service online detector.

## Event contract

~~~json
{
  "schema_version": 1,
  "event_id": "evt-42-100",
  "service": "checkout",
  "timestamp": "2026-10-28T12:00:00+00:00",
  "latency_ms": 180.0,
  "cpu_pct": 42.0,
  "error_rate": 0.01,
  "rps": 93.0,
  "ground_truth": false,
  "source": "simulator"
}
~~~

Ground-truth is generated only for simulation; real external telemetry must omit labels. Unexpected fields, naive timestamps and out-of-bounds/non-finite data are rejected. See [event dictionary](docs/DATA_DICTIONARY.md).

## API

| Method | Endpoint | Outcome |
|---|---|---|
| GET | /api/health | Status |
| GET | /api/summary?minutes=60 | Event/anomaly counts, rate, p50/p95, simulator precision/recall |
| GET | /api/events?anomalies_only=true&limit=100 | Findings and investigation states |
| GET | /api/trends?minutes=60 | Minute trend buckets |
| PATCH | /api/events/{event_id}/status | Review status new / investigating / resolved / dismissed |

Setting API_TOKEN makes PATCH require a bearer token. An empty token is suitable only for isolated local demos, never an exposed public service.

## Repository tree

~~~text
Real-Time-Streaming-Anomaly-Detection/
├── data/simulated/
├── producer/                # simulation, Kafka publisher
├── consumer/                # validator, DLQ, acknowledgements
├── src/
│   ├── features/            # transformations
│   ├── models/              # online detector + offline ML experiment
│   ├── sinks/               # SQL persistence
│   ├── alerts/              # severity
│   ├── monitoring/          # Prometheus metrics
│   ├── schema.py
│   ├── service.py
│   └── demo.py
├── backend/app/main.py      # FastAPI
├── frontend/src/           # React UI and labelled simulated preview
├── docker/                  # Prometheus config
├── scripts/                 # local performance measurement
├── tests/                   # schema, ML, SQL, API, offline integration
├── docs/
│   ├── assets/              # TEN original vector diagrams/charts
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── MODEL_CARD.md
│   ├── EVALUATION.md
│   ├── RUNBOOK.md
│   ├── SECURITY.md
│   ├── PORTFOLIO_CASE_STUDY.md
│   └── VISUAL_GALLERY.md
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
└── README.md
~~~

## Ten original visual assets

1. [Project cover](docs/assets/01-streamwatch-cover.svg)
2. [End-to-end architecture](docs/assets/02-end-to-end-architecture.svg)
3. [Kafka topics and DLQ](docs/assets/03-kafka-topic-topology.svg)
4. [Event schema contract](docs/assets/04-event-data-contract.svg)
5. [Feature pipeline](docs/assets/05-feature-and-model-flow.svg)
6. [Illustrative anomaly score chart](docs/assets/06-anomaly-score-timeline.svg)
7. [Illustrative throughput chart](docs/assets/07-event-throughput.svg)
8. [Latency instrumentation](docs/assets/08-latency-budget.svg)
9. [Investigation state machine](docs/assets/09-investigation-state-machine.svg)
10. [Development services graph](docs/assets/10-deployment-services.svg)

![Investigation lifecycle](docs/assets/09-investigation-state-machine.svg)

## What is not completed or independently validated

- No **public cloud deployment** of Redpanda, Python worker, database, API or React stack.
- Kafka consumer/model state is not durable across worker restarts; the online model rewarms after restart.
- No external production telemetry, drift-study validation, external ground-truth outcomes or domain review.
- No TLS, broker authentication, role-based authorization, protected user identity, production secrets or alert on-call.
- No independent load test, chaos drill, production latency SLA or disaster recovery.
- CSV and React preview are educational aids; browser fixtures are always labelled synthetic.

The current code delivers an inspectable, locally runnable and CI-testable portfolio project, not an enterprise security certification. Review [architecture](docs/ARCHITECTURE.md), [operational runbook](docs/RUNBOOK.md) and [security](docs/SECURITY.md).

**Created by Kavali Harshavardhan** · [GitHub profile](https://github.com/harshakavali81-collab) · [Career portfolio](https://harshakavali81-collab.github.io/harshavardhan-portfolio/) · MIT license.
