# CourtIQ File Inventory

Source repo: `https://github.com/Yashu2903/CourtIQ`

Canonical repo: `https://github.com/vishaljha2121/big_data_spring_proj`

CourtIQ was cloned under `external_sources/CourtIQ/` for inspection only. Runtime paths were not blindly copied into the canonical repo.

## Summary

- Files seen: 17
- Frontend files detected: none
- Backend/API files detected: none
- Model training files detected: none
- Kafka/replay files detected: yes
- Generated data files detected: none

## File Inventory

| File | Category | Language / Framework | Purpose | Classification | Suggested action |
| --- | --- | --- | --- | --- | --- |
| `.gitignore` | repo hygiene | text | Ignore local env/cache/generated data | Conflicting / obsolete | Ignore; canonical `.gitignore` wins |
| `LICENSE` | legal | text | MIT license | Useful reference only | Preserve repo attribution context only |
| `contracts/curated_point_schema.json` | contract | JSON Schema | Curated point schema | Conflicting / obsolete | Ignore; canonical contract wins |
| `contracts/data_quality_report_schema.json` | contract | JSON Schema | Data quality report schema | Conflicting / obsolete | Ignore; canonical contract wins |
| `contracts/match_feature_schema.json` | contract | JSON Schema | Match feature schema | Conflicting / obsolete | Ignore; canonical contract wins |
| `contracts/match_metadata_schema.json` | contract | JSON Schema | Match metadata schema | Conflicting / obsolete | Ignore; canonical contract wins |
| `contracts/player_baseline_schema.json` | contract | JSON Schema | Player baseline schema | Conflicting / obsolete | Ignore; canonical contract wins |
| `contracts/point_event_schema.json` | contract | JSON Schema | Kafka point event schema | Conflicting / obsolete | Preserve mismatch evidence under `external_review/` |
| `contracts/point_feature_schema.json` | contract | JSON Schema | Point feature schema | Conflicting / obsolete | Ignore; canonical contract wins |
| `contracts/replay_manifest_schema.json` | contract | JSON Schema | Replay manifest row schema | Conflicting / obsolete | Ignore; canonical contract wins |
| `data/quarantine/README.md` | data note | Markdown | Quarantine folder note | Useful reference only | Ignore; canonical Milestone 1B quarantine docs already exist |
| `data/staging/cleaned_csv/README.md` | data note | Markdown | Staging cleaned CSV note | Conflicting / obsolete | Ignore; future tracks must not use staging inputs |
| `docker-compose.processing.yml` | infra | Docker Compose | Single-node Kafka container | Reusable with adaptation | Preserve as reference for Track B |
| `docs/replay_producer_audit.md` | docs | Markdown | Replay producer audit | Useful reference only | Preserve as reference; do not adopt completion claims |
| `infra/local/kafka_setup.sh` | infra | Bash / Kafka CLI | Topic creation script | Reusable with adaptation | Preserve as reference for Track B |
| `producer/replay_producer.py` | replay | Python / pandas / kafka-python / jsonschema | Manifest-to-Kafka producer | Reusable with adaptation | Preserve as reference; not contract-compatible yet |
| `scripts/validate_replay_producer.py` | replay validation | Python / kafka-python / jsonschema | Kafka validation consumer | Reusable with adaptation | Preserve as reference; not run in canonical validation yet |

## Classification Counts

- Directly reusable: 0
- Reusable with adaptation: 4
- Useful reference only: 3
- Conflicting / obsolete: 10
- Unknown: 0

## Key Compatibility Notes

- CourtIQ does not contain frontend assets, model code, notebooks, or generated data.
- CourtIQ replay code uses `kafka-python`, while the canonical repo has intentionally not added Kafka runtime dependencies yet.
- CourtIQ point event schema includes fields such as `match_id`, `year`, `slam`, `surface`, `rally_length`, and serve speed fields. The canonical frozen Kafka point event contract intentionally emits raw replay manifest fields and excludes model/sparse metadata assumptions.
- CourtIQ topic names use `tennis.point.events`; canonical Milestone 2.5 topic config freezes `tennis-point-events`.
- CourtIQ replay audit claims producer testing with 20 events. That evidence is not canonical because Milestone 3A has not been executed in this repo.
