# Tennis Point-Level Analytics Project

This repository contains the validated data, model artifact, replay, scoring, local serving, and dashboard foundation for a tennis point-level analytics pipeline. Milestone 4E adds the final frontend narrative polish including KPI reordering, humanized labels, model comparison context, and replay ID handling.

## Current Status

- Milestone 1B: PASSED
- Milestone 2A: PASSED
- Milestone 2.5: PASSED after running `scripts/validate_parallel_readiness.py`
- Milestone 2.6: PASSED after CourtIQ integration audit and guardrail validation
- Milestone 2.7: PASSED for model artifacts and replay dry-run validation
- Milestone 2B: PASSED as part of Milestone 2.7
- Milestone 3A: PASSED for dry-run replay implementation; Kafka runtime was not executed locally
- Milestone 3B: VERIFIED PASSED for local JSONL streaming scorer integration
- Milestone 4A: PASSED for local file-backed FastAPI serving layer
- Milestone 4B: PASSED for minimal dashboard/frontend over documented API
- Milestone 4C: PASSED for final build freeze, full preflight, and one-command demo runner
- Milestone 4D: PASSED for frontend presentation redesign and demo polish
- Milestone 4E: PASSED for final frontend narrative polish, KPI reordering, humanized labels, and model comparison panel

## Completed Checklist

- [x] Converted staging CSV.GZ inputs into cleaned Parquet layers.
- [x] Built curated singles-only point data under `data/curated/singles_points/`.
- [x] Built curated singles match metadata under `data/curated/singles_matches/`.
- [x] Preserved invalid/special point evidence under `data/quarantine/`.
- [x] Built point-in-time-safe features under `data/features/point_features/`.
- [x] Built match features under `data/features/match_features/`.
- [x] Built player baselines under `data/baselines/player_baselines/`.
- [x] Built deterministic replay manifest under `data/replay/manifests/replay_manifest_v1.parquet`.
- [x] Added validation reports, schema contracts, tests, and audit docs through Milestone 2A.
- [x] Froze Track A and Track B contracts for parallel implementation.
- [x] Added paste-ready Codex prompts for both tracks.
- [x] Audited CourtIQ teammate repo and preserved compatible reference assets under `external_review/courtiq/`.
- [x] Trained and published an MVP odds model under `data/models/odds/v1/`.
- [x] Built and published a conservative risk config under `data/models/risk/v1/`.
- [x] Implemented canonical replay JSONL dry-run producer and validator.
- [x] Added local Kafka Compose and topic setup files.
- [x] Implemented local streaming scorer integration from replay JSONL to scored JSONL/Parquet.
- [x] Added online feature builder, model loader, risk scorer, scored event contract, validation, benchmark, and tests.
- [x] Added file-backed FastAPI serving layer over scored output.
- [x] Exported OpenAPI snapshot and API sample responses for frontend handoff.
- [x] Added minimal dashboard frontend over the documented FastAPI API.
- [x] Added final demo runbook, submission checklist, and frontend build validation.
- [x] Added final preflight checks and one-command local demo launcher.
- [x] Redesigned the dashboard with a clay-court presentation theme, theme switcher, polished chart, KPI strip, insight rail, and readable tables.
- [x] Reordered KPI strip with model quality metrics (AUC, Brier) and removed Risk Config from top KPIs.
- [x] Humanized all underscore/raw technical labels across the dashboard.
- [x] Made player names primary and synthetic IDs secondary throughout the UI.
- [x] Added Model Comparison Context panel with honest public reference benchmark context.
- [x] Created `docs/model_comparison_analysis.md` documenting fair comparison analysis.

## Remaining Checklist

- [ ] Final report and presentation packaging.
- [ ] Capture manual screenshots from the running dashboard.
- [ ] Prepare final slides from the validated runbook and screenshots.
- [ ] Do not add new architecture unless fixing a demo blocker.

## Key Findings So Far

- Curated singles point rows: `1,922,136`.
- Curated singles matches: `10,508`.
- Point feature rows: `1,922,136`.
- Match feature rows: `10,508`.
- Player baselines: `1,891`.
- Replay manifest events: `1,917,672`.
- Replay manifest matches: `10,464`.
- Replay exclusions: `44` matches.
- Surface coverage is `0.0%`; surface-based features remain blocked.
- Rally length coverage is about `5.96%`; rally length is not a primary MVP feature.
- ATP bridge remains unvalidated; ATP-derived labels/features remain blocked.
- CourtIQ had useful replay/Kafka reference code, but it did not contain model code or frontend assets.
- CourtIQ replay code is not canonical yet because it requires adaptation to frozen contracts and topic config.
- Published odds model target: `label_point_winner_is_player_a`.
- Published odds model type: `HistGradientBoostingClassifier`.
- Odds validation/test AUC: `0.6395` / `0.6415`.
- Odds validation/test Brier score: `0.2351` / `0.2347`.
- Risk artifact uses baseline deviation rules with `fake_labels_used=false`.
- Replay dry-run validation passed for `1000` canonical point events.
- Streaming scorer validated `1000` scored events with `0` invalid events.
- Streaming benchmark: `974.13` events/sec, average latency `0.9635` ms/event, p95 latency `1.5229` ms/event, model load time `3.2619` seconds.
- API validation passed with `1000` scored events and `6` unique matches exposed.
- Frontend build validation passed with local Node/npm.
- Dashboard theme system supports clay, hard, grass, and neutral themes. Clay is the default demo theme because source surface metadata is unavailable.
- Model comparison note: our model is a point-level predictor (test AUC 0.6415, test Brier 0.2347). Public tennis prediction references operate at match-level and use different metrics. Direct comparison is not valid without building a match-level predictor on the same evaluation set.

## CourtIQ Integration Audit

CourtIQ was inspected during Milestone 2.6. Useful files were preserved as reference-only under `external_review/courtiq/preserved_reference/`.

| Result | Summary |
| --- | --- |
| Files seen | `17` |
| Direct runtime merges | `0` |
| Preserved reference assets | replay producer, validation consumer, Kafka setup, Compose fragment, replay audit, point-event schema mismatch evidence |
| Rejected assets | duplicate/obsolete contracts, staging data notes, non-canonical completion claims |

Use `docs/courtiq_integration_audit.md`, `docs/courtiq_file_inventory.md`, and `docs/post_merge_next_phase_plan.md` before adapting any CourtIQ asset.

## Model Artifacts

```text
data/models/odds/latest.json
data/models/odds/v1/model.joblib
data/models/odds/v1/feature_schema.json
data/models/risk/latest.json
data/models/risk/v1/risk_config.json
```

## Replay Producer

Dry-run:

```bash
.venv/bin/python producer/replay_producer.py \
  --manifest data/replay/manifests/replay_manifest_v1.parquet \
  --config infra/kafka/topic_config.json \
  --dry-run \
  --dry-run-output data/results/replay_dry_run/sample_events.jsonl \
  --max-events 1000

.venv/bin/python scripts/validate_replay_producer.py \
  --events data/results/replay_dry_run/sample_events.jsonl \
  --schema contracts/point_event_schema.json
```

Kafka local:

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
bash infra/kafka/kafka_setup.sh
```

Kafka runtime was not executed in the current validation environment.

## One-Command Demo

Run the complete local demo stack:

```bash
bash scripts/run_full_demo.sh
```

The script validates the API contract, starts FastAPI, waits for `/health` and `/ready`, starts the Vite dashboard, and prints:

```text
Backend:  http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs
Frontend: http://127.0.0.1:5173
```

Logs and PID files are written under:

```text
data/results/final_demo/logs/
data/results/final_demo/pids/
```

Stop any remaining demo processes:

```bash
bash scripts/stop_full_demo.sh
```

Fast preflight:

```bash
.venv/bin/python scripts/final_preflight_check.py
.venv/bin/python scripts/smoke_test_full_demo.py
```

## Next Milestone

Final report and presentation packaging.

Scope:

- capture screenshots
- prepare slides/report
- rehearse the runbook
- avoid new backend architecture unless a blocker appears
- bug fixes only if a validation or demo blocker appears

## Streaming Scorer

Run the local JSONL scorer:

```bash
.venv/bin/python scripts/run_scoring_from_jsonl.py \
  --input-events data/results/replay_dry_run/sample_events.jsonl \
  --odds-latest data/models/odds/latest.json \
  --risk-latest data/models/risk/latest.json \
  --output-jsonl data/results/streaming_scoring/scored_events_sample.jsonl \
  --output-parquet data/results/streaming_scoring/scored_events_sample.parquet \
  --max-events 1000 \
  --report data/results/streaming_scoring/scoring_run_report.json
```

## Local API

Validate the API contract:

```bash
.venv/bin/python scripts/validate_api_contract.py
```

Run locally:

```bash
.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000
```

Key endpoints:

```text
GET /health
GET /ready
GET /api/summary
GET /api/scored-events
GET /api/scored-events/{event_id}
GET /api/matches
GET /api/matches/{synthetic_match_id}
GET /api/matches/{synthetic_match_id}/events
GET /api/risk/summary
GET /api/risk/events
GET /api/models/current
GET /api/benchmarks/latest
```

Contract artifacts:

```text
docs/api_contract.md
contracts/api_openapi_snapshot.json
contracts/api_response_examples.json
data/results/api_validation/api_validation_report.json
data/results/api_validation/sample_responses.json
```

## Frontend Dashboard

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Build/validate:

```bash
cd frontend
npm run build
cd ..
.venv/bin/python scripts/validate_frontend_build.py
```

The dashboard consumes:

```text
GET /health
GET /ready
GET /api/summary
GET /api/scored-events
GET /api/matches
GET /api/matches/{synthetic_match_id}
GET /api/matches/{synthetic_match_id}/events
GET /api/risk/summary
GET /api/risk/events
GET /api/models/current
GET /api/benchmarks/latest
```

Dashboard sections include a clay-court hero, KPI strip, selected match analytics, point probability timeline, risk summary, model metadata, benchmark evidence, match table, and scored events table. The UI states that probabilities are point-level probabilities, not betting odds, and risk scores are statistical anomaly signals, not proof of misconduct.

Theme notes:

- Default: clay-court demo theme.
- Available themes: clay, hard court, grass court, neutral.
- Surface metadata is unavailable in the current sample, so the theme switcher is frontend-only and does not imply true surface labels.

## Final Demo Sequence

```bash
.venv/bin/python scripts/final_preflight_check.py
.venv/bin/python scripts/validate_api_contract.py
.venv/bin/python scripts/validate_frontend_build.py
bash scripts/run_full_demo.sh
```

Manual fallback, if you do not use the one-command runner:

```bash
.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000
cd frontend
npm install
npm run dev
```

Then open `http://127.0.0.1:5173`.

Validate and benchmark:

```bash
.venv/bin/python scripts/validate_scored_events.py \
  --events data/results/streaming_scoring/scored_events_sample.jsonl \
  --schema contracts/scored_event_schema.json \
  --odds-latest data/models/odds/latest.json \
  --report data/results/streaming_scoring/scoring_validation_report.json \
  --expected-count 1000

.venv/bin/python scripts/benchmark_scoring_pipeline.py \
  --input-events data/results/replay_dry_run/sample_events.jsonl \
  --odds-latest data/models/odds/latest.json \
  --risk-latest data/models/risk/latest.json \
  --max-events 1000 \
  --report data/results/streaming_scoring/scoring_benchmark_report.json
```

Scored outputs:

```text
data/results/streaming_scoring/scored_events_sample.jsonl
data/results/streaming_scoring/scored_events_sample.parquet
data/results/streaming_scoring/scoring_run_report.json
data/results/streaming_scoring/scoring_validation_report.json
data/results/streaming_scoring/scoring_benchmark_report.json
```

## Historical Workstream Split

| Track | Branch | Owner Scope | Prompt |
| --- | --- | --- | --- |
| Track A | `feature/milestone-2b-model-artifacts` | model training, risk config, evaluation, two-phase publication | `docs/codex_prompt_milestone_2b.md` |
| Track B | `feature/milestone-3a-replay-producer` | Kafka local setup, replay producer, validation consumer, event contract | `docs/codex_prompt_milestone_3a.md` |

## Stable Inputs

```text
data/features/point_features/
data/features/match_features/
data/baselines/player_baselines/
data/replay/manifests/replay_manifest_v1.parquet
data/features/feature_quality_report.json
data/features/validation_report.json
data/baselines/baseline_quality_report.json
data/replay/replay_manifest_report.json
contracts/
```

Do not use `cleaned_data/` or staging CSV.GZ files for future modeling or replay work.

## Validate Parallel Readiness

```bash
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```

## Validate Milestone 2.7

```bash
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_replay_producer.py --events data/results/replay_dry_run/sample_events.jsonl --schema contracts/point_event_schema.json
.venv/bin/python scripts/validate_feature_layer.py --curated data/curated --features data/features --baselines data/baselines --replay data/replay --contracts contracts
.venv/bin/python -m pytest tests
```

## Validate Milestone 3B

```bash
.venv/bin/python scripts/validate_scored_events.py --events data/results/streaming_scoring/scored_events_sample.jsonl --schema contracts/scored_event_schema.json --odds-latest data/models/odds/latest.json --report data/results/streaming_scoring/scoring_validation_report.json --expected-count 1000
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_replay_producer.py --events data/results/replay_dry_run/sample_events.jsonl --schema contracts/point_event_schema.json
.venv/bin/python scripts/validate_feature_layer.py --curated data/curated --features data/features --baselines data/baselines --replay data/replay --contracts contracts
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```

## Validate Milestone 4A

```bash
.venv/bin/python scripts/validate_api_contract.py
.venv/bin/python -m pytest tests
```

## Validate CourtIQ Integration Guardrails

```bash
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```

## Deprecated Plan Warning

`2_week_execution_plan.md` is historical and deprecated. It references older Cassandra, Elasticsearch, Grafana/Kibana, 50M-record, and 25K events/sec goals that are not current milestone requirements. Use `README.md`, `CODEX.md`, `docs/parallel_workstream_handoff.md`, and current milestone docs as source of truth.
