# Centre Court Analytics

Centre Court Analytics is a local Big Data tennis analytics system that turns historical point-level match data into validated Parquet-style data layers, deterministic replay events, point-level probability scores, conservative risk signals, a FastAPI service, and a React dashboard for final review and demo.

## 1. What This Project Does

- Curates historical tennis point data into singles point and match layers.
- Replays historical matches as event streams with deterministic synthetic replay IDs.
- Scores each point with a point-level probability model and a conservative statistical risk signal.
- Serves validated scored output through a local FastAPI API.
- Presents the result in the Centre Court Analytics dashboard: Dashboard, Match Browser, Replay Center, Point Timeline, Prediction Center, Model Performance, Validation, and Pipeline Monitor.

The probability outputs are point-level model probabilities. They are not betting odds and they are not match-win probabilities.

## 2. Why This Satisfies Big Data Scope

| Big Data requirement | Implemented evidence |
| --- | --- |
| Dataset scale | 1,922,136 curated point rows and 10,508 curated singles matches |
| Replay scale | 1,917,672 replay events across 10,464 replay matches |
| Lake-style processing | Curated, feature, baseline, replay, model, and results layers under `data/` |
| Schema discipline | JSON contracts under `contracts/` and validation reports under `data/results/` |
| Streaming architecture | Kafka replay topic plus Spark Structured Streaming scorer |
| Checkpointed output | Spark checkpoint and JSONL/Parquet scored sinks under `data/checkpoints/` and `data/results/spark_streaming/` |
| Serving/product layer | FastAPI API plus Vite/React dashboard validated by scripts |

The local demo is intentionally bounded for reproducibility. The architecture demonstrates scalable patterns: partitioned Parquet-style artifacts, schema contracts, Kafka replay, Spark Structured Streaming, checkpointed scoring output, and API/dashboard serving over validated artifacts.

## 3. System Architecture

```text
raw data
  -> cleaned/curated Parquet
  -> point-in-time features
  -> replay manifest
  -> Kafka / JSONL replay
  -> Spark Structured Streaming / local scorer
  -> scored JSONL/Parquet
  -> FastAPI
  -> React dashboard
```

Key directories: `data/`, `contracts/`, `producer/`, `streaming/`, `spark_streaming/`, `api/`, `frontend/`, `infra/`, `scripts/`, `docs/`, and `presentation/`.

## 4. Key Results

| Metric | Value |
| --- | --- |
| Curated point rows | 1,922,136 |
| Curated matches | 10,508 |
| Replay events | 1,917,672 |
| Replay matches | 10,464 |
| Full-demo scored events | 9,049 events across 50 matches |
| Model target | `label_point_winner_is_player_a` |
| Model type | `HistGradientBoostingClassifier` |
| Test AUC | 0.6415 |
| Test Brier score | 0.2347 |
| Local scoring benchmark | 2,454.17 events/sec, 0.575 ms p95 latency |
| Kafka/Spark runtime | PASSED for 1,000 streamed/scored events |
| API/frontend validation | PASSED |

## 5. Run the Local Demo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_full_demo.sh
```

The demo runner validates the API contract, starts FastAPI, waits for health/readiness, starts the Vite dashboard, and writes logs under `data/results/final_demo/logs/`.

Open:

- Frontend: `http://127.0.0.1:5173`
- API docs: `http://127.0.0.1:8000/docs`
- API health: `http://127.0.0.1:8000/health`

Node/npm are required for the dashboard. If dependencies are already installed, `scripts/run_full_demo.sh` uses `frontend/node_modules`; otherwise it can run `npm install`.

Stop the demo:

```bash
bash scripts/stop_full_demo.sh
```

## 6. Optional Big Data Streaming Demo

Run this only when Docker, Java, PySpark, and the Spark Kafka connector are available:

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
bash infra/kafka/kafka_setup.sh
bash scripts/run_streaming_demo.sh --max-events 1000
```

The checked-in Milestone 5A reports show Kafka and Spark Structured Streaming passed for 1,000 events. Do not claim a fresh streaming run unless the script actually executes in the current environment.

## 7. Validation Commands

```bash
.venv/bin/python scripts/final_preflight_check.py
.venv/bin/python scripts/smoke_test_full_demo.py
.venv/bin/python scripts/validate_api_contract.py
.venv/bin/python scripts/validate_frontend_build.py
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_feature_layer.py --curated data/curated --features data/features --baselines data/baselines --replay data/replay --contracts contracts
.venv/bin/python -m pytest tests
```

Spark output validation, when the optional streaming demo has run:

```bash
.venv/bin/python scripts/validate_spark_streaming_output.py --expected-count 1000
```

## 8. Repository Map

| Path | Purpose |
| --- | --- |
| `api/` | FastAPI serving layer over validated local artifacts |
| `frontend/` | React dashboard for the professor-facing demo |
| `streaming/` | Local JSONL scorer, model loader, online feature builder, and risk scorer |
| `spark_streaming/` | Spark Structured Streaming scorer |
| `producer/` | Replay event producer for JSONL/Kafka paths |
| `infra/` | Kafka Docker Compose and topic setup |
| `data/` | Generated validated artifacts, model outputs, replay files, and evidence reports |
| `contracts/` | JSON schemas and API snapshots |
| `docs/` | Audits, runbooks, final report, validation index, and cleanup notes |
| `presentation/` | Final slide decks, scripts, diagrams, and screenshots |
| `scripts/` | Build, validation, scoring, API, demo, and streaming commands |
| `tests/` | Regression and validation tests |

## 9. Deliverables

- Final report: `docs/final_report.md`
- Final demo runbook: `docs/final_demo_runbook.md`
- Submission checklist: `docs/final_submission_checklist.md`
- Professor grading checklist: `docs/professor_grading_checklist.md`
- API contract: `docs/api_contract.md`
- Model audit: `docs/model_training_audit.md`
- Streaming audits: `docs/spark_structured_streaming_audit.md`, `docs/streaming_scorer_audit.md`
- Recommended slide deck: `presentation/CourtIQ_Final_Presentation_v2.pptx`
- Recommended speaker script: `presentation/speaker_notes_v2.md`
- Presentation index: `presentation/README.md`
- Documentation index: `docs/README.md`

## 10. Limitations

- Point probabilities are analytical model outputs, not betting odds and not match-win probabilities.
- Risk scores are statistical anomaly signals for review only. They do not prove misconduct or match-fixing.
- Surface metadata is unavailable in the curated data, so surface analytics are not claimed.
- Rally length coverage is sparse, so rally-derived features are secondary.
- ATP bridge/ranking data is not validated; official rankings are not claimed.
- The local demo is not a production deployment. It is a reproducible academic demo over local files, Docker Kafka, and Spark where available.
- The full local dashboard scores a bounded 50-match sample for demo performance; the larger replay manifest remains available for catalog/replay evidence.

## 11. Team Contributions

| Team member | Primary contribution area |
| --- | --- |
| Member 1 | Data engineering, cleaning, curated layers, schema validation, and data quality evidence |
| Member 2 | Feature engineering, point-level modeling, evaluation, risk scoring, and model publication |
| Member 3 | Replay/streaming integration, FastAPI service, frontend dashboard, demo runner, and validation automation |

Shared responsibilities included documentation, tests, demo rehearsal, limitations review, and final submission packaging.

## Milestone Compatibility Note

Historical milestone note for the preflight gate: Milestone 4B: PASSED for the FastAPI-backed dashboard/frontend.
