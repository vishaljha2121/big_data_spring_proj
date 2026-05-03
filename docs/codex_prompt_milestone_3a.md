# Codex Prompt: Milestone 3A Replay / Kafka Infra Track

You are working on branch `feature/milestone-3a-replay-producer` in `vishaljha2121/big_data_spring_proj`.

Implement Milestone 3A only: local Kafka setup, topic creation, replay producer, validation consumer, and replay audit docs.

Allowed inputs:

- `data/replay/manifests/replay_manifest_v1.parquet`
- `data/replay/replay_manifest_report.json`
- `contracts/point_event_schema.json`
- `contracts/replay_manifest_schema.json`
- `infra/kafka/topic_config.json`

Do not train models. Do not implement Spark Structured Streaming, FastAPI, React, PostgreSQL serving, or frontend work. Do not modify generated feature/baseline/replay Parquet data.

Required outputs:

- `producer/replay_producer.py`
- `producer/config.py`
- `infra/kafka/kafka_setup.sh`
- `infra/kafka/topic_config.json`
- `infra/docker/docker-compose.kafka.yml`
- `scripts/validate_replay_manifest.py`
- `scripts/validate_replay_producer.py`
- `scripts/consume_replay_sample.py`
- `docs/replay_producer_audit.md`
- `docs/kafka_local_setup.md`
- `docs/event_contract_handoff.md`
- replay/Kafka tests under `tests/`

Contracts to obey:

- Kafka topic: `infra/kafka/topic_config.json`
- Kafka event schema: `contracts/point_event_schema.json`
- Replay manifest schema: `contracts/replay_manifest_schema.json`

Success gates:

- local Kafka starts only when explicitly run
- topic config validates
- replay producer emits schema-valid JSON events
- partition key is `synthetic_match_id`
- replay order is monotonic within `synthetic_match_id`
- malformed events go to a dead-letter path/topic
- Spark streaming is not started

Run:

```bash
.venv/bin/python scripts/validate_replay_manifest.py
.venv/bin/python scripts/validate_replay_producer.py
.venv/bin/python -m pytest tests
```

Return PASSED/PARTIAL/FAILED with replay counts and validation results.
