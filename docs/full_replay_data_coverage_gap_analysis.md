# Full Replay & Data Coverage Gap Analysis

**Milestone:** 5B — Full Match Replay Experience, Data Coverage Fix, and Real Match Labeling  
**Date:** 2026-05-06  
**Status:** Analysis Complete

---

## 1. Why Replay Center Does Not Currently Replay Point-by-Point

The `ReplayCenterPage.jsx` component contains a `playing` state toggle and a "Play"/"Pause" button, but **no actual playback logic**:

- `useState(false)` tracks `playing`, but no `useEffect` or interval advances a `currentIndex`.
- The "Step +1 Point" button has no `onClick` handler — it is a static `<button>` element.
- There is no `currentIndex`, no `playbackSpeed`, no interval timer.
- The "Point Event Stream" card hard-codes `events.slice(0, 9)` — it always shows the first 9 events regardless of playback state.
- The progress bar is fixed at `value={100}`, not driven by replay position.

**Root cause:** The replay UI was scaffolded as a visual mockup but never wired to actual playback state management.

---

## 2. Why Dashboard Exposes Only ~1,000 Scored Events and ~6 Matches

The data limitation is a **serving/sample path issue**, not a model issue:

| Layer | Current Behavior | Impact |
|-------|-----------------|--------|
| **Scoring script** (`run_scoring_from_jsonl.py`) | Scores from `sample_events.jsonl` with `--max-events 1000` | Only 1,000 events are scored |
| **API config** (`config.py`) | Points to `scored_events_sample.jsonl` (1,000 events, 6 matches) | API can only serve what is loaded |
| **API data loader** (`data_loader.py`) | Builds `match_summaries` only from scored sample | No replay manifest data exposed |
| **Frontend client** (`client.js`) | `loadDashboardData` fetches `limit=100` for events and matches | Even if more data existed, frontend only requests 100 items |
| **PointTimelinePage** | `events.slice(0, 80)` | Arbitrarily caps visible events |
| **ReplayCenterPage** | `events.slice(0, 9)` | Shows only first 9 events |

The replay manifest contains **1,917,672 events across 10,464 matches** but is never loaded by the API.

---

## 3. Why Synthetic IDs Appear Prominently

- The replay manifest assigns `synthetic_match_id` values (e.g., `synthetic_match_0003f30d4e692463`) as the primary key.
- The existing `matchLabel()` helper in `pageUtils.jsx` does use player names when available: `${match.player_a} vs ${match.player_b}`.
- However, `compactReplayId()` is displayed prominently alongside or before player names in several views.
- The `MatchBrowserPage` table shows "Replay ID" as a full column.
- Match detail cards show replay IDs with visual prominence equal to or greater than player names.

**Root cause:** The UI treats synthetic replay IDs as primary identifiers rather than secondary metadata.

---

## 4. Why This Is Not Primarily a Model-Training Problem

The model artifacts are **functional and validated**:

- `data/models/odds/latest.json` — published HistGradientBoosting classifier, test AUC validated.
- `data/models/risk/latest.json` — published risk configuration with statistical deviation scoring.
- `StreamScorer` correctly scores point events using these artifacts.
- The 1,000-event scored sample validates correctly.

The issues are all in the **data serving and UI layer**:

1. The scoring script was run with `--max-events 1000` on a subset, not on complete matches.
2. The API loads only the scored sample, not the full replay manifest.
3. The frontend replay page has no playback logic.
4. Retraining the model would not add more match data to the dashboard.

---

## 5. What Data Exists in the Repo but Is Not Exposed by API

| Dataset | Location | Records | Currently Exposed |
|---------|----------|---------|-------------------|
| Full replay manifest | `data/replay/manifests/replay_manifest_v1.parquet` | 1,917,672 events / 10,464 matches | ❌ Not loaded by API |
| Scored events sample | `data/results/streaming_scoring/scored_events_sample.jsonl` | 1,000 events / 6 matches | ✅ Loaded by API |
| Replay manifest report | `data/replay/manifests/replay_manifest_v1.json` | Metadata only | ❌ Not exposed |
| Sample replay events | `data/results/replay_dry_run/sample_events.jsonl` | ~1,000 events | ❌ Not directly exposed |

---

## 6. What Will Be Fixed in This Milestone

1. **Replay Center playback** — Implement real `currentIndex`, interval timer, Step +1, Step −1, Restart, speed selector, and progress tracking.
2. **Data coverage** — Add replay manifest loading to API; create full-demo scored dataset with complete matches.
3. **API endpoints** — Add `/api/data/coverage`, `/api/replay/matches`, `/api/replay/matches/{id}/events`.
4. **Match labeling** — Make player names the primary match identity; demote synthetic IDs to secondary metadata chips.
5. **Dashboard coverage** — Show data coverage information; support replay catalog browsing.
6. **Documentation** — Update runbook, API contract, README, CODEX to explain the fix.

---

## 7. What Will Remain Out of Scope

- **Full 1.9M event scoring** — Scoring all replay events is computationally expensive and unnecessary for demo.
- **Model retraining** — Not needed; model artifacts are valid.
- **PostgreSQL/Redis** — File-backed serving is sufficient for demo.
- **Kafka live streaming** — Replay is historical playback, not live.
- **Tournament/surface metadata** — Not available in curated singles data.
- **Real-time data ingestion** — Out of scope for academic demo.
