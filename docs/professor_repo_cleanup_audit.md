# Professor Repo Cleanup Audit

## 1. Current Repo Strengths

- The project has an end-to-end validated path from curated tennis point data to FastAPI and a React dashboard.
- Big Data scale is backed by concrete artifacts: 1,922,136 curated point rows, 10,508 curated matches, 1,917,672 replay events, and 10,464 replay matches.
- Model artifacts are published and validated under `data/models/` and `data/results/model_eval/`.
- Replay, local scoring, Kafka, Spark Structured Streaming, API, frontend, and final-demo evidence reports are preserved under `data/results/`.
- `scripts/run_full_demo.sh` provides a one-command local product demo.
- `scripts/run_streaming_demo.sh` provides an optional Kafka/Spark runtime path when Docker/Spark dependencies are available.
- The frontend labels unsupported pages as planned or sample-derived, which avoids overclaiming official rankings, surface analytics, or betting outputs.

## 2. Current Repo Navigation Problems

- The previous root `README.md` read like a milestone diary instead of a grading-facing landing page.
- The `docs/` folder contains many useful audits, but there was no single index grouping them by purpose.
- The `presentation/` folder had multiple deck/script versions without a strong recommendation in the primary README.
- Historical implementation prompts and next-step planning docs remain useful for traceability but can distract a professor from the final evidence path.
- Root-level historical files such as `2_week_execution_plan.md`, `implementation_plan/`, and `data_analysis.txt` are not the current grading source of truth.
- `presentation/node_modules/` and `frontend/node_modules/` are heavy local dependency folders, but moving or deleting them was outside this cleanup because validation/demo scripts may depend on the current local environment.

## 3. Files/Folders Essential For Grading

| Path | Why it matters |
| --- | --- |
| `README.md` | Primary professor-facing landing page |
| `CODEX.md` | Current project rules, guardrails, and validation gates |
| `docs/final_report.md` | Final 5-section report |
| `docs/README.md` | Documentation index |
| `docs/final_demo_runbook.md` | Demo instructions and talk track |
| `docs/professor_grading_checklist.md` | 5-10 minute review checklist |
| `presentation/README.md` | Presentation index and recommended final files |
| `presentation/CourtIQ_Final_Presentation_v2.pptx` | Recommended final deck |
| `presentation/speaker_notes_v2.md` | Recommended speaker script |
| `scripts/run_full_demo.sh` | Primary local demo launcher |
| `scripts/final_preflight_check.py` | Final preflight validation |
| `scripts/smoke_test_full_demo.py` | API/frontend smoke test |
| `scripts/validate_api_contract.py` | API validation |
| `scripts/validate_frontend_build.py` | Frontend validation |
| `scripts/validate_model_artifacts.py` | Model artifact validation |
| `scripts/validate_feature_layer.py` | Feature/data layer validation |
| `api/` | FastAPI serving layer |
| `frontend/` | Dashboard source |
| `streaming/` | Local scoring runtime |
| `spark_streaming/` | Spark Structured Streaming implementation |
| `producer/` | Replay producer |
| `infra/` | Kafka/Docker setup |
| `contracts/` | Schema and API contracts |
| `data/results/` | Preserved validation and demo evidence |

## 4. Files/Folders Historical Or Reference Only

| Path | Status |
| --- | --- |
| `2_week_execution_plan.md` | Historical plan; not current source of truth |
| `implementation_plan/` | Historical planning material |
| `docs/codex_prompt_milestone_2b.md` | Historical implementation prompt |
| `docs/codex_prompt_milestone_3a.md` | Historical implementation prompt |
| `docs/next_implementation_steps.md` | Earlier next-step planning |
| `docs/post_merge_next_phase_plan.md` | Earlier phase plan |
| `docs/deprecated_plan_notice.md` | Notice for deprecated planning material |
| `external_review/courtiq/` | Reference-only preserved CourtIQ materials |
| `external_sources/` | Ignored external-source area |
| `presentation/CourtIQ_Final_Presentation.pptx` | Historical first presentation deck |
| `presentation/speaker_notes.md` | Historical first speaker script |
| `presentation/assets/` | Historical first-version presentation assets |

## 5. Generated Artifacts That Should Be Preserved

- `data/curated/`
- `data/features/`
- `data/baselines/`
- `data/replay/`
- `data/models/`
- `data/results/replay_dry_run/`
- `data/results/streaming_scoring/`
- `data/results/model_eval/`
- `data/results/api_validation/`
- `data/results/frontend_validation/`
- `data/results/final_demo/`
- `data/results/kafka_runtime/`
- `data/results/spark_streaming/`
- `data/checkpoints/spark_streaming_scorer/`
- `contracts/api_openapi_snapshot.json`
- `contracts/api_response_examples.json`
- `presentation/assets_v2/`

These artifacts are evidence for final grading and should not be deleted during cleanup.

## 6. Stale Docs Or Duplicate Milestone Claims

- The old root README was the main stale navigation problem because it listed milestones rather than answering grading questions directly.
- Several historical docs still mention earlier implementation stages. They are preserved but now indexed as historical/reference docs in `docs/README.md`.
- `docs/final_submission_checklist.md` still contains older final Git command examples for a previous milestone branch. It remains useful as a validation checklist, but it should not be treated as the current branch instruction.
- `CODEX.md` says the next priority is screenshots, report, and slides. This remains compatible with Milestone 6A because the work is final cleanup/report packaging, not model or architecture changes.

## 7. Cleanup Actions Taken

- Rewrote `README.md` into a concise professor-facing landing page.
- Added `docs/README.md` as the documentation index grouped by grading purpose.
- Updated `presentation/README.md` to identify the recommended final deck, speaker script, screenshots, and regeneration command.
- Added `docs/final_report.md` using the requested 5-section report structure.
- Added `docs/professor_grading_checklist.md` with demo checklist and click path.
- Added this cleanup audit at `docs/professor_repo_cleanup_audit.md`.
- Added a root `.gitignore` entry for dependency folders (`node_modules/`) so generated frontend/presentation dependencies do not obscure review status.
- Preserved limitations in the README and report: no betting odds, no match-fixing proof, no official rankings, no claimed production deployment, and no claimed surface analytics.

## 8. Cleanup Actions Intentionally Not Taken

- Did not delete or move generated data/results artifacts because they are grading evidence and may be referenced by validation scripts.
- Did not move root historical files because moving them could break links or distract from validation in a time-sensitive final pass.
- Did not delete `frontend/node_modules/` or `presentation/node_modules/` because local build/capture workflows may rely on the current installed dependency state.
- Did not rename presentation decks because existing links and submission packaging may depend on those filenames.
- Did not change API, model, streaming, feature, or frontend logic.
- Did not retrain models or regenerate data artifacts.
- Did not alter `scripts/run_full_demo.sh` or validation scripts.
