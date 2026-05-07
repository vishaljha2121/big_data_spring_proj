# Richer Targets and Observability Gap Analysis

**Milestone:** 5C
**Date:** 2026-05-06

## 1. What does the current model predict?
The existing machine learning model predicts the probability of Player A winning the *current point* (`label_point_winner_is_player_a`). It is a micro-level, point-in-time model.

## 2. Why point probability is not match-win probability?
Tennis uses a hierarchical, non-linear scoring system (points → games → sets → match). A player with a 55% probability of winning any given point typically has a >90% probability of winning the match, but the relationship is complex due to serve advantage, "big points" (break points, set points), and momentum. Point-level probability does not equate to the macro probability of winning the entire match, nor does it equal betting market odds which include bookmaker margins and public betting volume.

## 3. What richer targets are feasible from current data?
Assuming the chronological point data accurately reflects the progression of the match, we can potentially derive macro outcomes:
- **Game Winner**: Which player ultimately wins the current game.
- **Set Winner**: Which player ultimately wins the current set.
- **Match Winner**: Which player ultimately wins the entire match.

## 4. What labels can be reliably derived?
By scanning forward in the event stream for a given match:
- If a match is complete, the final point winner often wins the final game, set, and match. Alternatively, by tallying sets won, the match winner can be deduced.
- Set winners can be deduced by identifying the player who wins the final game of a set (when `set_number` increments or the match ends).
- Game winners can be deduced by identifying the player who wins the final point of a game (when `game_number` or `set_number` increments).

## 5. What labels are too risky or invalid?
- **Incomplete/Retired matches**: If a match ends prematurely, the "final" point winner did not necessarily win the match. These must be excluded.
- **Unknown Players**: Matches involving "Unknown" players or placeholders cannot be confidently labeled.
- **Betting Odds**: Without historical market data, generating "odds" is a fabrication.
- **Match-Fixing Detection**: Risk scores denote statistical anomalies, not proven misconduct.

## 6. What observability exists today?
Currently, the project generates static reports:
- Model evaluation reports (`odds_model_eval_report.json`, `risk_model_eval_report.json`)
- Scoring benchmark reports (`scoring_benchmark_report.json`, `scoring_run_report.json`)
- Validation reports (`spark_streaming_validation_report.json`)
- Simple API endpoints (`/health`, `/ready`, `/api/summary`)

## 7. What observability is missing?
A production-grade system requires dynamic observability:
- **Traceability**: Unique Trace IDs linking scoring runs to outputs.
- **Structured Logging**: JSON-formatted logs for API and scoring events.
- **Live Metrics**: API request counts, latency distributions, and runtime status.
- **Data Quality Alerts**: Warnings for missing surface metadata, unmapped players, or missing features.
- **Model Score Drift**: Detecting shifts in predicted probabilities compared to training baselines.

## 8. What will be implemented in this milestone?
- **Label Audit**: A strict, automated audit (`scripts/audit_outcome_labels.py`) to determine if game, set, and match winner labels can be reliably extracted from the existing dataset.
- **Outcome Models**: If labels pass the audit, derivation of target datasets and training of lightweight game/set/match models.
- **Local Observability Layer**: A structured logging, metric-gathering, and alerting module.
- **API & UI Extensions**: New observability endpoints and a "Pipeline Monitor" dashboard panel to expose these metrics.

## 9. What remains future work?
- External integration with true APM tools (Datadog, Prometheus, Grafana).
- Distributed tracing across microservices (OpenTelemetry, Jaeger).
- True concept drift detection requiring ongoing ground-truth labeling.
- Actual betting market integration for real-world odds comparison.
