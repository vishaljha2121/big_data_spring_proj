# Event Contract Handoff

## Canonical Kafka Event

The replay producer emits JSON events that match `contracts/point_event_schema.json`.

Required fields:

- `schema_version`
- `replay_session_id`
- `synthetic_match_id`
- `source_match_id`
- `event_id`
- `synthetic_event_id`
- `event_index`
- `replay_order`
- `replay_offset_seconds`
- `event_ts`
- `player_a`
- `player_b`
- `server_player`
- `receiver_player`
- `point_winner_player`
- `set_number`
- `game_number`
- `point_number`
- `p1_score`
- `p2_score`
- `is_ace`
- `is_double_fault`
- `is_break_point`
- `source_file`

## Partition Key

Use `synthetic_match_id`.

## Important Boundary

The Kafka event does not include model features. Milestone 3B must build online features from raw replay events before scoring.
