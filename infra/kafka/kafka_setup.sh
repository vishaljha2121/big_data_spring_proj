#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-infra/kafka/topic_config.json}"

echo "Milestone 3A scaffold only."
echo "Topic config: ${CONFIG_PATH}"
echo "TODO: create Kafka topic from topic_config.json after docker-compose.kafka.yml is implemented."
echo "This script intentionally does not start Kafka in Milestone 2.5."
