# CODEX.md — Tennis Big Data Project Instructions

## Project Goal

Build a tennis point-level analytics platform with validated batch data, model artifacts, replay infrastructure, and later streaming/API/frontend layers.

## Current Priority

Current milestone: **Milestone 2.5 — Parallelization Readiness, Contract Freeze, and Workstream Split**.

Milestone 1B and Milestone 2A are complete and validated. Milestone 2B and Milestone 3A are intentionally not implemented in this milestone.

After Milestone 2.5, the next priorities split into:

- Track A: **Milestone 2B Model Artifact Track** on branch `feature/milestone-2b-model-artifacts`
- Track B: **Milestone 3A Replay / Kafka Infra Track** on branch `feature/milestone-3a-replay-producer`

Do not start Spark Structured Streaming, FastAPI, React, PostgreSQL serving, or frontend work until both tracks pass and merge.

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

Track A owns model scripts, model artifacts, model evaluation outputs, and model docs.

Track B owns Kafka/replay producer code, Kafka config, replay validation, and replay producer docs.

Neither track may modify Milestone 1B/2A generated Parquet outputs without explicit team agreement.

## No Overclaiming

Risk scores are statistical anomaly signals only. Do not claim match-fixing detection, proof of misconduct, or injury detection.

## Deprecated Plan

`2_week_execution_plan.md` is historical. Do not follow it as current implementation source of truth.

## Validation Gate

Milestone 2.5 is done only when:

```bash
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```

both pass.
