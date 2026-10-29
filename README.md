# StreamWatch AI

Microservices emit latency, CPU, error-rate and request-volume events. Operators need a structured way to identify unusual signals, investigate findings, and measure system behavior. StreamWatch AI demonstrates event publishing, strict validation, at-least-once consumption, online detection, durable SQL persistence, monitoring and human review.

[Setup](#local-installation--setup-guide) · [Architecture](#architecture--system-design-diagram) · [Detailed guide](PROJECT_GUIDE.md) · [Repository standard](docs/REPOSITORY_STANDARD.md)

## Visuals

![StreamWatch AI](<docs/assets/01-streamwatch-cover.svg>)

Existing project visual; diagrams and illustrative graphics are not evidence of a deployed application.

## Live Link / Demo

Existing published preview link: [Open browser preview](https://harshakavali81-collab.github.io/harshavardhan-portfolio/). This update does not independently verify its availability or backend deployment.

## Key Features

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

## Tech Stack

![Python](https://img.shields.io/badge/Python-334155?style=flat-square) ![FastAPI](https://img.shields.io/badge/FastAPI-334155?style=flat-square) ![scikit-learn](https://img.shields.io/badge/scikit--learn-334155?style=flat-square) ![React](https://img.shields.io/badge/React-334155?style=flat-square) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-334155?style=flat-square) ![Docker](https://img.shields.io/badge/Docker-334155?style=flat-square)

Dependency versions and optional packages are defined in the repository manifests.

## Architecture / System Design Diagram

[Architecture documentation / diagram](<docs/ARCHITECTURE.md>)

## Local Installation & Setup Guide

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

## Challenges & Solutions

**Repository organization:** this project uses `src/`, `backend/`, `frontend/`. Keeping those paths stable avoids breaking imports, asset links and deployment commands while the documentation follows a shared format. Project-specific technical limitations and prior release evidence are retained in [Project guide](PROJECT_GUIDE.md).

## Future Improvements

- Capture a reproducible end-to-end demo with runtime versions and sample inputs.
- Expand regression checks for invalid inputs and documented edge cases.
- Record measured results, data provenance and deployment limitations alongside each release.

## Scope and supporting evidence

<div align="center">



### Real-Time Streaming · Anomaly Detection · Investigation Intelligence

**Redpanda/Kafka → Python Validation & ML → PostgreSQL → FastAPI → React**

[](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/actions/workflows/ci.yml)





[Architecture](docs/ARCHITECTURE.md) · [Visual gallery](docs/VISUAL_GALLERY.md) · [Model card](docs/MODEL_CARD.md) · [Verified CI & measured offline benchmark](docs/CI_EVIDENCE.md) · · [Runbook](docs/RUNBOOK.md) · [Portfolio case study](docs/PORTFOLIO_CASE_STUDY.md)

</div>

> **Evidence boundary:** A complete-source educational **prototype** using explicitly simulated events. This is not a publicly deployed production monitoring service. Browser preview graphs are illustrative. No fabricated Kafka throughput, model accuracy or public performance is claimed.

## Repository Structure

| Location | Purpose |
| --- | --- |
| `src/` | Source modules |
| `backend/` | Backend services |
| `frontend/` | Frontend interface |
| `tests/` | Tests |
| `docs/` | Documentation |
| `data/` | Data and samples |
| `scripts/` | Automation scripts |
| `.github/` | Issue forms, PR template and automated checks |

[Complete file inventory and workflow](docs/REPOSITORY_STANDARD.md). Runtime entry points retain their existing paths.

## Workflow & Tracking

Use the [bug and feature forms](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/issues/new/choose) to define work with acceptance criteria. Keep tasks in Todo → In progress → Review → Done, and link a pull request with `Closes #<number>`. See [the maintenance workflow](docs/REPOSITORY_STANDARD.md#workflow).

## License

See [LICENSE](LICENSE) for the existing terms.
