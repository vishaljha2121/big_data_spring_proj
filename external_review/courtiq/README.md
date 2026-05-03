# CourtIQ External Review

This folder preserves selected files from `https://github.com/Yashu2903/CourtIQ` for Milestone 2.6 review.

The preserved files are not canonical runtime code. They are reference material for the future Milestone 3A replay/Kafka track and must not be used unless the compatibility findings in `docs/courtiq_integration_audit.md` are addressed.

## Preserved Assets

- `preserved_reference/producer/replay_producer.py`: useful replay producer structure, but incompatible with the canonical frozen point event contract.
- `preserved_reference/scripts/validate_replay_producer.py`: useful validation-consumer structure, but requires Kafka and topic naming adaptation.
- `preserved_reference/infra/local/kafka_setup.sh`: useful topic creation reference, but topic names differ from canonical config.
- `preserved_reference/docker-compose.processing.yml`: useful single-node Kafka reference, but not promoted to canonical runtime yet.
- `preserved_reference/docs/replay_producer_audit.md`: useful narrative reference, but it claims completed Kafka testing that is not completed in the canonical repo.
- `preserved_reference/contracts/point_event_schema.json`: preserved only as evidence of contract mismatch.

## Canonical Rule

The canonical repo contracts under `contracts/` remain authoritative.
