# Documentation Index

This index is the shortest path through the repo for final grading. Start with the project status, run the demo commands, then use the audits as evidence for each layer.

## Project Status and Runbooks

| File | Purpose |
| --- | --- |
| `final_project_status.md` | Current implementation status and evidence summary |
| `final_demo_runbook.md` | One-command demo path, fallback commands, and demo talk track |
| `final_submission_checklist.md` | Submission checklist, validation commands, and known limitations |
| `professor_grading_checklist.md` | Professor-facing checklist and demo click path |
| `professor_repo_cleanup_audit.md` | Milestone 6A cleanup audit and intentional non-moves |
| `final_report.md` | Polished 5-section final report |

## Data Engineering

| File | Purpose |
| --- | --- |
| `milestone_1B_results.md` | Cleaned/curated layer results |
| `data_layer_audit.md` | Data-layer audit trail |
| `data_cleaning_decisions.md` | Cleaning decisions and handling notes |
| `feature_engineering_audit.md` | Point-in-time feature engineering evidence |
| `baseline_generation_audit.md` | Player baseline generation evidence |
| `replay_manifest_audit.md` | Replay manifest generation and validation |

## Modeling

| File | Purpose |
| --- | --- |
| `model_training_audit.md` | Published point-level model metrics and leakage prevention |
| `model_publication_audit.md` | Model artifact publication and registry details |
| `model_feature_selection.md` | Feature selection notes |
| `risk_scoring_methodology.md` | Conservative risk signal methodology |
| `model_comparison_analysis.md` | Honest comparison context for point-level vs match-level models |
| `outcome_label_derivation_audit.md` | Outcome label derivation evidence |

## Replay and Streaming

| File | Purpose |
| --- | --- |
| `replay_producer_audit.md` | Replay producer evidence |
| `streaming_scorer_audit.md` | Local JSONL streaming scorer audit |
| `spark_structured_streaming_audit.md` | Spark Structured Streaming architecture and evidence |
| `kafka_local_setup.md` | Local Kafka setup |
| `kafka_runtime_validation.md` | Kafka runtime validation evidence |
| `streaming_demo_runbook.md` | Optional streaming demo runbook |
| `full_replay_implementation_audit.md` | Replay Center and full-demo scored-data implementation audit |
| `full_replay_data_coverage_gap_analysis.md` | Replay/data coverage gap analysis and limits |

## API and Frontend

| File | Purpose |
| --- | --- |
| `api_contract.md` | FastAPI endpoints, artifacts, and API limitations |
| `local_serving_layer_audit.md` | File-backed serving-layer audit |
| `frontend_dashboard_audit.md` | React dashboard implementation and validation |
| `mockup_pivot_analysis.md` | Product-shell pivot analysis |
| `mockup_to_api_mapping.md` | Mapping from product pages to real API coverage |

## Validation and Final Demo

| File | Purpose |
| --- | --- |
| `final_build_freeze_audit.md` | Final build freeze evidence |
| `milestone_3b_validation_report.md` | Local streaming scorer validation |
| `parallel_workstream_handoff.md` | Parallel contract handoff |
| `event_contract_handoff.md` | Event contract handoff |
| `scoring_output_contract.md` | Scored event output contract |

Primary machine-readable evidence lives under `data/results/`, especially:

- `data/results/final_demo/final_preflight_report.json`
- `data/results/final_demo/full_demo_smoke_report.json`
- `data/results/api_validation/api_validation_report.json`
- `data/results/frontend_validation/frontend_validation_report.json`
- `data/results/model_eval/`
- `data/results/streaming_scoring/`
- `data/results/kafka_runtime/`
- `data/results/spark_streaming/`

## Presentation Materials

| File | Purpose |
| --- | --- |
| `../presentation/README.md` | Presentation index and recommended final deck |
| `../presentation/CourtIQ_Final_Presentation_v2.pptx` | Recommended final slide deck |
| `../presentation/speaker_notes_v2.md` | Recommended final speaker script |
| `../presentation/assets_v2/` | Final diagrams and screenshots |

## Historical and Reference Docs

| File | Purpose |
| --- | --- |
| `deprecated_plan_notice.md` | Notes that older planning docs are historical |
| `next_implementation_steps.md` | Earlier next-step planning, not the current grading source of truth |
| `post_merge_next_phase_plan.md` | Historical phase plan |
| `codex_prompt_milestone_2b.md` | Historical implementation prompt |
| `codex_prompt_milestone_3a.md` | Historical implementation prompt |
| `courtiq_integration_audit.md` | CourtIQ reference audit |
| `courtiq_file_inventory.md` | CourtIQ preserved-reference inventory |

Historical files are preserved for traceability. Use this index, the root `README.md`, and `docs/final_report.md` as the professor-facing entry points.
