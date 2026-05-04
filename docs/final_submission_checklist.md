# Final Submission Checklist

## Code Validation

- [x] Cleaned/curated Parquet data layer
- [x] Point-in-time-safe feature layer
- [x] Player baselines
- [x] Replay manifest
- [x] MVP odds model artifact
- [x] Conservative risk config
- [x] Replay producer dry-run
- [x] JSONL streaming scorer
- [x] File-backed FastAPI service
- [x] Minimal dashboard/frontend
- [x] Final preflight checker
- [x] One-command demo runner

Run before submission:

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

## Demo Validation

- [x] `bash scripts/run_full_demo.sh` starts API and frontend.
- [x] API health and readiness endpoints are checked before opening the dashboard.
- [x] Logs are written to `data/results/final_demo/logs/`.
- [x] Remaining demo processes can be stopped with `bash scripts/stop_full_demo.sh`.

## Screenshots Needed

- [ ] Dashboard status and summary cards
- [ ] Scored events table
- [ ] Match detail probability timeline
- [ ] Risk summary
- [ ] Model metadata panel
- [ ] Benchmark panel
- [ ] FastAPI `/docs`
- [ ] Terminal showing final validation pass

## Report Sections Needed

- [ ] Data cleaning and curated layer
- [ ] Point-in-time feature engineering
- [ ] Model training and evaluation
- [ ] Replay and scoring pipeline
- [ ] Local API serving layer
- [ ] Dashboard and final demo
- [ ] Limitations and future work

## Slides Needed

- [ ] Problem and project goal
- [ ] Architecture diagram
- [ ] Data and validation evidence
- [ ] Model and risk methodology
- [ ] Demo screenshots
- [ ] Results and limitations
- [ ] Future work

## Known Limitations

- Kafka runtime is optional for the local final demo and was not required.
- The API and dashboard are file-backed over the current validated scored sample.
- Surface, rally-primary, and ATP bridge features remain blocked by data limitations.
- Risk scores are statistical review signals only.
- Point probabilities are not betting odds and not match-win probabilities.
- `npm audit` reports dependency advisories in the lightweight Vite 2 toolchain; this is documented for the local demo and should be handled before any production deployment.

## Final Git Commands

```bash
git status --short
git add README.md CODEX.md api scripts docs frontend tests data/results contracts
git commit -m "Finalize demo build freeze and dashboard readiness"
git push origin feature/milestone-4c-final-build-freeze
```

Open or merge a PR only after the final validation commands pass.
