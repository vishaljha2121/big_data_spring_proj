# Kafka Runtime Validation

## Purpose

Milestone 5A adds real Kafka runtime validation around the existing canonical replay producer. Prior milestones had a Kafka mode, Docker Compose file, and topic setup, but the validated demo path remained JSONL-based.

## Runtime Commands

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
bash infra/kafka/kafka_setup.sh
.venv/bin/python scripts/validate_kafka_runtime.py
.venv/bin/python scripts/run_kafka_replay_smoke.py --max-events 1000
```

## Topic Contract

- topic: `tennis-point-events`
- partitions: `20`
- replication factor: `1`
- partition key: `synthetic_match_id`
- consumer group: `spark-tennis`

## Reports

- `data/results/kafka_runtime/kafka_runtime_report.json`
- `data/results/kafka_runtime/kafka_replay_smoke_report.json`
- `data/results/kafka_runtime/kafka_consume_sample_report.json`

## Milestone 5A Result

- Docker daemon: available
- Kafka image: `apache/kafka:3.7.0`
- Topic validation: PASSED
- Partition count: `20`
- Replay events produced: `1000`
- Replay events consumed and schema-validated: `1000`
- Missing synthetic match IDs: `0`
- Duplicate synthetic event IDs in consumed sample: `0`

## Honest Status Rule

Kafka is only reported as runtime-passed when Docker is available, the `tennis-kafka` container is running, the topic exists with the expected partition count, the replay producer publishes events, and the consumer validates those Kafka events against `contracts/point_event_schema.json`.

If Docker or Kafka is unavailable, the report must say `NOT_EXECUTED` or `FAILED`; the project should continue to use the deterministic JSONL path for the local demo.
