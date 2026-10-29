# Repository standard

## Layout

This repository keeps its working source paths. A shared portfolio structure does not require moving a React application, Python package, BI workbook or Verilog project into identical runtime directories.

| Area | Convention |
| --- | --- |
| Landing page | `README.md`: purpose, visuals, demo, features, stack, architecture, setup, tradeoffs and roadmap |
| Detailed reference | `PROJECT_GUIDE.md`: retained project-specific explanation and historical release notes |
| Documentation | `docs/`: design, inventory, reproduction and evidence |
| Work intake | `.github/ISSUE_TEMPLATE/`: bug and feature forms |
| Review | `.github/PULL_REQUEST_TEMPLATE.md`: linked issue, behavior and validation |
| Automation | `.github/workflows/portfolio-docs.yml`: README section and local-link checks |
| Source and tests | Existing project-specific paths listed below; no empty source/test placeholders |

## Workflow

1. Open an issue describing the user problem and measurable acceptance criteria.
2. Add it to a GitHub Project with Todo, In progress, Review and Done states when a board is configured.
3. Use a focused branch and meaningful commits, such as `docs: correct local setup paths` or `fix(api): reject malformed input`.
4. Run the project's documented checks and `python scripts/check_portfolio_docs.py`.
5. Open a pull request with actual validation results and `Closes #<issue-number>`.
6. Merge after review; record release evidence and update the issue/board.

Board creation, profile pins, repository social previews and milestone settings require account-level configuration. This file does not claim those settings have been applied.

## Validation scope

The documentation check validates the landing-page headings and local link targets only. It does not execute models, certify test coverage, inspect Git history for secrets, verify external websites, or prove production readiness. Existing application workflows remain the source of runtime CI evidence.

Keep credentials in local environment variables. A gitignore rule does not remove secrets already tracked or committed. Use only permitted sample data in public demos.

## Inventory at standardization

The following are the pre-existing public project files. New standardization files are described above. Historical guides may mention external bundles that are not part of this list.

- [`Dockerfile`](<../Dockerfile>)
- [`LICENSE`](<../LICENSE>)
- [`README.md`](<../README.md>)
- [`backend`](<../backend>)
- [`backend/__init__.py`](<../backend/__init__.py>)
- [`backend/app`](<../backend/app>)
- [`backend/app/__init__.py`](<../backend/app/__init__.py>)
- [`backend/app/main.py`](<../backend/app/main.py>)
- [`consumer`](<../consumer>)
- [`consumer/__init__.py`](<../consumer/__init__.py>)
- [`consumer/run.py`](<../consumer/run.py>)
- [`data`](<../data>)
- [`data/simulated`](<../data/simulated>)
- [`data/simulated/README.md`](<../data/simulated/README.md>)
- [`docker`](<../docker>)
- [`docker-compose.observability.yml`](<../docker-compose.observability.yml>)
- [`docker-compose.yml`](<../docker-compose.yml>)
- [`docker/alert_rules.yml`](<../docker/alert_rules.yml>)
- [`docker/grafana`](<../docker/grafana>)
- [`docker/grafana/dashboards.yml`](<../docker/grafana/dashboards.yml>)
- [`docker/grafana/datasources.yml`](<../docker/grafana/datasources.yml>)
- [`docker/grafana/streamwatch.json`](<../docker/grafana/streamwatch.json>)
- [`docker/prometheus.yml`](<../docker/prometheus.yml>)
- [`docs`](<../docs>)
- [`docs/ARCHITECTURE.md`](<../docs/ARCHITECTURE.md>)
- [`docs/CI_EVIDENCE.md`](<../docs/CI_EVIDENCE.md>)
- [`docs/DATA_DICTIONARY.md`](<../docs/DATA_DICTIONARY.md>)
- [`docs/DEMO_CHECKLIST.md`](<../docs/DEMO_CHECKLIST.md>)
- [`docs/DEPLOYMENT_BLUEPRINT.md`](<../docs/DEPLOYMENT_BLUEPRINT.md>)
- [`docs/EVALUATION.md`](<../docs/EVALUATION.md>)
- [`docs/MODEL_CARD.md`](<../docs/MODEL_CARD.md>)
- [`docs/OBSERVABILITY_VERIFICATION.md`](<../docs/OBSERVABILITY_VERIFICATION.md>)
- [`docs/OPERATIONS.md`](<../docs/OPERATIONS.md>)
- [`docs/PERFORMANCE_PLAN.md`](<../docs/PERFORMANCE_PLAN.md>)
- [`docs/PORTFOLIO_CASE_STUDY.md`](<../docs/PORTFOLIO_CASE_STUDY.md>)
- [`docs/RUNBOOK.md`](<../docs/RUNBOOK.md>)
- [`docs/SECURITY.md`](<../docs/SECURITY.md>)
- [`docs/THREAT_MODEL.md`](<../docs/THREAT_MODEL.md>)
- [`docs/VISUAL_GALLERY.md`](<../docs/VISUAL_GALLERY.md>)
- [`docs/assets`](<../docs/assets>)
- [`docs/assets/01-streamwatch-cover.svg`](<../docs/assets/01-streamwatch-cover.svg>)
- [`docs/assets/02-end-to-end-architecture.svg`](<../docs/assets/02-end-to-end-architecture.svg>)
- [`docs/assets/03-kafka-topic-topology.svg`](<../docs/assets/03-kafka-topic-topology.svg>)
- [`docs/assets/04-event-data-contract.svg`](<../docs/assets/04-event-data-contract.svg>)
- [`docs/assets/05-feature-and-model-flow.svg`](<../docs/assets/05-feature-and-model-flow.svg>)
- [`docs/assets/06-anomaly-score-timeline.svg`](<../docs/assets/06-anomaly-score-timeline.svg>)
- [`docs/assets/07-event-throughput.svg`](<../docs/assets/07-event-throughput.svg>)
- [`docs/assets/08-latency-budget.svg`](<../docs/assets/08-latency-budget.svg>)
- [`docs/assets/09-investigation-state-machine.svg`](<../docs/assets/09-investigation-state-machine.svg>)
- [`docs/assets/10-deployment-services.svg`](<../docs/assets/10-deployment-services.svg>)
- [`frontend`](<../frontend>)
- [`frontend/Dockerfile`](<../frontend/Dockerfile>)
- [`frontend/index.html`](<../frontend/index.html>)
- [`frontend/nginx.conf`](<../frontend/nginx.conf>)
- [`frontend/package.json`](<../frontend/package.json>)
- [`frontend/src`](<../frontend/src>)
- [`frontend/src/demo.js`](<../frontend/src/demo.js>)
- [`frontend/src/main.jsx`](<../frontend/src/main.jsx>)
- [`frontend/src/styles.css`](<../frontend/src/styles.css>)
- [`frontend/vite.config.js`](<../frontend/vite.config.js>)
- [`producer`](<../producer>)
- [`producer/__init__.py`](<../producer/__init__.py>)
- [`producer/run.py`](<../producer/run.py>)
- [`producer/simulator.py`](<../producer/simulator.py>)
- [`requirements.txt`](<../requirements.txt>)
- [`scripts`](<../scripts>)
- [`scripts/__init__.py`](<../scripts/__init__.py>)
- [`scripts/benchmark.py`](<../scripts/benchmark.py>)
- [`scripts/kafka_load.py`](<../scripts/kafka_load.py>)
- [`scripts/observability_smoke.py`](<../scripts/observability_smoke.py>)
- [`scripts/retention.py`](<../scripts/retention.py>)
- [`scripts/smoke.py`](<../scripts/smoke.py>)
- [`src`](<../src>)
- [`src/__init__.py`](<../src/__init__.py>)
- [`src/alerts`](<../src/alerts>)
- [`src/alerts/__init__.py`](<../src/alerts/__init__.py>)
- [`src/alerts/dlq.py`](<../src/alerts/dlq.py>)
- [`src/alerts/rules.py`](<../src/alerts/rules.py>)
- [`src/demo.py`](<../src/demo.py>)
- [`src/features`](<../src/features>)
- [`src/features/__init__.py`](<../src/features/__init__.py>)
- [`src/features/transform.py`](<../src/features/transform.py>)
- [`src/models`](<../src/models>)
- [`src/models/__init__.py`](<../src/models/__init__.py>)
- [`src/models/detector.py`](<../src/models/detector.py>)
- [`src/models/train.py`](<../src/models/train.py>)
- [`src/monitoring`](<../src/monitoring>)
- [`src/monitoring/__init__.py`](<../src/monitoring/__init__.py>)
- [`src/monitoring/metrics.py`](<../src/monitoring/metrics.py>)
- [`src/schema.py`](<../src/schema.py>)
- [`src/service.py`](<../src/service.py>)
- [`src/sinks`](<../src/sinks>)
- [`src/sinks/__init__.py`](<../src/sinks/__init__.py>)
- [`src/sinks/store.py`](<../src/sinks/store.py>)
- [`tests`](<../tests>)
- [`tests/conftest.py`](<../tests/conftest.py>)
- [`tests/test_api.py`](<../tests/test_api.py>)
- [`tests/test_api_hardening.py`](<../tests/test_api_hardening.py>)
- [`tests/test_detector.py`](<../tests/test_detector.py>)
- [`tests/test_e2e_demo.py`](<../tests/test_e2e_demo.py>)
- [`tests/test_kafka_load.py`](<../tests/test_kafka_load.py>)
- [`tests/test_privacy_retention.py`](<../tests/test_privacy_retention.py>)
- [`tests/test_recovery.py`](<../tests/test_recovery.py>)
- [`tests/test_schema.py`](<../tests/test_schema.py>)
- [`tests/test_storage.py`](<../tests/test_storage.py>)
