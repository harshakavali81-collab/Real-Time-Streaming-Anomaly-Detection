# Synthetic data only

No sensitive, private, company, financial or real customer events are included.

The code under producer/simulator.py generates service-labelled telemetry on demand. Four services are checkout, payments, search and identity. Each has distinct latency / CPU / errors / RPS baselines.

Independent seeded pseudo-randomness makes replay reproducible. Anomalies are injected as latency spikes, CPU-error surges or errors-with-traffic bursts, at a default probability of 8%.

Simulator labels allow synthetic precision/recall but do not represent actual service incidents. Offline mode uses a 5-events/sec generated timeline; Kafka live local mode uses the actual producer wall-clock.
