# Feature Engineering Audit

## Inputs Used

Milestone 2A used only `data/curated/singles_points/` and `data/curated/singles_matches/`. No staging CSV.GZ files, model artifacts, Kafka, streaming jobs, APIs, or frontend code were used.

## Transformations

- Curated singles points were sorted by `match_id`, `event_index`, and `event_id`.
- Point-level cumulative, rolling, serve/return, score-context, sparse rally, elapsed-time, and label columns were generated.
- Match-level summaries were derived from the point feature layer.
- All feature outputs were written as Parquet under `data/features/`.

## Point-In-Time Safety

Every `*_before` feature is shifted by construction: cumulative values subtract the current row's contribution, rolling windows use shifted values, and prior averages use only rows with `event_index` lower than the current row within the same match. Labels are allowed to use future outcome information and are separated with `label_` prefixes.

## Feature List

The point feature contract is `contracts/point_feature_schema.json`; the match feature contract is `contracts/match_feature_schema.json`.

## Labels

- `label_point_winner_is_player_a`
- `label_server_won_point`
- `label_match_winner_is_player_a`
- `label_match_winner_player`

## Known Limitations

- Rally features are sparse and are not recommended for the MVP primary feature set.
- Surface features are unavailable because curated `surface` is missing.
- Match winner labels are inferred from the last valid point winner in each curated point sequence, not from an ATP bridge.
- Rows with unknown-player placeholders are preserved but flagged.

## Verdict

Milestone 2A feature layer status: **PASSED**.

Input rows: 1922136
Output rows: 1922136
Match count: 10508
