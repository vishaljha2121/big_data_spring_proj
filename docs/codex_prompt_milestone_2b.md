# Codex Prompt: Milestone 2B Model Artifact Track

You are working on branch `feature/milestone-2b-model-artifacts` in `vishaljha2121/big_data_spring_proj`.

Implement Milestone 2B only: odds model training, conservative risk config, evaluation, and two-phase publication.

Allowed inputs:

- `data/features/point_features/`
- `data/features/match_features/`
- `data/baselines/player_baselines/`
- `data/features/feature_quality_report.json`
- `contracts/`

Do not use staging CSV.GZ files. Do not start Kafka, Spark streaming, FastAPI, React, or serving DB work.

Required outputs:

- `data/models/splits/*.json`
- `data/models/odds/staging/*`
- `data/models/odds/v1/*`
- `data/models/odds/latest.json`
- `data/models/risk/staging/*`
- `data/models/risk/v1/*`
- `data/models/risk/latest.json`
- `data/results/model_eval/*`
- model audit docs under `docs/`
- model tests under `tests/`

Contracts to obey:

- `contracts/odds_model_metadata_schema.json`
- `contracts/odds_model_feature_schema.json`
- `contracts/risk_model_metadata_schema.json`
- `contracts/risk_config_schema.json`
- `contracts/model_registry_schema.json`
- `contracts/model_eval_report_schema.json`

Quality gates:

- no match leakage across train/validation/test
- validation AUC >= 0.55
- test AUC >= 0.55
- validation Brier <= 0.30
- test Brier <= 0.30
- no fake anomaly labels
- no `latest.json` unless publication validation passes

Run:

```bash
.venv/bin/python scripts/validate_model_artifacts.py --models data/models --contracts contracts --results data/results/model_eval
.venv/bin/python -m pytest tests
```

Return PASSED/PARTIAL/FAILED with metrics and artifact paths.
