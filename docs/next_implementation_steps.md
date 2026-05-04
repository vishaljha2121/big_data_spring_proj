# Next Implementation Steps

## Current Status

Milestone 4C status: **PASSED**, pending only the final validation rerun immediately before submission.

Completed milestones:

- Milestone 1B: cleaned/curated data layer
- Milestone 2A: point-in-time feature layer, player baselines, replay manifest
- Milestone 2.5: parallel readiness and contract freeze
- Milestone 2.6: CourtIQ audit and preservation
- Milestone 2.7: model artifacts and replay/Kafka dry-run implementation
- Milestone 3B: local JSONL streaming scorer
- Milestone 4A: local file-backed FastAPI serving layer
- Milestone 4B: minimal dashboard over documented API
- Milestone 4C: final build freeze, preflight, smoke test, and one-command demo runner

## Final Demo Path

Use the one-command launcher:

```bash
bash scripts/run_full_demo.sh
```

It starts:

- FastAPI backend: `http://127.0.0.1:8000`
- OpenAPI docs: `http://127.0.0.1:8000/docs`
- React/Vite dashboard: `http://127.0.0.1:5173`

Stop remaining demo processes:

```bash
bash scripts/stop_full_demo.sh
```

## Required Pre-Submission Validation

Run:

```bash
.venv/bin/python scripts/final_preflight_check.py
.venv/bin/python scripts/smoke_test_full_demo.py
.venv/bin/python scripts/validate_api_contract.py
.venv/bin/python scripts/validate_frontend_build.py
.venv/bin/python scripts/validate_scored_events.py --events data/results/streaming_scoring/scored_events_sample.jsonl --schema contracts/scored_event_schema.json --odds-latest data/models/odds/latest.json --report data/results/streaming_scoring/scoring_validation_report.json --expected-count 1000
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_replay_producer.py --events data/results/replay_dry_run/sample_events.jsonl --schema contracts/point_event_schema.json
.venv/bin/python scripts/validate_feature_layer.py --curated data/curated --features data/features --baselines data/baselines --replay data/replay --contracts contracts
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```

## Remaining Work

The next work is final report and presentation packaging, not new architecture.

Recommended final tasks:

- capture dashboard screenshots
- capture API docs screenshot
- capture validation command output or reports
- prepare final slides
- write final report sections from the audit docs
- rehearse the one-command demo path

## Known Limitations To Report Honestly

- Point probabilities are point-level model probabilities, not betting odds and not match-win probabilities.
- Risk scores are statistical anomaly signals for review, not proof of misconduct or match-fixing.
- Kafka runtime code and dry-run replay exist, but Kafka runtime is not required for the local final demo.
- The API is file-backed over the validated scored sample output.
- Surface-specific features remain blocked because surface coverage is unavailable.
- Rally-length features remain sparse and are not primary MVP features.
- ATP bridge features remain blocked until a reliable point-to-match join is validated.

## Do Not Start Before Submission

- PostgreSQL
- Redis
- authentication
- production deployment
- new streaming architecture
- model retraining unless artifact validation breaks
- frontend redesign
