#!/usr/bin/env bash
set -e

BROKER="localhost:9092"

docker exec tennis-kafka kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --create \
  --if-not-exists \
  --topic tennis.point.events \
  --partitions 20 \
  --replication-factor 1 \
  --config retention.ms=86400000

docker exec tennis-kafka kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --create \
  --if-not-exists \
  --topic tennis.point.events.dlq \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=86400000

docker exec tennis-kafka kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --create \
  --if-not-exists \
  --topic tennis.replay.manifest \
  --partitions 20 \
  --replication-factor 1 \
  --config retention.ms=86400000

docker exec tennis-kafka kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --create \
  --if-not-exists \
  --topic tennis.replay.manifest.dlq \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=86400000

docker exec tennis-kafka kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --create \
  --if-not-exists \
  --topic tennis.replay.audit \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=86400000

docker exec tennis-kafka kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --list
