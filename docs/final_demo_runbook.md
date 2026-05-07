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

## Kafka + Spark Streaming Evidence

Milestone 5A validated the real streaming path. To rerun it:

```bash
bash scripts/run_streaming_demo.sh --max-events 1000
```

The current reports show `PASSED`:

- `data/results/kafka_runtime/kafka_runtime_report.json`
- `data/results/kafka_runtime/kafka_replay_smoke_report.json`
- `data/results/spark_streaming/spark_streaming_run_report.json`
- `data/results/spark_streaming/spark_streaming_validation_report.json`

The deterministic JSONL path remains the fallback for environments where Docker or Spark cannot run.

Frontend build:

```bash
cd frontend
npm install
npm run build
cd ..
```

## Presentation Path

1. Start with the Centre Court Analytics app shell: left sidebar groups, sticky top header, API readiness badge, and feature-scope banner.
2. On **Dashboard**, highlight the KPI grid, featured match, prediction preview, pipeline quality card, recent matches, risk signals, and reports.
3. Open **Match Browser**. Search/select a match, show player names as the primary label, and point out that replay IDs are secondary.
4. Open **Replay Center**. Explain that local replay dry-run is validated and Kafka runtime is not claimed as executed.
5. Open **Point Timeline**. Show replay order, server, point probability bars, and risk buckets for individual points.
6. Open **Prediction Center**. State that this is point-level scoring, not match-winner prediction and not betting odds.
7. Open **Model Performance** and walk through:
   - Our point-level model metrics (AUC, Brier, throughput)
   - Three public reference benchmarks
   - Fair comparison verdict
   - What would make the comparison fair
8. Open **Validation** and **Pipeline Monitor** to show final evidence, throughput, p95 latency, and local API status.
9. Open **Reports** to show the submission documents and audit trail.
10. Briefly visit the partial modules:
   - **Players** and **Player Comparison** are sample-derived from local scored matches.
   - **Surface Analytics** is blocked by unavailable surface metadata.
   - **Rankings** are sample-derived and not official ATP rankings.
11. Open `/docs` briefly to show that the frontend is backed by documented API endpoints.

## Suggested Talk Track

This project starts from curated tennis point data, builds point-in-time-safe features, trains a lightweight point-outcome model, prepares replay events, scores those replay events locally, serves the scored output through FastAPI, and displays it in a dashboard. The dashboard is intentionally local and file-backed for a reliable deadline demo.

The probability shown is the model's point-level probability for Player A or Player B on the current point. It is not a betting odd and it is not a match-win probability. The risk score is a conservative statistical anomaly signal for review, not proof of misconduct or match-fixing.

Our model is point-level, so it should not be directly compared to match-level betting accuracy. The Model Comparison Context panel explains this honestly and shows what would be needed for a fair head-to-head comparison.

The Centre Court app shell is intentionally broader than the current API. Pages with unsupported backend data are clearly labeled as planned or sample-derived, so the demo shows product direction without pretending that official tournament, surface, or ATP-ranking integrations are already complete.

## What Not To Claim

- Do not claim point probability is match-win probability.
- Do not claim outputs are betting odds.
- Do not claim risk score proves match-fixing, misconduct, or injury.
- Do not claim Kafka runtime was required or executed for the local dashboard demo.
- Do not claim this is production deployed.
- Do not claim our point-level model is better than match-level prediction systems.
- Do not claim point-level AUC is directly comparable to match-level accuracy.
