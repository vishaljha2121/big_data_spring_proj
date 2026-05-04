# Scoring Output Contract

## Contract

Scored events must validate against:

```text
contracts/scored_event_schema.json
```

The contract version is `scored_event_v1`.

## Required Output Fields

The scored event preserves replay identity and player context, then appends:

- `point_probability_player_a`
- `point_probability_player_b`
- `selected_model_type`
- `odds_model_version`
- `feature_schema_hash`
- `risk_score`
- `risk_bucket`
- `primary_risk_signal`
- `risk_explanation`
- `missing_feature_warnings`
- `scoring_latency_ms`
- `scored_at`
- `input_event_valid`
- `feature_row_valid`

## Probability Naming

The published MVP model target is `label_point_winner_is_player_a`, so the runtime output is a point-level probability. The scorer intentionally does not emit `match_win_probability` because no match-win conversion model exists.

## Risk Interpretation

Risk buckets are:

- `low`: `risk_score < 0.40`
- `medium`: `0.40 <= risk_score < 0.70`
- `high`: `risk_score >= 0.70`

The risk score is a statistical deviation signal only. It is not match-fixing detection, proof of misconduct, or an injury detector.

## Local Outputs

Current sample outputs:

```text
data/results/streaming_scoring/scored_events_sample.jsonl
data/results/streaming_scoring/scored_events_sample.parquet
data/results/streaming_scoring/scoring_run_report.json
data/results/streaming_scoring/scoring_validation_report.json
data/results/streaming_scoring/scoring_benchmark_report.json
```
