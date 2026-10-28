# Security scope and remaining production work

**This code is for local educational use, not production incident monitoring.**

Present: strict event contract, SQL parameterized statements, event-ID deduplication, optionally required bearer token on triage, loopback-bound development ports, no client-side hardcoded secrets and non-root Python Docker runtime.

Not implemented: external HTTPS/TLS, Kafka and DB transport authentication, RBAC, authenticated identity and audit logs, rate limits, multi-tenancy, secret rotation, durable model state, horizontally consistent scoring, public load-balancer security, data retention, safe replay and disaster recovery.

Development Postgres password is a placeholder, never expose the default stack to the Internet. Provide a proper secret to API_TOKEN for any accessible triage mutation; implement stronger identity and broker controls before public hosting.

Invalid DLQ messages include truncated original payload; do not send PII or private records without privacy review and restricted DLQ permissions.
