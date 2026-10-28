# Security scope and remaining production work

**This code is for local educational use, not production incident monitoring.**

Present: strict event contract, SQL parameterized statements, event-ID deduplication, production-required bearer token on triage and fail-closed production-mode startup, loopback-bound development ports, no client-side hardcoded secrets and non-root Python Docker runtime.

Not implemented: external HTTPS/TLS, Kafka and DB transport authentication, RBAC, authenticated identity and audit logs, rate limits, multi-tenancy, secret rotation, durable model state, horizontally consistent scoring, public load-balancer security, data retention, safe replay and disaster recovery.

Development Postgres password is a placeholder, never expose the default stack to the Internet. Provide a proper secret to API_TOKEN for any accessible triage mutation; implement stronger identity and broker controls before public hosting.

Invalid DLQ records now hold schema-field paths, payload size and SHA-256, but do not retain original payload or exception text. A hash of short predictable input can still be guessed; broker permissions and privacy review remain required.


## Operating controls added

A dedicated SQL investigation audit records status transitions with actor *class* (not verifiable user identity). The local retention command defaults to dry run and can delete both events and related audit; preserve required evidence before deletion.

Optional Grafana uses anonymous viewer access and a development-only password, bound to localhost. **Do not expose it as a public endpoint.** HTTPS, production identity, broker authentication, backup/recovery and penetration testing remain outstanding.
