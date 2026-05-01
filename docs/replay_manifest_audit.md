# Replay Manifest Audit

## Selection Criteria

Replay candidates were built only from `data/curated/singles_points/`. Matches with deterministic unknown-player placeholders were excluded by default, and matches with fewer than 20 valid point winners were excluded.

## Manifest Schema

The replay manifest schema is stored in `contracts/replay_manifest_schema.json`. The Parquet manifest is `data/replay/manifests/replay_manifest_v1.parquet`.

## Timestamp And Offset Logic

When `elapsed_seconds` is present, it drives `replay_offset_seconds`. Missing elapsed time falls back to `event_index * 2.0` semantics through a deterministic per-event interval. Offsets are monotonic within each synthetic match. Event timestamps are generated relative to `2026-01-01T00:00:00Z` for deterministic replay preparation.

## Exclusions

Excluded matches: 44

## Next Kafka Step

The next milestone may build a Kafka replay producer that reads this manifest in `synthetic_match_id, replay_order` order. Kafka was not started in Milestone 2A.
