# Tennis Point-Level Analytics Project

This repository contains the validated data, model artifact, and replay foundation for a tennis point-level analytics pipeline. Milestone 2.7 adds real MVP model artifacts and a canonical replay producer dry-run path.

## Current Status

- Milestone 1B: PASSED
- Milestone 2A: PASSED
- Milestone 2.5: PASSED after running `scripts/validate_parallel_readiness.py`
- Milestone 2.6: PASSED after CourtIQ integration audit and guardrail validation
- Milestone 2.7: PASSED for model artifacts and replay dry-run validation
- Milestone 2B: PASSED as part of Milestone 2.7
- Milestone 3A: PASSED for dry-run replay implementation; Kafka runtime was not executed locally

## Completed Checklist

- [x] Converted staging CSV.GZ inputs into cleaned Parquet layers.
- [x] Built curated singles-only point data under `data/curated/singles_points/`.
- [x] Built curated singles match metadata under `data/curated/singles_matches/`.
- [x] Preserved invalid/special point evidence under `data/quarantine/`.
- [x] Built point-in-time-safe features under `data/features/point_features/`.
- [x] Built match features under `data/features/match_features/`.
- [x] Built player baselines under `data/baselines/player_baselines/`.
- [x] Built deterministic replay manifest under `data/replay/manifests/replay_manifest_v1.parquet`.
- [x] Added validation reports, schema contracts, tests, and audit docs through Milestone 2A.
- [x] Froze Track A and Track B contracts for parallel implementation.
- [x] Added paste-ready Codex prompts for both tracks.
- [x] Audited CourtIQ teammate repo and preserved compatible reference assets under `external_review/courtiq/`.
- [x] Trained and published an MVP odds model under `data/models/odds/v1/`.
- [x] Built and published a conservative risk config under `data/models/risk/v1/`.
- [x] Implemented canonical replay JSONL dry-run producer and validator.
- [x] Added local Kafka Compose and topic setup files.

## Remaining Checklist

- [ ] Milestone 3B: integrate streaming scorer using Kafka point events and published model artifacts.
- [ ] Do not start FastAPI, React, PostgreSQL serving, or frontend work until streaming scorer writes scored output.

## Key Findings So Far

- Curated singles point rows: `1,922,136`.
- Curated singles matches: `10,508`.
- Point feature rows: `1,922,136`.
- Match feature rows: `10,508`.
- Player baselines: `1,891`.
- Replay manifest events: `1,917,672`.
- Replay manifest matches: `10,464`.
- Replay exclusions: `44` matches.
- Surface coverage is `0.0%`; surface-based features remain blocked.
- Rally length coverage is about `5.96%`; rally length is not a primary MVP feature.
- ATP bridge remains unvalidated; ATP-derived labels/features remain blocked.
- CourtIQ had useful replay/Kafka reference code, but it did not contain model code or frontend assets.
- CourtIQ replay code is not canonical yet because it requires adaptation to frozen contracts and topic config.
- Published odds model target: `label_point_winner_is_player_a`.
- Published odds model type: `HistGradientBoostingClassifier`.
- Odds validation/test AUC: `0.6395` / `0.6415`.
- Odds validation/test Brier score: `0.2351` / `0.2347`.
- Risk artifact uses baseline deviation rules with `fake_labels_used=false`.
- Replay dry-run validation passed for `1000` canonical point events.

## CourtIQ Integration Audit

CourtIQ was inspected during Milestone 2.6. Useful files were preserved as reference-only under `external_review/courtiq/preserved_reference/`.

| Result | Summary |
| --- | --- |
| Files seen | `17` |
| Direct runtime merges | `0` |
| Preserved reference assets | replay producer, validation consumer, Kafka setup, Compose fragment, replay audit, point-event schema mismatch evidence |
| Rejected assets | duplicate/obsolete contracts, staging data notes, non-canonical completion claims |

Use `docs/courtiq_integration_audit.md`, `docs/courtiq_file_inventory.md`, and `docs/post_merge_next_phase_plan.md` before adapting any CourtIQ asset.

## Model Artifacts

```text
data/models/odds/latest.json
data/models/odds/v1/model.joblib
data/models/odds/v1/feature_schema.json
data/models/risk/latest.json
data/models/risk/v1/risk_config.json
```

## Replay Producer

Dry-run:

```bash
.venv/bin/python producer/replay_producer.py \
  --manifest data/replay/manifests/replay_manifest_v1.parquet \
  --config infra/kafka/topic_config.json \
  --dry-run \
  --dry-run-output data/results/replay_dry_run/sample_events.jsonl \
  --max-events 1000

.venv/bin/python scripts/validate_replay_producer.py \
  --events data/results/replay_dry_run/sample_events.jsonl \
  --schema contracts/point_event_schema.json
```

Kafka local:

```bash
docker compose -f infra/docker/docker-compose.kafka.yml up -d
bash infra/kafka/kafka_setup.sh
```

Kafka runtime was not executed in the current validation environment.

## Next Milestone

Milestone 3B: streaming scorer integration.

Scope:

- consume `tennis-point-events`
- build online features compatible with `data/models/odds/v1/feature_schema.json`
- load `data/models/odds/latest.json`
- load `data/models/risk/latest.json`
- write scored output to local JSONL/Parquet first

## Historical Workstream Split

| Track | Branch | Owner Scope | Prompt |
| --- | --- | --- | --- |
| Track A | `feature/milestone-2b-model-artifacts` | model training, risk config, evaluation, two-phase publication | `docs/codex_prompt_milestone_2b.md` |
| Track B | `feature/milestone-3a-replay-producer` | Kafka local setup, replay producer, validation consumer, event contract | `docs/codex_prompt_milestone_3a.md` |

## Stable Inputs

```text
data/features/point_features/
data/features/match_features/
data/baselines/player_baselines/
data/replay/manifests/replay_manifest_v1.parquet
data/features/feature_quality_report.json
data/features/validation_report.json
data/baselines/baseline_quality_report.json
data/replay/replay_manifest_report.json
contracts/
```

Do not use `cleaned_data/` or staging CSV.GZ files for future modeling or replay work.

## Validate Parallel Readiness

```bash
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```

## Validate Milestone 2.7

```bash
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python scripts/validate_replay_producer.py --events data/results/replay_dry_run/sample_events.jsonl --schema contracts/point_event_schema.json
.venv/bin/python scripts/validate_feature_layer.py --curated data/curated --features data/features --baselines data/baselines --replay data/replay --contracts contracts
.venv/bin/python -m pytest tests
```

## Validate CourtIQ Integration Guardrails

```bash
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```

## Deprecated Plan Warning

`2_week_execution_plan.md` is historical and deprecated. It references older Cassandra, Elasticsearch, Grafana/Kibana, 50M-record, and 25K events/sec goals that are not current milestone requirements. Use `README.md`, `CODEX.md`, `docs/parallel_workstream_handoff.md`, and current milestone docs as source of truth.
