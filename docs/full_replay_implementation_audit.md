# Full Replay Implementation Audit

**Milestone:** 5B  
**Date:** 2026-05-06  
**Status:** PASSED

---

## Summary

Milestone 5B fixes three product/demo issues without retraining the model or redesigning the architecture:

1. **Replay Center** now plays back matches point-by-point with real controls.
2. **Dashboard data coverage** expanded from 1,000 events / 6 matches to 9,000+ events / 50 matches.
3. **Match labeling** uses player names as primary identity, with synthetic IDs as secondary metadata.

---

## Root Causes

### Why Replay Was Not Playing
- `ReplayCenterPage.jsx` had a `playing` state toggle but no interval timer or `currentIndex`.
- The "Step +1 Point" button had no `onClick` handler.
- The event stream was hard-coded to `events.slice(0, 9)`.

### Why Only Limited Match Data Showed
- The scoring script ran with `--max-events 1000` on a small subset of replay events.
- The API config pointed to `scored_events_sample.jsonl` (1,000 events, 6 matches).
- The API data loader built match summaries only from loaded scored events.
- The full replay manifest (1.9M events, 10,464 matches) was never loaded by the API.

### Why Synthetic IDs Appeared
- The replay manifest assigns `synthetic_match_id` values as primary keys.
- While `matchLabel()` used player names, `compactReplayId()` had equal or greater visual prominence.
- No labeling hierarchy was enforced (player names first, IDs secondary).

### Why This Was Not a Model Problem
- Model artifacts (`odds/latest.json`, `risk/latest.json`) were functional and validated.
- The issue was entirely in the data serving path and UI layer.
- Retraining the model would not have added more matches to the dashboard.

---

## Changes Made

### Backend / API
| File | Change |
|------|--------|
| `api/app/config.py` | Added `replay_manifest_parquet`, `full_scored_events_jsonl`, env var overrides |
| `api/app/data_loader.py` | Loads replay manifest from parquet, builds replay catalog, adds `data_coverage()` |
| `api/app/repositories.py` | Added `ReplayRepository`, configurable `max_limit` in `paginate()` |
| `api/app/routes/replay.py` | New: `/api/replay/matches`, `/api/replay/matches/{id}/events` |
| `api/app/routes/benchmarks.py` | New: `/api/data/coverage` endpoint |
| `api/app/routes/matches.py` | Raised match events limit to 5000 |
| `api/app/main.py` | Registered replay router |

### Frontend
| File | Change |
|------|--------|
| `frontend/src/api/client.js` | Added `getDataCoverage()`, `getReplayMatches()`, `getReplayMatchEvents()` |
| `frontend/src/pages/ReplayCenterPage.jsx` | Full rewrite: interval playback, Step ±1, Restart, speed selector, progress bar, current point card |
| `frontend/src/pages/PointTimelinePage.jsx` | Removed 80-event slice, added "Show more" pagination |
| `frontend/src/pages/DashboardPage.jsx` | Added Data Coverage card, uses `displayMatchTitle` |
| `frontend/src/pages/MatchBrowserPage.jsx` | Added Scored/Catalog tabs, replay catalog browsing |
| `frontend/src/pages/pageUtils.jsx` | Added `displayMatchTitle`, `displayReplayId`, `displaySourceId`, `isRealPlayerName` |
| `frontend/src/utils/formatting.js` | Added `isRealPlayerName`, `displaySourceId`, enhanced `hasRealPlayers` |

### Scripts
| File | Change |
|------|--------|
| `scripts/generate_full_demo_scored_matches.py` | New: generates full-demo scored dataset from manifest |
| `scripts/run_full_demo.sh` | Auto-detects full demo file |
| `scripts/validate_api_contract.py` | Added new endpoint validation |

### Tests
| File | Tests |
|------|-------|
| `tests/test_data_coverage_api.py` | 4 tests for `/api/data/coverage` |
| `tests/test_replay_catalog_api.py` | 6 tests for `/api/replay/matches` |
| `tests/test_full_demo_scoring.py` | 3 tests for full-demo scored output |
| `tests/test_replay_player_ui.py` | 11 structural tests for ReplayCenterPage |

### Documentation
| File | Change |
|------|--------|
| `docs/full_replay_data_coverage_gap_analysis.md` | New: gap analysis |
| `docs/full_replay_implementation_audit.md` | This file |
| `docs/final_demo_runbook.md` | Added 5B section |
| `README.md` | Added 5B status, checklist items, endpoints |
| `CODEX.md` | Updated to 5B |

---

## Validation Results

| Gate | Status |
|------|--------|
| API contract validation | PASSED |
| Frontend build | PASSED |
| Frontend validation | PASSED |
| Pytest (94 tests) | PASSED |
| Full-demo scoring (50 matches) | PASSED |
| API validation with full demo data | PASSED |

---

## Model Decision

**The model was NOT retrained.** The existing published model artifacts were used to score additional matches from the replay manifest. This confirmed that the model works correctly — the issue was always in the data serving path, not the model.

---

## Remaining Limitations

1. Only 50 of 10,464 matches are scored in the full demo — configurable via `--max-matches`.
2. Feature builder resets per match; cross-match features are not available.
3. Surface metadata remains unavailable (0% coverage in source data).
4. Tournament metadata is not available in the curated singles data.
5. ATP rankings are sample-derived, not official.
6. Replay catalog browsing from the frontend loads manifest matches but cannot score them on-the-fly.
