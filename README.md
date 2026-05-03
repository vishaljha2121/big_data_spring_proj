# Tennis Point-Level Analytics Project

This repository contains the validated data and feature foundation for a tennis point-level analytics pipeline. Milestone 2.5 freezes contracts and splits the remaining work into two independent implementation tracks: model artifacts and Kafka replay infrastructure.

## Current Status

- Milestone 1B: PASSED
- Milestone 2A: PASSED
- Milestone 2.5: PASSED after running `scripts/validate_parallel_readiness.py`
- Milestone 2B: NOT STARTED in this branch; prepared for Track A
- Milestone 3A: NOT STARTED in this branch; prepared for Track B

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

## Remaining Checklist

- [ ] Track A / Milestone 2B: train odds model and create risk config.
- [ ] Track A / Milestone 2B: publish validated model artifacts through staging to `v1`.
- [ ] Track B / Milestone 3A: implement local Kafka setup and replay producer.
- [ ] Track B / Milestone 3A: validate Kafka point-event contract and replay ordering.
- [ ] Future Milestone 3B: integrate streaming scorer after both tracks merge.
- [ ] Do not start Spark Structured Streaming, FastAPI, React, or serving DB work until both tracks pass.

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

## Workstream Split

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

## Deprecated Plan Warning

`2_week_execution_plan.md` is historical and deprecated. It references older Cassandra, Elasticsearch, Grafana/Kibana, 50M-record, and 25K events/sec goals that are not current milestone requirements. Use `README.md`, `CODEX.md`, `docs/parallel_workstream_handoff.md`, and current milestone docs as source of truth.
