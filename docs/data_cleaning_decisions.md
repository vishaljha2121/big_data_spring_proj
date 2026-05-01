# Data Cleaning Decisions

- `cleaned_data/` is staging input, not final cleaned output.
- MVP curated data is singles only; doubles and mixed are excluded by filename classification and counted.
- Invalid `PointWinner`/`PointServer` codes are not silently cast. Valid values are `1`, `1.0`, `2`, and `2.0`; all other non-empty values are invalid and mapped player fields are set to null.
- Non-integer `PointNumber` values such as `0X`, `0Y`, and `45D` are not forced to integers. They are counted, copied to quarantine evidence, and represented as null in canonical `point_number`.
- `event_index` is deterministic by `match_id`, source event suffix when present, and source row order.
- ATP match data is written as cleaned Parquet but not forced into curated points because there is no inspected reliable key bridge.
- Blank `player1` or `player2` metadata values are not dropped or fabricated as real names. They are replaced with deterministic unknown-player participant placeholders in curated output and copied to `data/quarantine/invalid_metadata/`.
- No fraud labels, model labels, or anomaly labels are created in Milestone 1B.
