# StreamWatch AI architecture

![Architecture](assets/02-end-to-end-architecture.svg)

## Message flow

~~~mermaid
flowchart LR
  A[Seeded synthetic generator] --> B[Redpanda Kafka topic]
  B --> C[Consumer]
  C --> D{Pydantic valid?}
  D -->|No| E[Dead-letter topic]
  D -->|Yes| F[Feature transforms]
  F --> G[Per-service online detector]
  G --> H[SQL idempotent sink]
  H --> I[FastAPI]
  I --> J[React dashboard]
  H --> K[Investigation statuses]
~~~

Producer keys messages by service. One consumer group disables automatic offset commits. Malformed messages go to the DLQ and the source offset is committed **only after the DLQ broker acknowledges**. A valid event is deduplicated by ID, scored and written to SQL before its offset is committed.

Backend monitoring reads the SQL store, including minute trend buckets and p95 timing. React polls the API every five seconds. Prometheus scrapes worker-local counters and histograms on port 9100 inside Compose.

## Delivery and failure tradeoffs

| Scenario | Current behavior | Production requirement |
|---|---|---|
| Kafka replay | Unique event ID prevents duplicate SQL rows | Durable model state for replay-safe learning |
| Invalid event | DLQ then source acknowledgement | DLQ retention, privacy controls and human replay tools |
| SQL outage | Processing fails, source offset not committed | Backoff, retry, incident monitors |
| Consumer restart | Committed offsets resume; online baseline resets | Model snapshots / stateful streaming platform |
| Broker unreachable | Producer/consumer log errors | Strong reconnect and error budget policies |
| Multiple workers | SQL IDs prevent repeated insertion but model profiles diverge | Partition-aligned state and coordinated rebalances |

## Timing

Processing latency is elapsed Python time around scoring/save. End-to-end is wall-clock insert timestamp minus event timestamp; queueing and clock skew can affect it. Kafka lag is **not** inferred from SQL counts.

## Development topology

Single Redpanda node and single PostgreSQL instance, without TLS or multi-zone resilience. No public cloud deployment is claimed.

![Services](assets/10-deployment-services.svg)
