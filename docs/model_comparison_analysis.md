# Model Comparison Analysis

## 1. What Our Model Predicts

Our model is a **point-level probability model**. For each tennis point event in a match replay, it predicts the probability that Player A wins the current point.

- **Target:** `label_point_winner_is_player_a` (Player A point winner label)
- **Model type:** HistGradientBoosting classifier (scikit-learn)
- **Feature count:** 26 point-in-time-safe features
- **Training rows:** 300,000
- **Validation rows:** 287,565
- **Test rows:** 284,868
- **Random seed:** 42

The model outputs a calibrated probability between 0 and 1, not a class label, making it suitable for real-time scoring dashboards where point-by-point probability movement is the primary analytical tool.

## 2. What the Inspiration Models Likely Predict

The public tennis prediction and betting tools that inspired this project operate at a fundamentally different level:

| Reference | Prediction unit | Primary metric | Approach |
|---|---|---|---|
| TennisBets-style model | Match outcome (pre-match) | Held-out match accuracy | XGBoost trained on 95k+ ATP matches with ELO-style features |
| SportBot-style model | Match/set outcome (picks) | Pick accuracy, CLV, ROI | Surface-aware Elo + serve/return analytics |
| CourtCruncher-style system | Betting units | Units profit | ATP/Challenger Elo-based betting system |

These systems predict **whether a player will win a match** (or a set, or produce a betting edge) rather than predicting the outcome of individual points within a match.

## 3. Why Point-Level AUC Is Not Directly Comparable to Match-Level Accuracy

### Different prediction targets

- Our model predicts: "Will Player A win this specific point?" (binary, per-point)
- Match-level models predict: "Will Player A win the match?" (binary, per-match)

### Different base rates

- Point-level outcomes are closer to 50/50, especially in competitive tennis, making high AUC harder to achieve.
- Match-level outcomes can have more signal, especially with ELO/ranking features and historical head-to-head data.

### Different evaluation metrics

- Our model reports **AUC** and **Brier score** on a held-out test set of 284,868 points.
- Match-level models typically report **accuracy** (% of correct match winner predictions) and/or **betting-oriented metrics** (ROI, CLV, units).

### AUC vs accuracy

- AUC measures discrimination ability across all thresholds.
- Accuracy at a 50% threshold is a single operating point.
- A point-level AUC of 0.64 and a match-level accuracy of 66% are measuring fundamentally different things and cannot be directly compared.

## 4. Our Current Validated Metrics

From the published model evaluation report (`data/models/odds/v1/eval_report.json`):

| Metric | Validation | Test |
|---|---|---|
| AUC | 0.6396 | 0.6415 |
| Brier score | 0.2351 | 0.2347 |
| Log loss | 0.6628 | 0.6619 |

From the scoring benchmark (`data/results/streaming_scoring/scoring_benchmark_report.json`):

| Metric | Value |
|---|---|
| Scoring throughput | 2,454.2 events/sec |
| Average latency | 0.384 ms/event |
| p95 latency | 0.575 ms/event |
| Model load time | 1.705 seconds |

## 5. Public Reference Metrics

> **Important:** These are publicly reported claims from reference projects. They have not been independently verified by our team. They are presented as context, not as validated benchmarks.

### TennisBets-style match predictor
- **Claim:** 66.3% held-out match accuracy on 2024 ATP matches
- **Approach:** XGBoost model trained on 95k+ ATP matches with ELO-style features
- **Metric type:** Match-level pre-match accuracy
- **Source:** Public project page (not independently validated)

### SportBot-style surface-aware model
- **Claim:** 55% recent-pick accuracy, +2% CLV, +9.1% ROI
- **Approach:** Surface-aware Elo combined with serve/return analytics
- **Metric type:** Betting outcome metrics (accuracy, CLV, ROI)
- **Source:** Public reporting (not independently validated)

### CourtCruncher-style Elo betting system
- **Claim:** Performance reported in betting units rather than classification accuracy
- **Approach:** ATP/Challenger Elo-based betting system
- **Metric type:** Betting system performance metrics
- **Source:** Public reporting (not independently validated)

## 6. What We Can Honestly Claim

Based on validated local evidence:

1. **Our model produces calibrated point-level probabilities** with a test AUC of 0.6415 and a test Brier score of 0.2347 on 284,868 held-out points.

2. **The scoring pipeline runs at production-capable throughput** — 2,454 events/sec with sub-millisecond p95 latency on a local machine.

3. **The full pipeline is end-to-end validated** from curated data through features, model training, replay, scoring, API serving, and dashboard display.

4. **Model artifacts are published and versioned** with schema hashes, evaluation reports, and quality gates.

5. **Risk scoring provides statistical review signals** using baseline deviation methodology with no fake labels.

## 7. What We Cannot Claim

1. **We cannot claim our model is better than match-level prediction systems.** The comparison is apples-to-oranges because we predict points, not matches.

2. **We cannot claim a point-level AUC of 0.64 is equivalent to or better than a match-level accuracy of 66%.** These are fundamentally different metrics on different prediction targets.

3. **We cannot claim our probability outputs are betting odds.** They are statistical model outputs for analytical display.

4. **We cannot claim our risk scores detect match-fixing.** They are statistical anomaly signals for review only.

5. **We cannot claim the reference models' reported metrics are independently verified.** They are publicly reported claims.

## 8. Future Work for Fair Comparison

To enable a fair head-to-head comparison with match-level prediction systems:

1. **Build match-level outcome labels** — Aggregate point-level predictions into match-win probabilities using score simulation or direct match-level modeling.

2. **Use the same held-out match set** — Evaluate all models on identical held-out matches from the same time period.

3. **Report common metrics** — Accuracy, log loss, Brier score, and calibration at the match level.

4. **Compare against closing odds** — If historical betting odds data is available, use it as a benchmark baseline for all models.

5. **Evaluate at the same granularity** — Build a match-level classifier that uses our point-level features and compare directly with ELO/XGBoost match-level approaches.

6. **Control for surface and ranking data** — Our current model lacks surface features; adding them would enable fairer comparison with surface-aware models.

---

*Generated as part of Milestone 4E — Frontend Narrative Polish.*
*Metrics sourced from validated local artifacts. Reference metrics from public claims.*
