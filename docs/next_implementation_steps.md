# Next Implementation Steps

Milestone 2.5 status: **PASSED**.

## Parallel Work Can Start

The repository is ready for two-person parallel work after contract freeze:

- Track A: Milestone 2B model artifacts
- Track B: Milestone 3A replay / Kafka infrastructure

## Track A Next Step

Create branch `feature/milestone-2b-model-artifacts` and use `docs/codex_prompt_milestone_2b.md`.

Track A should implement odds model training, conservative risk config, evaluation reports, two-phase publication, model registry metadata, and model artifact tests.

## Track B Next Step

Create branch `feature/milestone-3a-replay-producer` and use `docs/codex_prompt_milestone_3a.md`.

Track B should implement local Kafka setup, topic creation, replay producer, validation consumer, event contract validation, ordering checks, and replay audit docs.

## Merge Order

1. Merge `feature/milestone-2b-model-artifacts` after Track A validation passes.
2. Merge `feature/milestone-3a-replay-producer` after Track B validation passes.
3. Start `feature/milestone-3b-streaming-scorer` only after both tracks merge.

## Remaining Blockers

- Surface-specific features and baselines remain blocked until metadata improves.
- Rally-length features remain sparse and should not be primary MVP model inputs.
- ATP match bridge features remain blocked until a reliable point-to-match join is validated.
- Spark streaming/API/frontend work remains blocked until both Track A and Track B pass.
