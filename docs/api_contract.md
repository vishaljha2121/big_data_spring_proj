# API Contract

## Scope

Milestone 4A exposes a local file-backed FastAPI service over validated scored tennis point output. It does not require Kafka, Docker, PostgreSQL, Redis, or a frontend.

Base service version: `api_v1`

## Endpoints

### `GET /health`

Returns service liveness:

```json
{"status":"ok","service":"tennis-scoring-api","timestamp":"...","version":"api_v1"}
```

### `GET /ready`

Checks required files: scored events JSONL, scoring run report, odds latest pointer, risk latest pointer, and in-memory event load.

### `GET /api/summary`

Returns scored event count, unique match count, odds/risk model versions, benchmark throughput, average latency, p95 latency, warnings, and risk disclaimer.

### `GET /api/scored-events`

Query parameters:

- `limit`: default `100`, max `1000`
- `offset`: default `0`
- `risk_bucket`: optional `low`, `medium`, or `high`
- `match_id`: optional synthetic or source match id

Returns paginated compact scored events.

### `GET /api/scored-events/{event_id}`

Returns one full scored event.

### `GET /api/matches`

Query parameters:

- `limit`: default `100`, max `1000`
- `offset`: default `0`

Returns match summaries with event count, average player-A point probability, max risk score, high-risk event count, and first/last event timestamps.

### `GET /api/matches/{synthetic_match_id}`

Returns match summary, all loaded scored events for the match, risk summary, and point probability timeline.

### `GET /api/matches/{synthetic_match_id}/events`

Returns paginated scored events for a match.

### `GET /api/risk/summary`

Returns bucket counts, top risk events, top risk matches, and the statistical-risk disclaimer.

### `GET /api/risk/events`

Query parameters:

- `bucket`: optional `low`, `medium`, or `high`
- `limit`: default `100`, max `1000`
- `offset`: default `0`

Returns risk-sorted scored events.

### `GET /api/models/current`

Returns odds latest pointer, odds metadata summary, feature count, risk latest pointer, risk config summary, and `fake_labels_used=false`.

### `GET /api/benchmarks/latest`

Returns scoring benchmark, scoring run report, scoring validation report, model eval reports, and validation status.

### `GET /api/data/coverage` *(Milestone 5B)*

Returns data coverage metadata:

- `scored_event_count`, `scored_match_count`: from the scored events file
- `replay_manifest_event_count`, `replay_manifest_match_count`: from the full replay manifest
- `scored_data_source`, `replay_manifest_source`: file paths
- `coverage_mode`: `"sample"`, `"full_demo"`, or `"manifest_catalog"`
- `warning`: present when only sample data is loaded

### `GET /api/replay/matches` *(Milestone 5B)*

Query parameters:

- `limit`: default `100`, max `500`
- `offset`: default `0`
- `search`: optional player name or match ID substring

Returns the replay catalog from the full manifest. Each item includes `player_a`, `player_b`, `primary_match_label`, `replay_id`, `replay_event_count`, `first_event_ts`, `last_event_ts`, and `scored_available`.

### `GET /api/replay/matches/{synthetic_match_id}/events` *(Milestone 5B)*

Query parameters:

- `limit`: default `1000`, max `5000`
- `offset`: default `0`

Returns raw replay manifest events for a match (even if not scored). Events are sorted by `replay_order`.

## Contract Artifacts

```text
contracts/api_openapi_snapshot.json
contracts/api_response_examples.json
```

## Limitations

- `point_probability_player_a` and `point_probability_player_b` are point-level probabilities. They are not betting odds and not match-win probabilities.
- Risk scores are statistical anomaly signals for review only. They are not proof of misconduct and not match-fixing detection.
- The API serves the current local scored sample, not a live Kafka stream.
