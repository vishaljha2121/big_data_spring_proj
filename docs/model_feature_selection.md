# Model Feature Selection

## Included Features

The published odds model uses 26 point-in-time-safe numeric/boolean features from `data/features/point_features/`.

Included families:

- prior point counts and win percentages
- prior server and receiver point counts/win percentages
- recent 5/10 prior point win percentages
- prior ace and double-fault counts
- elapsed-time prior values and availability flags
- server/receiver identity flags relative to player A
- data validity flags

## Excluded Features

Excluded from training:

- identifiers: `event_id`, `match_id`, `source_file`, `schema_version`
- raw player names and current winner fields
- all label columns except the selected target
- raw score strings
- current game/set/score numeric fields after leakage review
- surface fields because surface coverage is unavailable
- rally-length features because coverage is sparse
- ATP bridge fields because no reliable bridge is validated

## Target

Primary target: `label_point_winner_is_player_a`.

## Null Handling

The published sklearn pipeline uses median imputation inside the model artifact, so inference callers must provide exactly the frozen feature list and may pass null numeric values.

## Inference Contract

The frozen feature contract is `data/models/odds/v1/feature_schema.json`. The streaming scorer in Milestone 3B must reject inputs whose feature columns do not match that schema.
