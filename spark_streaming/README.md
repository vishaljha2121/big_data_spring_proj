# Spark Structured Streaming Scorer

This package contains the local Spark Structured Streaming path for Milestone 5A.

```text
Kafka topic tennis-point-events
  -> Spark readStream Kafka source
  -> foreachBatch parser
  -> streaming.stream_scorer.StreamScorer
  -> JSONL and Parquet local sinks
  -> checkpoint directory
```

The implementation intentionally uses `foreachBatch` so the existing validated Python model loader, online feature builder, and risk scorer can be reused without distributed model-loading complexity.

Run through:

```bash
.venv/bin/python scripts/run_spark_streaming_scorer.py \
  --bootstrap-servers localhost:9092 \
  --topic tennis-point-events \
  --max-events 1000 \
  --timeout-seconds 60
```

This requires PySpark, Java, Docker Kafka, and the Spark Kafka connector package.

