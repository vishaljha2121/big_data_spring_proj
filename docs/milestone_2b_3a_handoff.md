# Milestone 2B / 3A Handoff

## Status

Milestone 2.7 produced both model artifacts and replay producer implementation.

## Model Artifacts

Odds model:

- latest pointer: `data/models/odds/latest.json`
- artifact: `data/models/odds/v1/model.joblib`
- metadata: `data/models/odds/v1/metadata.json`
- feature schema: `data/models/odds/v1/feature_schema.json`

Risk config:

- latest pointer: `data/models/risk/latest.json`
- config: `data/models/risk/v1/risk_config.json`
- metadata: `data/models/risk/v1/metadata.json`

## Replay Producer

- producer: `producer/replay_producer.py`
- dry-run output: `data/results/replay_dry_run/sample_events.jsonl`
- validator: `scripts/validate_replay_producer.py`
- Kafka topic config: `infra/kafka/topic_config.json`

## Future Milestone 3B Connection

Milestone 3B must connect:

```text
Kafka event -> online feature builder -> odds model -> risk scorer -> scored event output
```

Milestone 3B should first write scored output to local JSONL or Parquet. It should not build FastAPI, PostgreSQL serving, or React frontend yet.

## Loader Expectations

The streaming scorer must:

- read `data/models/odds/latest.json`
- load the referenced `model.joblib`
- load the referenced odds `feature_schema.json`
- reject inference rows missing the frozen feature columns
- read `data/models/risk/latest.json`
- load the referenced risk config
- emit scored events with probability and risk fields
