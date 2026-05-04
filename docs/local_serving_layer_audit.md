# Local Serving Layer Audit

## Purpose

Milestone 4A adds a small FastAPI service over validated local scored output so the project has a reliable final demo path before frontend work.

## Data Sources

The service reads:

- `data/results/streaming_scoring/scored_events_sample.jsonl`
- `data/results/streaming_scoring/scoring_run_report.json`
- `data/results/streaming_scoring/scoring_validation_report.json`
- `data/results/streaming_scoring/scoring_benchmark_report.json`
- `data/models/odds/latest.json`
- `data/models/odds/v1/metadata.json`
- `data/models/odds/v1/feature_schema.json`
- `data/models/risk/latest.json`
- `data/models/risk/v1/metadata.json`
- `data/models/risk/v1/risk_config.json`
- model evaluation reports under `data/results/model_eval/`

No database is required.

## Endpoints

The API exposes health, readiness, system summary, scored events, match summaries/details, risk summaries/events, model metadata, and latest benchmark details.

## Validation Status

`scripts/validate_api_contract.py` passes and writes:

```text
data/results/api_validation/api_validation_report.json
data/results/api_validation/sample_responses.json
contracts/api_openapi_snapshot.json
contracts/api_response_examples.json
```

## Why File-Backed Is Acceptable

The deadline requires a reliable demo and report evidence. The scored output sample is small enough to load into memory, and file-backed serving avoids adding PostgreSQL operational risk before the scoring path is demonstrated.

## Limitations

- The API serves a static scored sample and refreshes only on process restart.
- Kafka runtime remains optional and was not required for API validation.
- The risk score is a statistical anomaly signal only, not proof of misconduct.

## Future Upgrade Path

Milestone 4B can build a minimal dashboard using the documented API. Later, a persistence milestone can move scored events into PostgreSQL after the API contract stabilizes.
