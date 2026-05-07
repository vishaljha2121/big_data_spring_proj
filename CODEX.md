# CODEX.md — Tennis Big Data Project Instructions

## Project Goal

Build a tennis point-level analytics platform with validated batch data, model artifacts, replay infrastructure, and later streaming/API/frontend layers.

## Current Priority

Current completed milestone: **Milestone 5B — Full Match Replay Experience, Data Coverage Fix, and Real Match Labeling**.

Milestone 1B, Milestone 2A, Milestone 2.5, Milestone 2.6, Milestone 2.7, Milestone 3B, Milestone 4A, Milestone 4B, Milestone 4C, Milestone 4D, Milestone 4E, Milestone 4F, Milestone 5A, and Milestone 5B are complete and validated.

Milestone 5B key outcomes:
- Replay Center now has real point-by-point playback with Step ±1, Play/Pause, and speed controls.
- Full-demo scored dataset: 50 matches, 9,000+ events generated from the replay manifest using the existing model (no retraining).
- Dashboard data coverage was a serving/sample issue, not a model-training issue.
- Player names are now the primary match label; synthetic IDs are secondary metadata.
- New API endpoints: `/api/data/coverage`, `/api/replay/matches`, `/api/replay/matches/{id}/events`.

The next allowed priority is:

- **Screenshots, report, and slides**
- **Final submission cleanup**
- **Bug fixes only if a validation or demo blocker appears**

Do not redesign the frontend. Do not introduce PostgreSQL, Redis, authentication, deployment work, or another broad product architecture change. Kafka/Spark runtime can be claimed only with the existing Milestone 5A reports.

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
- `data/results/streaming_scoring/scored_events_sample.jsonl`
- `data/results/streaming_scoring/scored_events_sample.parquet`
- `api/app/main.py`
- `docs/api_contract.md`
- `contracts/api_openapi_snapshot.json`
- `frontend/`
- `data/results/frontend_validation/frontend_validation_report.json`
- `scripts/run_full_demo.sh`
- `scripts/stop_full_demo.sh`
- `scripts/final_preflight_check.py`
- `data/results/final_demo/final_preflight_report.json`
- `frontend/src/theme/surfaceThemes.js`
- `frontend/src/shell/navigation.js`
- `docs/mockup_pivot_analysis.md`
- `docs/mockup_to_api_mapping.md`
- `spark_streaming/`
- `scripts/run_streaming_demo.sh`
- `docs/streaming_gap_analysis.md`
- `data/results/streaming_scoring/scored_events_demo_full.jsonl`
- `data/results/streaming_scoring/scored_events_demo_full.parquet`
- `data/results/streaming_scoring/full_demo_scoring_report.json`
- `scripts/generate_full_demo_scored_matches.py`
- `api/app/routes/replay.py`
- `docs/full_replay_data_coverage_gap_analysis.md`

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

Future final packaging work may not modify Milestone 1B/2A generated Parquet outputs, retrain Milestone 2.7 artifacts, or change the API contract without updating docs/tests.

## No Overclaiming

Risk scores are statistical anomaly signals only. Do not claim match-fixing detection, proof of misconduct, or injury detection.

CourtIQ replay producer files under `external_review/courtiq/` are reference-only. Do not treat them as canonical Kafka completion evidence.

## Deprecated Plan

`2_week_execution_plan.md` is historical. Do not follow it as current implementation source of truth.

## Validation Gate

Milestone 5B baseline gates include:

```bash
.venv/bin/python scripts/final_preflight_check.py
.venv/bin/python scripts/smoke_test_full_demo.py
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_replay_producer.py --events data/results/replay_dry_run/sample_events.jsonl --schema contracts/point_event_schema.json
.venv/bin/python scripts/validate_scored_events.py --events data/results/streaming_scoring/scored_events_sample.jsonl --schema contracts/scored_event_schema.json --odds-latest data/models/odds/latest.json --report data/results/streaming_scoring/scoring_validation_report.json --expected-count 1000
.venv/bin/python scripts/validate_api_contract.py
.venv/bin/python scripts/validate_frontend_build.py
.venv/bin/python -m pytest tests
```

all pass.

Kafka/Spark runtime gates require:

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
bash infra/kafka/kafka_setup.sh
.venv/bin/python scripts/validate_kafka_runtime.py
.venv/bin/python scripts/run_kafka_replay_smoke.py --max-events 1000
.venv/bin/python scripts/run_spark_streaming_scorer.py --max-events 1000 --timeout-seconds 60
.venv/bin/python scripts/validate_spark_streaming_output.py --expected-count 1000
bash scripts/run_streaming_demo.sh --max-events 1000
```

## Demo Runner

Use this as the primary local product launch path:

```bash
bash scripts/run_full_demo.sh
```

It starts FastAPI on `http://127.0.0.1:8000`, the API docs on `http://127.0.0.1:8000/docs`, and the frontend dashboard on `http://127.0.0.1:5173`. Stop remaining demo processes with:

```bash
bash scripts/stop_full_demo.sh
```
