#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-infra/kafka/topic_config.json}"

TOPIC="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["topic"])' "$CONFIG_PATH")"
PARTITIONS="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["partitions"])' "$CONFIG_PATH")"
REPLICATION_FACTOR="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["replication_factor"])' "$CONFIG_PATH")"
RETENTION_MS="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["retention_ms"])' "$CONFIG_PATH")"
CLEANUP_POLICY="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["cleanup_policy"])' "$CONFIG_PATH")"
MAX_MESSAGE_BYTES="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["max_message_bytes"])' "$CONFIG_PATH")"

docker exec tennis-kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --if-not-exists \
  --topic "$TOPIC" \
  --partitions "$PARTITIONS" \
  --replication-factor "$REPLICATION_FACTOR" \
  --config "retention.ms=$RETENTION_MS" \
  --config "cleanup.policy=$CLEANUP_POLICY" \
  --config "max.message.bytes=$MAX_MESSAGE_BYTES"

docker exec tennis-kafka kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic "$TOPIC"
