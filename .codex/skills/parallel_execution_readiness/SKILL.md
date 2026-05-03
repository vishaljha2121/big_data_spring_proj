# Skill: Parallel Execution Readiness

Use this skill when preparing this tennis big data repo for parallel milestone work.

## Rules

- Freeze contracts before splitting work.
- Keep Track A model files separate from Track B replay/Kafka files.
- Do not let either track modify stable Milestone 1B or 2A Parquet outputs.
- Do not create fake model artifacts or fake Kafka completion evidence.
- Validate source reports before declaring a handoff ready.

## Track Boundaries

- Track A owns model scripts, model artifacts, model eval reports, and model audit docs.
- Track B owns producer code, Kafka infra, replay validation, and replay audit docs.

## Merge Order

1. Merge `feature/milestone-2b-model-artifacts` after Track A validation passes.
2. Merge `feature/milestone-3a-replay-producer` after Track B validation passes.
3. Start `feature/milestone-3b-streaming-scorer` only after both tracks are merged.

## Validation Gate

Run:

```bash
.venv/bin/python scripts/validate_parallel_readiness.py
.venv/bin/python -m pytest tests
```
