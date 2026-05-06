# Mockup To API Mapping

| Page | Mockup Intent | Current API Source | Status | Implementation Decision |
| --- | --- | --- | --- | --- |
| Dashboard | Executive overview of tennis analytics, scoring, model, replay, validation, and reports | `/api/summary`, `/api/models/current`, `/api/benchmarks/latest`, `/api/risk/summary`, `/api/matches`, `/api/scored-events` | Real now | API-backed KPI grid, featured match, prediction preview, pipeline quality, recent matches, risk signals, and reports |
| Match Browser | Browse and inspect tennis matches | `/api/matches`, `/api/matches/{synthetic_match_id}`, `/api/matches/{synthetic_match_id}/events` | Real now | Searchable match table with selected match detail and navigation actions |
| Players | Player directory and profile summaries | Derived from `/api/matches` and selected event rows | Partial / sample-derived | Show sample-derived appearances and risk exposure only; not official player profiles |
| Player Comparison | Compare two players | Derived from `/api/matches` and `/api/matches/{id}/events` | Partial / sample-derived | Compare selected match players using local sample events and clearly label scope |
| Tournaments | Tournament explorer | No current endpoint | Planned | Planned module card; do not invent official tournament metadata |
| Surface Analytics | Surface-level insights | No reliable surface coverage in current data | Planned / blocked | Show surface metadata blocker and visual-theme note only |
| Rankings | Player ranking table | Derived from `/api/matches` and event appearances | Partial / sample-derived | Show local sample ranking only; label as not official ATP ranking |
| Replay Center | Replay control-room view | `/api/matches/{id}/events`, `/api/benchmarks/latest`, `/api/summary` | Real now | Show local replay dry-run status, selected match stream, and court-inspired visualization |
| Point Timeline | Chronological point events | `/api/matches/{id}/events` | Real now | Show scored points with replay order, server, point probability, and risk bucket |
| Replay Manifest | Replay manifest details | Artifact exists in `data/replay/manifests/`; no dedicated frontend API endpoint | Partial / artifact-backed | Show validated artifact status and planned API endpoint note |
| Prediction Center | Prediction workflow | `/api/models/current`, `/api/matches/{id}/events` | Real now | Reframe as point scoring center; avoid match-winner or betting claims |
| Model Performance | Model and benchmark metrics | `/api/models/current`, `/api/benchmarks/latest` | Real now | Show model type, target, AUC, Brier, feature count, schema hash, and benchmark evidence |
| Data Explorer | Validated artifact inventory | `/api/summary` plus documented project constants | Real now / documented | Show validated outputs and mark constants as project-summary figures |
| Validation | Validation status board | `/health`, `/ready`, `/api/summary`, generated reports | Real now | Show API, model, scored events, replay, feature, frontend, and preflight validation statuses |
| Pipeline Monitor | Local pipeline runtime evidence | `/api/benchmarks/latest`, `/api/summary`, `/ready` | Real now | Show JSONL scorer throughput, latency, model load time, API status, and Kafka limitation |
| Reports | Audit and submission docs | Static repo document list | Real now | Show filenames and descriptions; browser does not fetch local Markdown files |

## Truthfulness Rules

- Point probabilities are point-level outputs, not betting odds.
- Risk scores are statistical anomaly signals for review, not proof of misconduct or match-fixing.
- Rankings are sample-derived unless an official rankings source is added later.
- Surface analytics remain blocked until reliable surface metadata is available.
- Kafka runtime is not presented as executed in the local validation path.
