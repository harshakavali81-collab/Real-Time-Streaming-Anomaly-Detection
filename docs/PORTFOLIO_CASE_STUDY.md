# StreamWatch AI — portfolio case study

## Problem

Microservices emit a continuous flow of operational events, but manual review cannot scale. An engineer needs an inspectable detection pipeline and a workflow that separates model suggestion from human incident classification.

## Implementation

I designed a local-first event system comprising deterministic synthetic telemetry generation, Redpanda's Kafka API, strict Pydantic schema validation, a malformed-message dead-letter topic and manual acknowledgement, online per-service statistical anomaly scoring, an idempotent PostgreSQL/SQLite sink, FastAPI monitoring, a responsive React review dashboard, and Prometheus instrumentation.

## Architecture

Event generation → Kafka topic → validation → feature engineering → online detector → SQL → API → charts and investigation statuses.

## Engineering decisions

Manual offset commits help demonstrate at-least-once processing; SQL event ID constraints prevent duplicated persisted alerts; per-service normalized online scoring offers interpretable baseline detections; simulator-provided labels enable controlled test evaluation with explicit scope.

## Evidence / readiness

Source includes tests, a repeatable offline demo, a local benchmark, a separate optional Isolation Forest experiment, GitHub CI, and ten original diagrams. Any pass counts or numerical performance must be confirmed against actual workflow logs before citing in a resume.

## Limitations

Synthetic events only. No independently validated real-world anomaly model, public production API, hosted Kafka/Postgres, durable ML state, high-availability deployment, enterprise authentication or SLA guarantee is established.

## Interview summary

“I built an event-driven anomaly detection prototype that validates Kafka messages, performs online scoring, stores findings idempotently, and exposes investigation controls. I can demonstrate the full local workflow and discuss why replay safety, model state, reliable metrics and production security are separate engineering concerns.”

[Repository](https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection) · [Architecture](ARCHITECTURE.md) · [Model card](MODEL_CARD.md)
