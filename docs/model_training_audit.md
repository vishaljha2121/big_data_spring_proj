# Model Training Audit

## Verdict

Milestone 2.7 model training passed. A real odds model and conservative risk scoring artifact were trained/built from validated Milestone 2A outputs and published through the two-phase staging-to-v1 flow.

## Inputs

- `data/features/point_features/`
- `data/baselines/player_baselines/`
- `data/features/feature_quality_report.json`

Forbidden raw/staging CSV inputs were not used.

## Split Strategy

Deterministic match-level split with seed `42`:

- train matches: `7355`
- validation matches: `1576`
- test matches: `1577`
- full train rows: `1338464`
- validation rows used for evaluation: `287565`
- test rows used for evaluation: `284868`

No `match_id` appears in more than one split.

## Odds Model

- Target: `label_point_winner_is_player_a`
- Selected model: `HistGradientBoostingClassifier`
- Feature count: `26`
- Training rows used by selected run: `300000`
- Validation AUC: `0.639548197813816`
- Test AUC: `0.6415344327971061`
- Validation Brier score: `0.23509465864335471`
- Test Brier score: `0.2346526207800247`

The first candidate run showed an unrealistically high AUC when current score numeric fields were included. Those fields were removed before publication to avoid likely score-state leakage.

## Limitations

- Surface features remain blocked.
- Rally-length features remain sparse and excluded from the primary model.
- ATP-derived labels/features remain blocked.
- Model performance is MVP-level only and should be monitored in streaming replay.
