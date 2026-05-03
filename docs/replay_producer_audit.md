# Replay Producer Audit

## Verdict

Milestone 2.7 replay producer implementation passed dry-run validation. Kafka runtime code and local setup files are implemented, but Kafka was not executed in this environment.

## Input

The producer reads only:

- `data/replay/manifests/replay_manifest_v1.parquet`

It does not use staging CSVs, raw CSVs, CourtIQ data, or model feature rows.

## Event Contract

Every dry-run event validates against:

- `contracts/point_event_schema.json`

The emitted event is a raw replay point event and intentionally excludes model features.

## Dry-Run Result

Command:

```bash
.venv/bin/python producer/replay_producer.py \
  --manifest data/replay/manifests/replay_manifest_v1.parquet \
  --config infra/kafka/topic_config.json \
  --dry-run \
  --dry-run-output data/results/replay_dry_run/sample_events.jsonl \
  --max-events 1000
```

Result:

- events written: `1000`
- validation: PASSED
- unique synthetic event ids: `1000`

## Kafka Runtime Status

Kafka runtime was not executed locally. No Kafka success is claimed.

Kafka mode is implemented through `kafka-python` and can be run after starting the local Compose stack.
