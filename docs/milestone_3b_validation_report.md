# Milestone 3B Validation Report

## Verdict

Milestone 3B: **PASSED** for the local JSONL streaming scorer path.

## Commands Run

```bash
.venv/bin/python scripts/run_scoring_from_jsonl.py --input-events data/results/replay_dry_run/sample_events.jsonl --odds-latest data/models/odds/latest.json --risk-latest data/models/risk/latest.json --output-jsonl data/results/streaming_scoring/scored_events_sample.jsonl --output-parquet data/results/streaming_scoring/scored_events_sample.parquet --max-events 1000 --report data/results/streaming_scoring/scoring_run_report.json

.venv/bin/python scripts/validate_scored_events.py --events data/results/streaming_scoring/scored_events_sample.jsonl --schema contracts/scored_event_schema.json --odds-latest data/models/odds/latest.json --report data/results/streaming_scoring/scoring_validation_report.json --expected-count 1000

.venv/bin/python scripts/benchmark_scoring_pipeline.py --input-events data/results/replay_dry_run/sample_events.jsonl --odds-latest data/models/odds/latest.json --risk-latest data/models/risk/latest.json --max-events 1000 --report data/results/streaming_scoring/scoring_benchmark_report.json
```

Additional model, replay, feature, parallel-readiness, and pytest validation commands were run after implementation.

## Scoring Result

- Input events: `1000`
- Scored events: `1000`
- Invalid events: `0`
- Defaulted features: `elapsed_seconds_delta_from_prev`
- Missing model features: none
- Output JSONL: `data/results/streaming_scoring/scored_events_sample.jsonl`
- Output Parquet: `data/results/streaming_scoring/scored_events_sample.parquet`

## Benchmark Result

- Events scored: `1000`
- Throughput: `974.13` events/sec
- Average latency: `0.9635` ms/event
- p95 latency: `1.5229` ms/event
- Model load time: `3.2619` seconds

## Kafka Runtime

Kafka scoring code exists in `scripts/run_scoring_from_kafka.py`, but Kafka runtime was not executed for this milestone. The JSONL path is the validated primary demo path.

## Next Milestone Recommendation

Proceed to **Milestone 4A: local serving layer**. Build a small FastAPI or file-backed local API around the validated scored output and published model/risk artifacts. Keep React blocked until an API contract exists.
