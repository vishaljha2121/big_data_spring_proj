# Parallel Workstream Handoff

## Current Status

Milestone 1B and Milestone 2A are complete and validated. Milestone 2.5 freezes contracts and workstream boundaries so two team members can proceed independently.

Milestone 2B model artifacts are not implemented in this handoff. Milestone 3A Kafka replay is not implemented in this handoff.

## Stable Inputs

- `data/features/point_features/`
- `data/features/match_features/`
- `data/baselines/player_baselines/`
- `data/replay/manifests/replay_manifest_v1.parquet`
- `data/features/feature_quality_report.json`
- `data/features/validation_report.json`
- `data/baselines/baseline_quality_report.json`
- `data/replay/replay_manifest_report.json`
- `contracts/`

Do not use staging CSV.GZ files directly.

## Frozen Contracts

- `contracts/point_event_schema.json`
- `contracts/replay_manifest_schema.json`
- `contracts/odds_model_metadata_schema.json`
- `contracts/odds_model_feature_schema.json`
- `contracts/risk_model_metadata_schema.json`
- `contracts/risk_config_schema.json`
- `contracts/model_registry_schema.json`
- `contracts/model_eval_report_schema.json`
- `contracts/replay_producer_config_schema.json`
- `contracts/kafka_topic_config_schema.json`
- `contracts/parallel_workstream_handoff_schema.json`

## Workstream A: Model Artifact Track

### Owner Responsibilities

- Train the odds model from `data/features/point_features/`.
- Create risk scoring config from point features and player baselines.
- Evaluate odds and risk artifacts.
- Publish artifacts through staging to `v1`.
- Write `latest.json` only after validation passes.
- Implement fixture scoring and model artifact validation.
- Write model audit docs.

### Allowed Files

- `scripts/train_odds_model.py`
- `scripts/train_risk_model.py`
- `scripts/publish_model.py`
- `scripts/validate_model_artifacts.py`
- `scripts/score_fixture.py`
- `data/models/`
- `data/results/model_eval/`
- `docs/model_training_audit.md`
- `docs/model_feature_selection.md`
- `docs/model_publication_audit.md`
- `docs/risk_scoring_methodology.md`
- model tests under `tests/test_model_*.py` and `tests/test_odds_model_training.py`

### Forbidden Files

- `data/curated/`
- `data/features/point_features/`
- `data/features/match_features/`
- `data/baselines/player_baselines/`
- `data/replay/manifests/replay_manifest_v1.parquet`
- `producer/`
- `infra/kafka/`
- `infra/docker/docker-compose.kafka.yml`

### Required Outputs

Track A must produce the `data/models/`, `data/results/model_eval/`, docs, scripts, and tests listed in `docs/codex_prompt_milestone_2b.md`.

### Validation Commands

```bash
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python -m pytest tests
```

### Success Gate

Odds and risk `latest.json` files exist only after real artifacts validate. Match split must have no leakage. Odds gates must pass or the milestone is marked PARTIAL/FAILED without publishing latest.

## Workstream B: Replay / Kafka Infra Track

### Owner Responsibilities

- Implement local Kafka setup.
- Create Kafka topic from frozen config.
- Implement replay producer from `replay_manifest_v1.parquet`.
- Serialize raw point replay events following `contracts/point_event_schema.json`.
- Implement replay speed control.
- Implement validation consumer.
- Handle malformed events and dead-letter behavior.
- Write replay producer audit docs.

### Allowed Files

- `producer/`
- `infra/kafka/`
- `infra/docker/docker-compose.kafka.yml`
- `scripts/validate_replay_manifest.py`
- `scripts/validate_replay_producer.py`
- `scripts/consume_replay_sample.py`
- `docs/replay_producer_audit.md`
- `docs/kafka_local_setup.md`
- `docs/event_contract_handoff.md`
- replay/Kafka tests under `tests/test_replay_*` and `tests/test_kafka_event_contract.py`

### Forbidden Files

- `data/curated/`
- `data/features/`
- `data/baselines/`
- `data/models/`
- `data/results/model_eval/`
- model training scripts
- model metadata contracts unless coordinated with Track A

### Required Outputs

Track B must produce the Kafka/replay files listed in `docs/codex_prompt_milestone_3a.md`.

### Validation Commands

```bash
.venv/bin/python scripts/validate_replay_manifest.py
.venv/bin/python scripts/validate_replay_producer.py
.venv/bin/python -m pytest tests
```

### Success Gate

Replay producer emits contract-valid JSON events in manifest order to `tennis-point-events`; validation consumer confirms ordering and dead-letter behavior without starting Spark streaming.

## Branch Strategy

- Track A: `feature/milestone-2b-model-artifacts`
- Track B: `feature/milestone-3a-replay-producer`

## Merge Order

1. Merge model artifacts branch after validation passes.
2. Merge replay producer branch after validation passes.
3. Start integration branch `feature/milestone-3b-streaming-scorer`.

## Integration Point

The integration point is a future streaming scorer that reads Kafka raw point events, derives/joins feature state, loads `data/models/*/latest.json`, and emits scored records. Do not implement this in Track A or Track B.

## Files That Must Not Be Modified Without Team Agreement

- `contracts/point_event_schema.json`
- `contracts/replay_manifest_schema.json`
- `contracts/model_registry_schema.json`
- `contracts/odds_model_feature_schema.json`
- `data/features/`
- `data/baselines/`
- `data/replay/manifests/replay_manifest_v1.parquet`
- `README.md`
- `CODEX.md`

## Known Blockers and Limitations

- Surface metadata is unavailable.
- Rally length is sparse and not a primary MVP feature.
- ATP bridge is not validated.
- Model features must not leak labels or identifiers.
- Kafka replay emits raw point events only, not model features.

## Exact Next Prompts for Codex

- Track A prompt: `docs/codex_prompt_milestone_2b.md`
- Track B prompt: `docs/codex_prompt_milestone_3a.md`
