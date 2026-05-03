# CourtIQ Integration Audit

## Verdict

Milestone 2.6 passed as an audit and preservation merge. CourtIQ contains useful replay/Kafka reference work, but no file was promoted into canonical runtime paths because the useful code requires adaptation to the frozen contracts and current workstream boundaries.

## Inputs Inspected

Canonical source of truth:

- `README.md`
- `CODEX.md`
- `docs/parallel_workstream_handoff.md`
- `docs/next_implementation_steps.md`
- `docs/codex_prompt_milestone_2b.md`
- `docs/codex_prompt_milestone_3a.md`
- `contracts/`
- `scripts/`
- `producer/`
- `infra/`
- `tests/`
- `data/results/parallel_readiness_report.json`

CourtIQ source:

- `external_sources/CourtIQ/`

## Useful Assets Preserved

The following CourtIQ files were preserved under `external_review/courtiq/preserved_reference/`:

- `producer/replay_producer.py`
- `scripts/validate_replay_producer.py`
- `infra/local/kafka_setup.sh`
- `docker-compose.processing.yml`
- `docs/replay_producer_audit.md`
- `contracts/point_event_schema.json`

These are reference-only until Track B adapts them to the canonical contracts.

## Compatibility Findings

### Replay Producer

CourtIQ has a concrete Kafka replay producer structure with manifest row validation, point-event transformation, DLQ routing, dry-run support, replay speed control, and Kafka publication. This is useful for Milestone 3A.

It was not merged into `producer/replay_producer.py` because:

- it imports `kafka.KafkaProducer`, but the canonical repo has not started Kafka runtime work;
- it emits a broader point event contract than the frozen canonical `contracts/point_event_schema.json`;
- it uses topic defaults that differ from `infra/kafka/topic_config.json`;
- it derives `year` and `slam` from match IDs, which is outside the current frozen point event contract;
- it includes sparse/unavailable fields such as `surface`, `rally_length`, and serve speed as emitted event fields.

### Replay Validation Consumer

CourtIQ has a useful Kafka consumer validation pattern with schema validation and DLQ checks.

It was not merged into canonical runtime because:

- it requires a live Kafka broker;
- it assumes CourtIQ topic names;
- canonical Milestone 3A has not started;
- the existing canonical `scripts/validate_replay_producer.py` remains a non-claiming scaffold.

### Kafka Infra

CourtIQ has a single-node Kafka Compose file and a topic creation script.

These were preserved as reference only because canonical `infra/kafka/topic_config.json` already freezes the topic contract and the current branch must not start Kafka runtime.

### Contracts

CourtIQ contracts overlap with canonical contracts. The canonical `contracts/` directory wins. CourtIQ's point event contract was preserved only as evidence of mismatch.

### Docs

CourtIQ's replay producer audit is useful as a future writing reference, but it claims Kafka testing outcomes that are not canonical. It was preserved under external review and not merged into `docs/` as an authoritative audit.

## Rejected or Ignored Assets

- CourtIQ data staging notes were rejected because future canonical work must not use staging CSV inputs.
- CourtIQ duplicate schema files were ignored because canonical contracts are already frozen.
- CourtIQ `.gitignore` was ignored except for adding `external_sources/` to the canonical ignore rules.

## Merge Actions

- Preserved selected CourtIQ replay/Kafka assets under `external_review/courtiq/preserved_reference/`.
- Added this audit and `docs/courtiq_file_inventory.md`.
- Added `data/results/courtiq_integration_report.json`.
- Added `tests/test_courtiq_integration_guardrails.py`.
- Updated `README.md`, `CODEX.md`, and `docs/next_implementation_steps.md`.

## Guardrails

- Do not use CourtIQ assets unless this audit lists them as approved reference.
- Do not replace canonical contracts with CourtIQ contracts.
- Do not promote preserved replay/Kafka code into runtime paths until Milestone 3A.
- Do not treat CourtIQ replay audit claims as canonical validation evidence.

## Final Status

PASSED. CourtIQ was safely audited and useful assets were preserved without changing validated Milestone 1B, 2A, or 2.5 outputs.
