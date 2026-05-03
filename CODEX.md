# CODEX.md — Tennis Big Data Project Instructions

## Project Goal

Build a tennis point-level analytics platform with validated batch data, model artifacts, replay infrastructure, and later streaming/API/frontend layers.

## Current Priority

Current completed milestone: **Milestone 2.7 — Model Artifacts + Replay/Kafka Producer Implementation**.

Milestone 1B, Milestone 2A, Milestone 2.5, Milestone 2.6, and Milestone 2.7 are complete and validated. Milestone 2B model artifacts are published and Milestone 3A replay dry-run implementation is complete. Kafka runtime code exists, but Kafka was not executed locally.

The next allowed priority is:

- **Milestone 3B Streaming Scorer Integration** on branch `feature/milestone-3b-streaming-scorer`

Do not start FastAPI, React, PostgreSQL serving, or frontend work until the streaming scorer consumes replay events, computes online features, loads odds/risk artifacts, and writes scored output.

Do not use CourtIQ assets unless they were merged or listed as approved reference in `docs/courtiq_integration_audit.md`.

## Stable Source Data

Allowed stable inputs for the next tracks:

- `data/features/point_features/`
- `data/features/match_features/`
- `data/baselines/player_baselines/`
- `data/replay/manifests/replay_manifest_v1.parquet`
- `data/features/feature_quality_report.json`
- `data/features/validation_report.json`
- `data/baselines/baseline_quality_report.json`
- `data/replay/replay_manifest_report.json`
- `contracts/`
- `data/models/odds/latest.json`
- `data/models/risk/latest.json`
- `infra/kafka/topic_config.json`
- `producer/replay_producer.py`

Do not use staging CSV.GZ files directly.

## Contract Discipline

Do not change frozen contracts without team agreement:

- `contracts/point_event_schema.json`
- `contracts/replay_manifest_schema.json`
- `contracts/odds_model_metadata_schema.json`
- `contracts/odds_model_feature_schema.json`
- `contracts/risk_model_metadata_schema.json`
- `contracts/risk_config_schema.json`
- `contracts/model_registry_schema.json`
- `contracts/model_eval_report_schema.json`
- `contracts/replay_producer_config_schema.json`
- `contracts/kafka_topic_config_schema.json`
- `contracts/parallel_workstream_handoff_schema.json`

## Track Boundaries

Track A model artifact work is complete.

Track B replay dry-run and Kafka setup work is complete except Kafka runtime execution.

Future streaming scorer work may not modify Milestone 1B/2A generated Parquet outputs.

## No Overclaiming

Risk scores are statistical anomaly signals only. Do not claim match-fixing detection, proof of misconduct, or injury detection.

CourtIQ replay producer files under `external_review/courtiq/` are reference-only. Do not treat them as canonical Kafka completion evidence.

## Deprecated Plan

`2_week_execution_plan.md` is historical. Do not follow it as current implementation source of truth.

## Validation Gate

Milestone 2.7 is done only when:

```bash
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_replay_producer.py --events data/results/replay_dry_run/sample_events.jsonl --schema contracts/point_event_schema.json
.venv/bin/python -m pytest tests
```

both pass.
