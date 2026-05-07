# Spark Structured Streaming Audit

## Architecture

```text
data/replay/manifests/replay_manifest_v1.parquet
  -> producer/replay_producer.py
  -> Kafka topic tennis-point-events
  -> Spark Structured Streaming readStream Kafka source
  -> foreachBatch scoring adapter
  -> streaming.stream_scorer.StreamScorer
  -> data/results/spark_streaming/scored_events_jsonl/
  -> data/results/spark_streaming/scored_events_parquet/
  -> data/checkpoints/spark_streaming_scorer/
```

## Kafka Source

The Spark job reads Kafka using:

- `format("kafka")`
- `kafka.bootstrap.servers=localhost:9092`
- `subscribe=tennis-point-events`
- `startingOffsets=earliest`

The Kafka value is cast to string and parsed as canonical `point_event_v1` JSON.

## Structured Streaming Job

The entrypoint is:

```bash
.venv/bin/python scripts/run_spark_streaming_scorer.py \
  --bootstrap-servers localhost:9092 \
  --topic tennis-point-events \
  --max-events 1000 \
  --timeout-seconds 60
```

The implementation uses `foreachBatch` rather than Spark UDF model scoring. This keeps model loading and online feature state in the driver-side micro-batch adapter, reusing the already validated Python scorer.

## Checkpointing

Checkpoint path:

```text
data/checkpoints/spark_streaming_scorer/
```

Checkpointing is used for local Structured Streaming progress tracking. The local file sink is append-oriented and intended for demo validation, not production exactly-once guarantees.

## Model Loading

The Spark adapter loads:

- `data/models/odds/latest.json`
- `data/models/risk/latest.json`

through `streaming.stream_scorer.StreamScorer`, which internally uses the existing model loader, online feature builder, and risk scorer.

## Output Sink

Outputs:

- JSONL: `data/results/spark_streaming/scored_events_jsonl/part-00000.jsonl`
- Parquet batches: `data/results/spark_streaming/scored_events_parquet/batch-*.parquet`
- Run report: `data/results/spark_streaming/spark_streaming_run_report.json`
- Validation report: `data/results/spark_streaming/spark_streaming_validation_report.json`

## Validation

The validator checks:

- scored output exists
- expected event count is present
- `contracts/scored_event_schema.json` compliance
- probability and risk score ranges
- risk bucket validity
- valid input and feature flags
- no duplicate `synthetic_event_id`
- checkpoint directory existence
- JSONL and Parquet readability

## Milestone 5A Result

- Source topic: `tennis-point-events`
- Spark mode: local Structured Streaming with Kafka source
- Scoring adapter: `foreachBatch`
- Scored events: `1000`
- Invalid events: `0`
- JSONL output: `data/results/spark_streaming/scored_events_jsonl/part-00000.jsonl`
- Parquet output: `data/results/spark_streaming/scored_events_parquet/batch-000000.parquet`
- Checkpoint path: `data/checkpoints/spark_streaming_scorer/`
- Run report: `data/results/spark_streaming/spark_streaming_run_report.json`
- Validation report: `data/results/spark_streaming/spark_streaming_validation_report.json`
- Validation status: PASSED

## Limitations

- This is a local course/demo Structured Streaming implementation.
- `foreachBatch` scoring is intentionally pragmatic and not a high-throughput production design.
- Spark Kafka connector resolution may require network access for Maven packages.
- Kafka/Spark runtime is not claimed as passed unless the scripts actually execute.
- The existing JSONL path remains the deterministic fallback.
