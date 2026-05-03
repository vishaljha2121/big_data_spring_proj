# Risk Scoring Methodology

## Method

The risk artifact is a conservative baseline-deviation scoring configuration. It compares current or fixture metrics to population baseline expectations derived from `data/baselines/player_baselines/`.

This is not match-fixing detection. It is not proof of misconduct.

## Features Used

- `serve_point_win_pct`
- `return_point_win_pct`
- `ace_rate`
- `double_fault_rate`

Unknown placeholder players are not treated as strong baselines.

## Formula

For each available feature:

```text
deviation = min(1.0, abs(current_value - baseline_expectation))
risk_score = average(available deviations)
```

If no comparable features are available, the score is `0.0` with missing-feature warnings.

## Buckets

- low: `risk_score < 0.40`
- medium: `0.40 <= risk_score < 0.70`
- high: `risk_score >= 0.70`

## Output

The scoring function returns:

- `risk_score`
- `risk_bucket`
- `primary_signal`
- `explanation`
- `missing_feature_warnings`

## Limitations

- Surface-specific risk signals are blocked.
- Rally-length risk signals are not primary MVP signals.
- This artifact uses no fake labels and no supervised anomaly target.
