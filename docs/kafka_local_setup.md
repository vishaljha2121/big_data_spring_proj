# Kafka Local Setup

## Start Kafka

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
```

## Create Topic

```bash
bash infra/kafka/kafka_setup.sh
```

The setup script reads `infra/kafka/topic_config.json` and creates the canonical topic idempotently.

## Topic Config

- topic: `tennis-point-events`
- partitions: `20`
- replication factor: `1`
- retention: `86400000` ms
- cleanup policy: `delete`
- max message bytes: `1048576`
- partition key: `synthetic_match_id`
- consumer group: `spark-tennis`

## Produce Sample

```bash
.venv/bin/python producer/replay_producer.py \
  --manifest data/replay/manifests/replay_manifest_v1.parquet \
  --config infra/kafka/topic_config.json \
  --bootstrap-servers localhost:9092 \
  --topic tennis-point-events \
  --max-events 1000 \
  --speed 50
```

## Consume Sample

```bash
.venv/bin/python scripts/consume_replay_sample.py \
  --bootstrap-servers localhost:9092 \
  --topic tennis-point-events \
  --max-events 100
```

Kafka was not run during Milestone 2.7 validation in this environment; dry-run validation is the completed evidence.
