# Next Implementation Steps

Milestone 2.6 status: **PASSED**.

CourtIQ was audited and useful replay/Kafka reference assets were preserved under `external_review/courtiq/`. No CourtIQ runtime code was promoted into canonical execution paths.

## Parallel Work Can Start

The repository remains ready for two-person parallel work after contract freeze and CourtIQ audit:

- Track A: Milestone 2B model artifacts
- Track B: Milestone 3A replay / Kafka infrastructure

## Track A Next Step

Create branch `feature/milestone-2b-model-artifacts` and use `docs/codex_prompt_milestone_2b.md`.

Track A should implement odds model training, conservative risk config, evaluation reports, two-phase publication, model registry metadata, and model artifact tests.

Team A should not use CourtIQ assets because CourtIQ did not contain model training or risk scoring code.

## Track B Next Step

Create branch `feature/milestone-3a-replay-producer` and use `docs/codex_prompt_milestone_3a.md`.

Track B should implement local Kafka setup, topic creation, replay producer, validation consumer, event contract validation, ordering checks, and replay audit docs.

Track B may consult `external_review/courtiq/preserved_reference/`, but any implementation must adapt to canonical contracts and topic config.

## Merge Order

1. Merge `feature/integrate-courtiq-assets` after Milestone 2.6 review.
2. Merge `feature/milestone-2b-model-artifacts` after Track A validation passes.
3. Merge `feature/milestone-3a-replay-producer` after Track B validation passes.
4. Start `feature/milestone-3b-streaming-scorer` only after both tracks merge.

## Remaining Blockers

- Surface-specific features and baselines remain blocked until metadata improves.
- Rally-length features remain sparse and should not be primary MVP model inputs.
- ATP match bridge features remain blocked until a reliable point-to-match join is validated.
- Spark streaming/API/frontend work remains blocked until both Track A and Track B pass.
- CourtIQ assets are reference-only unless explicitly approved in `docs/courtiq_integration_audit.md`.
