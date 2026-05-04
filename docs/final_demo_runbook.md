# Final Demo Runbook

## Fast Path: One-Command Demo

From the repo root:

```bash
bash scripts/run_full_demo.sh
```

The launcher:

1. checks the Python virtual environment and required artifacts;
2. regenerates the scored sample if it is missing;
3. validates the API contract;
4. starts FastAPI on `127.0.0.1:8000`;
5. waits for `/health` and `/ready`;
6. starts the Vite dashboard on `127.0.0.1:5173`;
7. writes logs under `data/results/final_demo/logs/`.

Open:

```text
Backend:  http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs
Frontend: http://127.0.0.1:5173
```

Stop the demo:

```bash
bash scripts/stop_full_demo.sh
```

## Manual Fallback Path

Validate first:

```bash
.venv/bin/python scripts/final_preflight_check.py
.venv/bin/python scripts/smoke_test_full_demo.py
.venv/bin/python scripts/validate_api_contract.py
.venv/bin/python scripts/validate_frontend_build.py
```

Start the API:

```bash
.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Full Validation Commands

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

Frontend build:

```bash
cd frontend
npm install
npm run build
cd ..
```

## Presentation Path

1. Start with the clay-court hero, readiness badge, disclaimer chips, and KPI strip.
2. Use the court theme switcher to show Clay, Hard, Grass, and Neutral themes. Explain that clay is the default demo theme because surface metadata is unavailable.
3. Show `1000` scored local replay events and the match count in the KPI strip.
4. Select a match and show the large point probability timeline.
5. Show recent point events with probability bars and risk badges.
6. Show the risk summary and top risk events.
7. Show model metadata, including odds model version, feature count, and `fake_labels_used=false` for risk.
8. Show benchmark metrics for throughput and latency.
9. Open `/docs` briefly to show that the frontend is backed by documented API endpoints.

## Suggested Talk Track

This project starts from curated tennis point data, builds point-in-time-safe features, trains a lightweight point-outcome model, prepares replay events, scores those replay events locally, serves the scored output through FastAPI, and displays it in a dashboard. The dashboard is intentionally local and file-backed for a reliable deadline demo.

The probability shown is the model's point-level probability for Player A or Player B on the current point. It is not a betting odd and it is not a match-win probability. The risk score is a conservative statistical anomaly signal for review, not proof of misconduct or match-fixing.

## What Not To Claim

- Do not claim point probability is match-win probability.
- Do not claim outputs are betting odds.
- Do not claim risk score proves match-fixing, misconduct, or injury.
- Do not claim Kafka runtime was required or executed for the local dashboard demo.
- Do not claim this is production deployed.
