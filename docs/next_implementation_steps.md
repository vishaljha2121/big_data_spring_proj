# Next Implementation Steps

## Current Status

- Milestone 1B: **PASSED**
- Milestone 2A: **PASSED**
- Milestone 2.5: **PASSED**
- Milestone 2.6: **PASSED**
- Milestone 2.7: **PASSED**
- Milestone 3B: **VERIFIED PASSED** for local JSONL streaming scorer integration
- Milestone 4A: **PASSED** for local file-backed FastAPI serving layer

## Working Demo Path

The project now has a reliable local demo path:

```text
canonical replay JSONL events
  -> online feature builder
  -> published odds model
  -> published risk config
  -> scored JSONL/Parquet output
  -> file-backed FastAPI service
```

Primary scoring outputs:

```text
data/results/streaming_scoring/scored_events_sample.jsonl
data/results/streaming_scoring/scored_events_sample.parquet
data/results/streaming_scoring/scoring_run_report.json
data/results/streaming_scoring/scoring_validation_report.json
data/results/streaming_scoring/scoring_benchmark_report.json
```

Primary API outputs:

```text
api/app/main.py
contracts/api_openapi_snapshot.json
contracts/api_response_examples.json
data/results/api_validation/api_validation_report.json
data/results/api_validation/sample_responses.json
```

## Next Recommended Milestone

Proceed to:

**Milestone 4B: minimal dashboard/frontend over documented API**

Recommended scope:

- build a minimal dashboard against `docs/api_contract.md`
- show system summary, scored events, match detail, risk summary, and model metadata
- avoid backend architecture changes unless a blocker is found
- keep PostgreSQL/Redis out of scope unless explicitly required

## Blockers

- Kafka runtime has not been executed locally, although dry-run replay and JSONL scoring both pass.
- Risk scoring is conservative and baseline-based; it must not be described as match-fixing detection.
- Surface, rally-primary, and ATP-bridge features remain blocked by data limitations.

## Exact Next Branch

Use:

```text
feature/milestone-4b-minimal-dashboard
```
