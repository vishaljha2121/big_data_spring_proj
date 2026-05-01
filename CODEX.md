# CODEX.md — Tennis Big Data Project Instructions

## Project Goal

Build a real-time tennis odds and integrity-risk analytics platform using a cloud-style big data architecture.

## Current Priority

The current priority is Milestone 1B:

Curated Singles Point Dataset + Project-Compliant Cleaned Data Layer + Data Quality Report.

Do not work on model training, Kafka replay, Spark streaming, API, or frontend until Milestone 1B passes.

## Architecture Summary

The planned architecture uses:

- S3-style data lake
- Spark batch for cleaning and features
- Kafka for replay
- Spark Structured Streaming for live scoring
- PostgreSQL for serving
- FastAPI backend
- React frontend

## Data Layer Rule

The current teammate-provided `cleaned_data` zip is staging input only. It is not final cleaned output.

Final cleaned/curated outputs must include:

- Parquet files
- schema JSON files
- zone_metadata.json
- data_quality_report.json
- feature_availability_report.json
- human-readable audit docs
- validation tests

## MVP Dataset Rule

Use singles point data only for MVP. Exclude doubles and mixed from curated singles outputs.

## No Overclaiming

Risk scores are statistical anomaly signals only. Do not claim match-fixing detection.

## Execution Discipline

Work in small, validated increments:

1. inventory
2. profile
3. normalize
4. curate
5. validate
6. report
7. handoff

Every phase must leave behind files, tests, or reports.

Your first milestone is not modeling or streaming. It is Milestone 1B: convert the teammate-provided cleaned_data zip from staging-level CSV.GZ into a project-compliant cleaned/curated data layer.

Use the latest implementation plan as source of truth.

Treat the zip as staging input only. Build local S3-style outputs:

- cleaned/points/\*.parquet
- cleaned/matches/\*.parquet
- cleaned/match_metadata/\*.parquet
- curated/singles_points/\*.parquet
- curated/singles_matches/\*.parquet
- zone_metadata.json
- data_quality_report.json
- feature_availability_report.json
- docs/data_layer_audit.md
- docs/data_cleaning_decisions.md
- tests

MVP = singles only. Exclude doubles/mixed and report row counts.

Normalize:

- event_id
- match_id
- event_index
- player_a/player_b
- server_player
- point_winner_player
- set/game/point fields
- scores
- rally_length
- serve speed
- ace/double fault/break point flags
- elapsed_seconds
- source_file
- schema_version

Do not silently cast dirty values. Handle PointWinner/PointServer values like 1, 1.0, 2, 2.0, 0, blank. Handle special PointNumber values like 0X, 0Y, 45D explicitly.

Generate:

- data_quality_report.json
- feature_availability_report.json
- human-readable audit
- validation tests

Milestone passes only if:

- curated singles Parquet exists
- event_id and match_id are non-null
- event_id is unique
- event_index is deterministic within match
- doubles/mixed excluded
- invalid values counted/quarantined
- reports exist
- tests pass

Do not proceed to feature engineering, Kafka, streaming, models, API, or frontend until this passes.

# CODEX.md — Current Execution Rules

Current milestone: Milestone 2A only.

Goal:
Build point-in-time-safe feature engineering, player baselines, and replay manifest preparation from the already validated Milestone 1B curated singles data.

Allowed source data:

- data/curated/singles_points/
- data/curated/singles_matches/
- data/curated/replay_candidates/
- data/curated/data_quality_report.json

Do not use:

- original cleaned_data CSV.GZ files
- staging CSV files
- raw zip directly

Do not implement:

- model training
- Kafka
- Spark Structured Streaming
- FastAPI
- React
- frontend
- deployment

Core correctness rule:
All features ending in `_before` must use only events with lower event_index inside the same match. Current point outcome must never be included in current row features.

MVP rules:

- singles only
- rally_length is sparse, so optional only
- surface is unavailable, so do not build surface-specific features
- unknown player placeholders must not be treated as strong baselines
- no fake anomaly labels
- no overclaiming integrity detection

Definition of done:

- feature Parquet exists
- baseline Parquet exists
- replay manifest exists
- JSON reports exist
- audit docs exist
- validation script passes
- pytest passes
