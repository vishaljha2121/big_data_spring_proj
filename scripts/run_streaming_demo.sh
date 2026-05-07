#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MAX_EVENTS=1000
TIMEOUT_SECONDS=60
SKIP_DOCKER_UP=0
KEEP_KAFKA_RUNNING=0
SPARK_PID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-events) MAX_EVENTS="$2"; shift 2 ;;
    --timeout-seconds) TIMEOUT_SECONDS="$2"; shift 2 ;;
    --skip-docker-up) SKIP_DOCKER_UP=1; shift ;;
    --keep-kafka-running) KEEP_KAFKA_RUNNING=1; shift ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

cleanup() {
  if [[ -n "${SPARK_PID}" ]] && kill -0 "$SPARK_PID" >/dev/null 2>&1; then
    kill "$SPARK_PID" >/dev/null 2>&1 || true
    wait "$SPARK_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$KEEP_KAFKA_RUNNING" -eq 0 && "$SKIP_DOCKER_UP" -eq 0 ]]; then
    docker compose -f infra/docker/docker-compose.kafka.yml down >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for Kafka runtime and is not available." >&2
  exit 2
fi
docker info >/dev/null

if [[ "$SKIP_DOCKER_UP" -eq 0 ]]; then
  docker compose -f infra/docker/docker-compose.kafka.yml up -d
fi

echo "Waiting for Kafka container..."
for _ in {1..45}; do
  if docker exec tennis-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

bash infra/kafka/kafka_setup.sh
.venv/bin/python scripts/validate_kafka_runtime.py

rm -rf data/results/spark_streaming data/checkpoints/spark_streaming_scorer
mkdir -p data/results/spark_streaming

echo "Starting Spark Structured Streaming scorer..."
.venv/bin/python scripts/run_spark_streaming_scorer.py \
  --bootstrap-servers localhost:9092 \
  --topic tennis-point-events \
  --odds-latest data/models/odds/latest.json \
  --risk-latest data/models/risk/latest.json \
  --output-dir data/results/spark_streaming \
  --checkpoint-dir data/checkpoints/spark_streaming_scorer \
  --max-events "$MAX_EVENTS" \
  --timeout-seconds "$TIMEOUT_SECONDS" &
SPARK_PID="$!"

sleep 8

echo "Publishing replay sample to Kafka..."
.venv/bin/python producer/replay_producer.py \
  --manifest data/replay/manifests/replay_manifest_v1.parquet \
  --config infra/kafka/topic_config.json \
  --bootstrap-servers localhost:9092 \
  --topic tennis-point-events \
  --max-events "$MAX_EVENTS" \
  --speed 0

wait "$SPARK_PID"
SPARK_PID=""

.venv/bin/python scripts/validate_spark_streaming_output.py \
  --output-dir data/results/spark_streaming \
  --schema contracts/scored_event_schema.json \
  --expected-count "$MAX_EVENTS"

echo "Streaming demo completed."
echo "Kafka runtime report: data/results/kafka_runtime/kafka_runtime_report.json"
echo "Spark run report: data/results/spark_streaming/spark_streaming_run_report.json"
echo "Spark validation report: data/results/spark_streaming/spark_streaming_validation_report.json"
