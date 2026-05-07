# Final Project Status

## Verdict

The project has a validated local end-to-end demo path from curated tennis point data to model-scored events, a file-backed API, a presentation-ready tennis dashboard, and final preflight/demo launcher scripts.

Milestone 4F pivots the frontend into a Centre Court Analytics product shell with grouped sidebar navigation, multiple analytics/replay/model/data-ops pages, and clear real-versus-planned module labeling.

Milestone 5A adds Kafka runtime validation scripts and a Spark Structured Streaming scorer implementation. It executed locally with Kafka runtime, replay publish/consume validation, Spark Structured Streaming scoring, checkpointing, and scored output validation all showing `PASSED`.

## Completed Milestones

- Milestone 1B: cleaned/curated data layer
- Milestone 2A: point-in-time features, baselines, replay manifest
- Milestone 2.5: parallel readiness and contract freeze
- Milestone 2.6: CourtIQ audit/preservation
- Milestone 2.7: model artifacts and replay/Kafka dry-run
- Milestone 3B: local JSONL streaming scorer
- Milestone 4A: file-backed FastAPI serving layer
- Milestone 4B: minimal dashboard/frontend
- Milestone 4C: final build freeze, preflight, smoke test, and one-command demo
- Milestone 4D: frontend presentation redesign and demo polish
- Milestone 4E: final frontend narrative polish and model comparison context
- Milestone 4F: Centre Court Analytics product pivot over the existing API
- Milestone 5A: Kafka + Spark Structured Streaming runtime completion

## Demo Path

```text
replay JSONL
  -> online feature builder
  -> odds model
  -> risk config
  -> scored JSONL/Parquet
  -> FastAPI
  -> React dashboard
```

## Key Evidence

- Scored events: `1000`
- API match count: `6`
- Odds model: `v1`
- Risk config: `v1`
- Frontend build: see `data/results/frontend_validation/frontend_validation_report.json`
- Frontend theme system: clay, hard, grass, neutral
- Frontend product shell: Analytics, Replay, ML Model, and Data Ops navigation groups
- Streaming runtime path: Kafka `tennis-point-events` to Spark Structured Streaming foreachBatch scorer to local JSONL/Parquet sink
- Kafka events produced/validated: `1000`
- Spark events scored/validated: `1000`
- Spark checkpoint: `data/checkpoints/spark_streaming_scorer/`
- Backend validation: see `data/results/api_validation/api_validation_report.json`
- Final preflight: see `data/results/final_demo/final_preflight_report.json`
- Demo smoke test: see `data/results/final_demo/full_demo_smoke_report.json`

## One-Command Demo

```bash
bash scripts/run_full_demo.sh
```

Open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:5173`

## Limitations

- Probabilities are point-level probabilities only.
- Risk scores are statistical anomaly signals for review only.
- Surface analytics and official rankings are not claimed; those modules are clearly marked blocked or sample-derived.
- Kafka runtime is optional for the current demo and was not required.
- Kafka/Spark runtime was executed locally for Milestone 5A; production deployment is still out of scope.
- No PostgreSQL, Redis, or production deployment is included.
