# Post-Merge Next Phase Plan

## 1. What CourtIQ Assets Were Merged?

No CourtIQ runtime code was merged into canonical execution paths. The canonical architecture and frozen contracts remain unchanged.

The only canonical updates are audit, guardrail, and reference-preservation files:

- `docs/courtiq_file_inventory.md`
- `docs/courtiq_integration_audit.md`
- `data/results/courtiq_integration_report.json`
- `external_review/courtiq/`
- `tests/test_courtiq_integration_guardrails.py`

## 2. What CourtIQ Assets Were Preserved as Reference-Only?

Preserved under `external_review/courtiq/preserved_reference/`:

- Kafka replay producer reference
- Kafka validation consumer reference
- Kafka topic setup reference
- Docker Compose Kafka reference
- Replay producer audit reference
- CourtIQ point event schema as mismatch evidence

## 3. What CourtIQ Assets Were Rejected and Why?

- Duplicate contracts were rejected because canonical contracts are already frozen.
- Staging data notes were rejected because future work must not use staging CSV inputs.
- Kafka runtime scripts were not promoted because Milestone 3A has not started.
- CourtIQ replay audit claims were not adopted because canonical validation has not run Kafka replay.

## 4. Is the Canonical Repo Still Ready for Parallel Work?

Yes. Milestone 2.5 readiness remains intact. Track A and Track B can proceed independently after this branch merges.

## 5. Should Team A Proceed With Milestone 2B?

Yes. Team A should proceed on `feature/milestone-2b-model-artifacts` using `docs/codex_prompt_milestone_2b.md`.

Team A should not use CourtIQ assets because CourtIQ did not contain model training code or risk scoring code.

## 6. Should Team B Proceed With Milestone 3A?

Yes. Team B should proceed on `feature/milestone-3a-replay-producer` using `docs/codex_prompt_milestone_3a.md`.

Team B may consult `external_review/courtiq/preserved_reference/`, but must adapt any useful ideas to:

- `contracts/point_event_schema.json`
- `contracts/replay_manifest_schema.json`
- `infra/kafka/topic_config.json`
- existing non-claiming canonical stubs

## 7. New Dependencies or Conflicts

No new runtime dependencies were added.

CourtIQ references `kafka-python`, but it was not added to canonical requirements because Kafka runtime work remains blocked until Milestone 3A.

## 8. Exact Next Branch Plan

Team A:

- Branch: `feature/milestone-2b-model-artifacts`
- Prompt: `docs/codex_prompt_milestone_2b.md`

Team B:

- Branch: `feature/milestone-3a-replay-producer`
- Prompt: `docs/codex_prompt_milestone_3a.md`

Later integration:

- Branch: `feature/milestone-3b-streaming-scorer`

## Merge Order

1. Merge this Milestone 2.6 branch.
2. Merge Team A after Milestone 2B validation passes.
3. Merge Team B after Milestone 3A validation passes.
4. Start Milestone 3B integration only after both tracks pass.
