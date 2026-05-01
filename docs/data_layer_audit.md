# Data Layer Audit

## Executive Verdict

Milestone 1B status: **PASSED**.

The teammate-provided CSV.GZ files were treated as staging input. The project-compliant outputs are Parquet datasets under `data/cleaned/` and `data/curated/`, with quarantine evidence under `data/quarantine/`.

## Input Inventory

- Total CSV.GZ files seen: 85
- Point files seen: 83
- Metadata files seen: 1
- ATP match files seen: 1
- Raw point rows: 2314887
- Raw metadata rows: 13154
- Raw ATP match rows: 941649

## Transformations

- Singles point files were converted to canonical curated point Parquet.
- Doubles and mixed files were excluded from MVP curated singles output.
- `PointWinner` and `PointServer` values `1`, `1.0`, `2`, and `2.0` were normalized to players; invalid codes were counted and nullified in mapped player fields.
- Special non-integer `PointNumber` values were counted, nullified in `point_number`, and copied to quarantine evidence.
- `ElapsedTime` was parsed to `elapsed_seconds` where possible.
- Metadata was joined by `match_id`; ATP matches were preserved as cleaned Parquet without a forced unreliable join.
- Rows with blank `player1` or `player2` metadata were preserved using deterministic `unknown_player_1:<match_id>` / `unknown_player_2:<match_id>` participant placeholders and copied to invalid metadata quarantine evidence.

## Exclusions And Quarantine

- Excluded doubles files: 18
- Excluded doubles rows: 329456
- Excluded mixed files: 16
- Excluded mixed rows: 63295
- Quarantined evidence rows: 10599

## Quality Results

- Curated singles point rows: 1922136
- Curated singles match count: 10508
- Duplicate event IDs: 0
- Missing event IDs: 0
- Missing match IDs: 0
- Metadata join missing rows: 4310
- Invalid PointWinner values: 10599
- Invalid PointServer values: 10598
- Special PointNumber values: 6970
- Missing elapsed time rows: 369445
- Missing rally length rows: 1807598
- Missing surface rows: 1922136

## Remaining Risks

- Surface is not present in `match_metadata_cleaned.csv.gz`, so curated `surface` is null.
- Some metadata rows have blank player slots. The curated layer keeps those rows with deterministic unknown-player placeholders and quarantines the original rows for review.
- Rally length coverage is sparse and should not be a primary MVP feature.
- ATP match data is preserved but not joined to point events until a reliable bridge is defined.
- Static curated data intentionally leaves `event_ts` null; replay timestamps belong to the later replay milestone.
