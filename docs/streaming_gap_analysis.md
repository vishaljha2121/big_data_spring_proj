# Streaming Gap Analysis

## Existing Streaming-Related Pieces

- `producer/replay_producer.py` can serialize canonical replay manifest rows as `point_event_v1` JSON and already supports Kafka publishing mode.
- `infra/docker/docker-compose.kafka.yml` defines a local Kafka broker.
- `infra/kafka/topic_config.json` freezes the canonical topic contract for `tennis-point-events`.
- `infra/kafka/kafka_setup.sh` creates the Kafka topic idempotently.
- `scripts/consume_replay_sample.py` can consume Kafka events and validate them against `contracts/point_event_schema.json`.
- `scripts/run_scoring_from_kafka.py` provides a Python Kafka consumer scoring path.
- `streaming/stream_scorer.py` contains the validated local scorer used by the JSONL path.

## Currently Dry-Run Only

- The validated final demo path uses `data/results/replay_dry_run/sample_events.jsonl`.
- The scored output used by the API comes from local JSONL/Parquet scoring, not a Kafka/Spark runtime.
- Kafka runtime was scaffolded but not part of the prior validation evidence.

## Kafka Runtime Pieces Not Yet Validated

- Docker Compose startup had not been proven in the current environment.
- Topic creation had no dedicated JSON runtime report.
- Replay producer publish + consumer validate had no persisted report.

## Missing Spark Structured Streaming Pieces

- No PySpark Structured Streaming application existed.
- No Kafka source parser existed for Spark.
- No checkpointed Spark streaming scorer existed.
- No Spark streaming output sink or validation report existed.

## Runtime Path Implemented In Milestone 5A

```text
Kafka topic tennis-point-events
  -> canonical replay producer publishes point_event_v1 JSON
  -> Spark Structured Streaming reads Kafka value payloads
  -> foreachBatch scores events through streaming.stream_scorer.StreamScorer
  -> scored events are appended to local JSONL and Parquet sink files
  -> validator checks scored_event_schema, counts, probabilities, risk fields, and duplicate IDs
```

## Out Of Scope

- Frontend redesign
- model retraining
- model feature changes
- PostgreSQL or Redis
- production deployment
- exactly-once production semantics
- changing generated Parquet datasets

Milestone 5A may only be marked PASSED if Kafka and Spark actually execute locally. If Docker, Kafka, Spark, Java, or Spark Kafka connector dependencies are unavailable, the implementation remains in place but the milestone must be marked PARTIAL with exact blockers.
