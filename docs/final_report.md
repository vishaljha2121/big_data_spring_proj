# Final Report: Centre Court Analytics

## 1. Executive Overview

Centre Court Analytics is an end-to-end tennis Big Data analytics system built for a local academic demo. The project starts with historical point-level match data, validates and curates it into structured data layers, builds point-in-time-safe features, trains a point-level probability model, replays historical points as events, scores those events, serves the output through FastAPI, and presents it in a React dashboard.

The final product is intentionally honest about scope. It demonstrates a scalable architecture and validated local execution path, but it does not claim betting odds, match-fixing detection, official rankings, or production deployment.

The main demo command is:

```bash
bash scripts/run_full_demo.sh
```

This launches the local API at `http://127.0.0.1:8000`, API documentation at `http://127.0.0.1:8000/docs`, and the dashboard at `http://127.0.0.1:5173`.

## 2. Data Engineering and Big Data Scope

The project satisfies Big Data scope through both dataset scale and system architecture. The curated data layer contains 1,922,136 singles point rows and 10,508 curated singles matches. The replay layer contains 1,917,672 replay events across 10,464 replay matches. These artifacts are organized under `data/` into curated, feature, baseline, replay, model, and result layers.

The data engineering path uses schema contracts and validation reports to make the pipeline reviewable:

- Curated point and match layers under `data/curated/`
- Point-in-time feature layer under `data/features/`
- Player baselines under `data/baselines/`
- Replay manifest under `data/replay/manifests/`
- JSON schemas under `contracts/`
- Machine-readable validation evidence under `data/results/`

The feature design avoids leakage by using prior state for point-level scoring. Known data limitations are preserved rather than hidden: surface metadata is unavailable, rally-length coverage is sparse, and ATP-derived ranking/bridge features are not validated.

## 3. Modeling, Replay, and Streaming

The published model predicts `label_point_winner_is_player_a`, meaning whether Player A wins the current point. The selected model is a scikit-learn `HistGradientBoostingClassifier` with 26 point-in-time-safe features. The validated test AUC is 0.6415 and the test Brier score is 0.2347.

The model is a point-level analytical model, not a betting model and not a match-winner model. The risk layer is also intentionally conservative: it produces statistical anomaly review signals using baseline-deviation logic, not proof of misconduct or match-fixing.

Replay is implemented through deterministic point events generated from the replay manifest. The local JSONL path is the reliable fallback for demo reproducibility. The Big Data streaming path was also implemented and validated with Kafka and Spark Structured Streaming:

```text
replay manifest
  -> producer
  -> Kafka topic tennis-point-events
  -> Spark Structured Streaming readStream
  -> foreachBatch scorer
  -> JSONL/Parquet scored output
  -> validation report
```

Milestone 5A evidence shows Kafka and Spark processing 1,000 events with validation status `PASSED`. The Spark path uses checkpointing under `data/checkpoints/spark_streaming_scorer/`. This is a local course/demo implementation, not a production exactly-once streaming deployment.

## 4. Serving Layer, Product Interface, and Validation

The serving layer is a file-backed FastAPI application over validated scored output. It exposes health/readiness checks, summary metrics, scored events, match summaries, risk summaries, model metadata, benchmark evidence, data coverage, observability, and replay catalog endpoints. The API contract is documented in `docs/api_contract.md`, with OpenAPI and response examples under `contracts/`.

The frontend is a Vite/React dashboard organized as a Centre Court Analytics product shell. The main views for grading are:

- Dashboard
- Match Browser
- Replay Center
- Point Timeline
- Prediction Center
- Model Performance
- Validation
- Pipeline Monitor

The full demo currently serves 9,049 scored events across 50 matches for responsive local review. The broader replay catalog remains available as evidence of the 10,464-match replay manifest. Unsupported product pages are labeled planned or sample-derived rather than presented as official data integrations.

Validation is automated through scripts:

```bash
.venv/bin/python scripts/final_preflight_check.py
.venv/bin/python scripts/smoke_test_full_demo.py
.venv/bin/python scripts/validate_api_contract.py
.venv/bin/python scripts/validate_frontend_build.py
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_feature_layer.py --curated data/curated --features data/features --baselines data/baselines --replay data/replay --contracts contracts
.venv/bin/python -m pytest tests
```

## 5. Evaluation, Difficulties, Limitations, and Final Readiness

The strongest evaluation evidence is the combination of data validation, model metrics, replay validation, streaming reports, API validation, frontend build validation, smoke tests, and pytest coverage. The final preflight and smoke-test scripts are designed to let a reviewer verify the repository quickly without reading every historical milestone document.

Important difficulties shaped the implementation:

- Surface metadata was unavailable, so surface analytics are not claimed.
- Rally-length coverage was sparse, so rally features are secondary.
- Point-level feature leakage was a real risk, so feature construction and model publication were constrained.
- Kafka/Spark execution introduced local environment dependencies, so the JSONL path remains the deterministic fallback.
- The dashboard product shell needed to be polished without implying unsupported official rankings, tournament data, or betting outputs.

Limitations:

- Point probabilities are not betting odds.
- Point probabilities are not match-win probabilities.
- Risk scores do not prove misconduct or match-fixing.
- Official ATP rankings are not claimed.
- Surface analytics are not claimed because surface coverage is unavailable.
- The local demo is not production deployment.
- The full demo scores a bounded 50-match sample for responsiveness, while the larger replay manifest remains available for catalog evidence.

Final readiness verdict: the repository is professor-ready as a local, validated Big Data analytics project. The root `README.md`, `docs/README.md`, `docs/professor_grading_checklist.md`, `docs/final_demo_runbook.md`, and `presentation/README.md` provide the intended 5-10 minute review path.
