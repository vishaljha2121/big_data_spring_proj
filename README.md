# Tennis Point-Level Feature Engineering Project

This repository contains the data engineering foundation for a tennis point-level analytics and modeling pipeline. The current implementation has completed Milestone 1B and Milestone 2A: curated singles-only Parquet data, point-in-time-safe feature generation, player baselines, replay manifest preparation, validation scripts, schema contracts, tests, and audit documentation.

## Current Status

- Milestone 1B: PASSED
- Milestone 2A: PASSED
- Latest validation command: `.venv/bin/python scripts/validate_feature_layer.py --curated data/curated --features data/features --baselines data/baselines --replay data/replay --contracts contracts`
- Latest test result: `21 passed`

## Implemented Checklist

- [x] Converted staging CSV.GZ inputs into cleaned Parquet layers.
- [x] Built curated singles-only point data under `data/curated/singles_points/`.
- [x] Built curated singles match metadata under `data/curated/singles_matches/`.
- [x] Preserved invalid/special point evidence under `data/quarantine/`.
- [x] Added data quality reports and feature availability reports.
- [x] Added schema contracts for curated data and Milestone 2A outputs.
- [x] Built point-in-time-safe point-level features under `data/features/point_features/`.
- [x] Built match-level feature summaries under `data/features/match_features/`.
- [x] Built player baselines under `data/baselines/player_baselines/`.
- [x] Built deterministic replay manifests under `data/replay/manifests/`.
- [x] Added validation scripts for cleaned/curated and feature-layer outputs.
- [x] Added audit documentation for data cleaning, feature engineering, baselines, and replay manifests.
- [x] Added pytest coverage for normalization, schema checks, point-in-time safety, baselines, and replay manifest determinism.

## Remaining Checklist

- [ ] Milestone 2B: train the first model using the validated feature layer.
- [ ] Publish model artifacts only after training validation passes.
- [ ] Define and validate a reliable ATP match bridge before using ATP-derived labels or match metadata.
- [ ] Add surface-specific features only after surface metadata becomes available.
- [ ] Treat rally-length features as secondary until coverage improves.
- [ ] Build Kafka replay producer from `data/replay/manifests/replay_manifest_v1.parquet`.
- [ ] Add Spark Structured Streaming after replay and batch model paths are stable.
- [ ] Build serving API only after model artifact publication.
- [ ] Build frontend only after the API contract is stable.

## Key Findings So Far

- Curated singles point rows: `1,922,136`.
- Curated singles matches: `10,508`.
- Point feature rows: `1,922,136`.
- Match feature rows: `10,508`.
- Player baselines: `1,891`.
- Replay manifest events: `1,917,672`.
- Replay manifest matches: `10,464`.
- Replay exclusions: `44` matches, including `32` unknown-player placeholder matches and `12` matches with fewer than 20 valid points.
- Surface coverage is `0.0%`, so surface-based features and baselines are blocked.
- Rally length coverage is about `5.96%`, so rally length should not be a primary MVP model feature.
- Elapsed-time feature availability is about `80.76%`.
- Serve/return feature availability is about `99.42%`.
- Unknown-player rows remain visible and auditable instead of being silently dropped.

## Milestone 2A Outputs

```text
data/features/
  point_features/part-00000.parquet
  match_features/part-00000.parquet
  feature_build_report.json
  feature_quality_report.json
  validation_report.json

data/baselines/
  player_baselines/part-00000.parquet
  baseline_quality_report.json

data/replay/
  manifests/replay_manifest_v1.parquet
  manifests/replay_manifest_v1.json
  replay_candidates/part-00000.parquet
  replay_manifest_report.json
```

## How To Rebuild Milestone 2A

```bash
.venv/bin/python scripts/build_feature_layer.py \
  --curated data/curated \
  --out data/features \
  --contracts contracts

.venv/bin/python scripts/build_player_baselines.py \
  --features data/features \
  --curated data/curated \
  --out data/baselines \
  --contracts contracts

.venv/bin/python scripts/build_replay_manifests.py \
  --curated data/curated \
  --out data/replay \
  --contracts contracts \
  --seed 42 \
  --default-interval-seconds 2

.venv/bin/python scripts/validate_feature_layer.py \
  --curated data/curated \
  --features data/features \
  --baselines data/baselines \
  --replay data/replay \
  --contracts contracts

.venv/bin/python -m pytest tests
```

## Guardrails

Do not use staging CSV.GZ files directly for future modeling milestones. Use the curated Parquet datasets and validated feature outputs. Do not start model training, Kafka, Spark Structured Streaming, FastAPI, or React until the corresponding milestone is explicitly in scope.

