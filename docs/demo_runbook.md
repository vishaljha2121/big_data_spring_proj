# Demo Runbook

## 1. Validate Existing Artifacts

```bash
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_replay_producer.py --events data/results/replay_dry_run/sample_events.jsonl --schema contracts/point_event_schema.json
```

## 2. Rerun Local Scoring

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

## 3. Validate Scored Events

```bash
.venv/bin/python scripts/validate_scored_events.py \
  --events data/results/streaming_scoring/scored_events_sample.jsonl \
  --schema contracts/scored_event_schema.json \
  --odds-latest data/models/odds/latest.json \
  --report data/results/streaming_scoring/scoring_validation_report.json \
  --expected-count 1000
```

## 4. Validate API Contract

```bash
.venv/bin/python scripts/validate_api_contract.py
```

## 5. Start API Locally

```bash
.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000
```

## 6. Curl Key Endpoints

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/ready
curl -s http://127.0.0.1:8000/api/summary
curl -s "http://127.0.0.1:8000/api/scored-events?limit=3"
curl -s "http://127.0.0.1:8000/api/matches?limit=3"
curl -s http://127.0.0.1:8000/api/risk/summary
curl -s http://127.0.0.1:8000/api/models/current
curl -s http://127.0.0.1:8000/api/benchmarks/latest
```

## Notes For Presentation

- Point probability means current-point probability, not match-win probability.
- Risk score means statistical anomaly signal for review, not proof of misconduct.
- React/frontend is intentionally not implemented yet.
