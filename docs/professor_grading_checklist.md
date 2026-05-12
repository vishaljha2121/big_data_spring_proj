# Professor Grading Checklist

## Quick Verification

- [ ] Demo runs with `scripts/run_full_demo.sh`
- [ ] API docs visible at `/docs`
- [ ] Frontend visible at `localhost:5173`
- [ ] Big Data scope shown in root `README.md`
- [ ] Kafka/Spark evidence documented
- [ ] Model metrics documented
- [ ] Limitations stated honestly
- [ ] Presentation files available
- [ ] Final report available

## Commands To Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_full_demo.sh
```

Open:

- `http://127.0.0.1:5173`
- `http://127.0.0.1:8000/docs`

## What To Click During Demo

1. **Dashboard** - confirm top KPIs, data coverage, model quality, and validation summaries.
2. **Match Browser** - inspect scored matches and full replay catalog browsing.
3. **Replay Center** - play, pause, step forward/back, and show point-by-point replay.
4. **Point Timeline** - inspect per-point probability movement and risk buckets.
5. **Prediction Center** - show point-level scoring language, not betting or match-winner claims.
6. **Model Performance** - show AUC, Brier score, model type, feature count, and comparison caveats.
7. **Validation** - show evidence status and validation artifacts.
8. **Pipeline Monitor** - show data/API/scoring pipeline health and runtime evidence.

## Evidence To Check In Repo

| Evidence | Path |
| --- | --- |
| Final report | `docs/final_report.md` |
| Demo runbook | `docs/final_demo_runbook.md` |
| API contract | `docs/api_contract.md` |
| Documentation index | `docs/README.md` |
| Presentation index | `presentation/README.md` |
| Recommended slides | `presentation/CourtIQ_Final_Presentation_v2.pptx` |
| Speaker script | `presentation/speaker_notes_v2.md` |
| Final preflight report | `data/results/final_demo/final_preflight_report.json` |
| Smoke-test report | `data/results/final_demo/full_demo_smoke_report.json` |
| API validation | `data/results/api_validation/api_validation_report.json` |
| Frontend validation | `data/results/frontend_validation/frontend_validation_report.json` |
| Model validation | `data/results/model_eval/model_artifact_validation_report.json` |
| Feature validation | `data/features/validation_report.json` |
| Kafka runtime report | `data/results/kafka_runtime/kafka_runtime_report.json` |
| Spark validation report | `data/results/spark_streaming/spark_streaming_validation_report.json` |

## Limitations To Confirm Are Stated

- Point probabilities are not betting odds.
- Point probabilities are not match-win probabilities.
- Risk scores do not prove misconduct or match-fixing.
- Surface analytics are not claimed.
- Official ATP rankings are not claimed.
- The local demo is not a production deployment.

## Optional Streaming Verification

Only run when Docker, Java, PySpark, and Spark Kafka dependencies are available:

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
bash infra/kafka/kafka_setup.sh
bash scripts/run_streaming_demo.sh --max-events 1000
```

If this environment cannot run Docker or Spark, use the checked-in reports under `data/results/kafka_runtime/` and `data/results/spark_streaming/` as prior local execution evidence.
