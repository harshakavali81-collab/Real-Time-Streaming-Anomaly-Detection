# Event schema and data dictionary

![Schema illustration](assets/04-event-data-contract.svg)

| Field | Type | Validation |
|---|---|---|
| schema_version | integer | exactly 1 |
| event_id | string | ASCII alphanumeric / hyphen, 8 to 80 chars |
| service | enum | checkout, payments, search, identity |
| timestamp | datetime | timezone-aware |
| latency_ms | float | finite, 0 to 120000 |
| cpu_pct | float | finite, 0 to 100 |
| error_rate | float | finite, 0 to 1 |
| rps | float | finite, 0 to 100000 |
| ground_truth | optional boolean | simulator label only |
| source | enum | simulator, external |

Derived fields: model, anomaly score, reason, severity, triage status, event/store timestamp, processing_ms and e2e_latency_ms.

Unknown fields, invalid service names, non-finite numbers and naive timestamps cause validation failures. Production producer identity and privacy controls are required before accepting external events.
