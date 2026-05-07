# Streaming Demo Runbook

## Requirement

The Kafka + Spark demo requires:

- Docker Desktop or Docker daemon
- local Kafka container from `infra/docker/docker-compose.kafka.yml`
- Python virtual environment with project requirements
- PySpark and Java runtime
- Spark Kafka connector package availability

## One-Command Streaming Demo

```bash
bash scripts/run_streaming_demo.sh --max-events 1000
```

The script:

1. verifies Docker;
2. starts Kafka Compose;
3. waits for Kafka;
4. creates/verifies the topic;
5. starts Spark Structured Streaming scorer;
6. publishes replay events to Kafka;
7. waits for Spark output;
8. validates scored output;
9. writes runtime reports.

## Manual Commands

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
bash infra/kafka/kafka_setup.sh
.venv/bin/python scripts/validate_kafka_runtime.py
.venv/bin/python scripts/run_kafka_replay_smoke.py --max-events 1000
.venv/bin/python scripts/run_spark_streaming_scorer.py --max-events 1000 --timeout-seconds 60
.venv/bin/python scripts/validate_spark_streaming_output.py --expected-count 1000
```

## Expected Reports

- `data/results/kafka_runtime/kafka_runtime_report.json`
- `data/results/kafka_runtime/kafka_replay_smoke_report.json`
- `data/results/kafka_runtime/kafka_consume_sample_report.json`
- `data/results/spark_streaming/spark_streaming_run_report.json`
- `data/results/spark_streaming/spark_streaming_validation_report.json`

## JSONL Fallback

If Docker, Kafka, Java, PySpark, or Spark Kafka connector resolution is unavailable, use the deterministic local JSONL demo:

```bash
bash scripts/run_full_demo.sh
```

In that case, present Kafka/Spark as implemented but not runtime-executed in the current environment. Do not claim Kafka or Spark passed without the reports above showing `PASSED`.

## Presentation Wording

If runtime reports pass:

> We implemented a real Kafka replay stream and a Spark Structured Streaming scoring job. The local JSONL path remains a deterministic fallback, but this branch adds validated streaming runtime evidence.

Milestone 5A runtime reports passed locally with 1000 Kafka replay events and 1000 Spark-scored events.

If runtime reports do not pass:

> The Kafka/Spark runtime implementation is present, but the local execution environment did not complete runtime validation. The deterministic JSONL scorer remains the validated demo path.
