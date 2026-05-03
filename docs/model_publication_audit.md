# Model Publication Audit

## Publication Flow

Both model tracks use two-phase publication:

1. Write staging artifacts under `data/models/<type>/staging/`.
2. Validate loadability, fixture scoring, schemas, hashes, and gates.
3. Copy staging artifacts to `data/models/<type>/v1/`.
4. Write `latest.json` only after validation passes.

## Odds Artifact

- Staging path: `data/models/odds/staging/`
- Published path: `data/models/odds/v1/`
- Registry pointer: `data/models/odds/latest.json`
- Artifact: `data/models/odds/v1/model.joblib`
- Feature schema: `data/models/odds/v1/feature_schema.json`

## Risk Artifact

- Staging path: `data/models/risk/staging/`
- Published path: `data/models/risk/v1/`
- Registry pointer: `data/models/risk/latest.json`
- Artifact/config: `data/models/risk/v1/risk_config.json`

## Gates

Odds gates passed:

- validation AUC >= `0.55`
- test AUC >= `0.55`
- validation Brier <= `0.30`
- test Brier <= `0.30`
- fixture probabilities in `[0, 1]`
- feature schema hash matches metadata

Risk gates passed:

- config loads
- fixture scoring works
- `fake_labels_used=false`

## Failure Behavior

If gates fail, `latest.json` is not written and the staging failure file records reasons.
