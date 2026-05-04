# Frontend Dashboard Audit

## Purpose

Milestone 4D turns the functional Milestone 4B dashboard into a presentation-ready tennis analytics interface over the documented FastAPI service. It keeps the same API contract and local file-backed demo path while improving visual hierarchy, spacing, chart readability, table quality, and demo language.

## Stack

- Vite 2
- React 17
- Plain CSS with CSS custom properties
- Frontend-only court theme system
- Custom SVG probability chart
- No backend architecture changes

## Redesign Summary

- Added a premium app shell with clay-court gradient background and subtle court-line motif.
- Added sticky top navigation anchors for Overview, Matches, Risk, Model, and Benchmark.
- Replaced the raw top section with a hero panel containing project title, readiness badge, theme switcher, scored event count, and disclaimer chips.
- Replaced stacked sections with a dashboard grid: KPI strip, large match analytics card, right-side insight rail, and lower data tables.
- Rebuilt the point probability timeline as a large SVG chart with 0-100% scale, 50% reference line, gradient stroke, and risk markers.
- Reworked tables with sticky headers, ID pills, probability bars, risk badges, hover/selected states, and contained horizontal overflow.
- Reworked risk/model/benchmark panels to avoid raw JSON and concatenated labels.

## Theme System

The dashboard supports frontend-only themes under `frontend/src/theme/surfaceThemes.js`:

- `clay`: default Roland Garros-inspired clay-court demo theme
- `hard`: blue hard-court theme
- `grass`: green grass-court theme
- `neutral`: neutral slate theme

Current source data has unavailable or incomplete surface metadata. When selected match surface is missing, the dashboard defaults to the clay-court demo theme and shows:

> Surface metadata unavailable for this sample; dashboard shown in clay-court demo theme.

The user-facing theme switcher works even when surface metadata is unavailable.

## API Dependencies

The frontend uses `VITE_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`, and calls only endpoints documented in `docs/api_contract.md`:

- `/health`
- `/ready`
- `/api/summary`
- `/api/scored-events`
- `/api/matches`
- `/api/matches/{synthetic_match_id}`
- `/api/matches/{synthetic_match_id}/events`
- `/api/risk/summary`
- `/api/risk/events`
- `/api/models/current`
- `/api/benchmarks/latest`

## Sections Implemented

- Hero/status section
- Theme switcher
- KPI strip
- Selected match analytics panel
- Point probability timeline
- Recent point events
- Risk summary and top risk events
- Model artifact panel
- Benchmark evidence panel
- Matches table
- Scored events table

## How To Run

Preferred:

```bash
bash scripts/run_full_demo.sh
```

Manual fallback:

```bash
.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000

cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Validation

```bash
cd frontend
npm install
npm run build
cd ..

.venv/bin/python scripts/validate_frontend_build.py
```

The script checks required files, runs `npm run build`, and writes `data/results/frontend_validation/frontend_validation_report.json`.

## Screenshots To Capture Manually

- Hero + KPI strip
- Selected match analytics card
- Point probability timeline
- Right-side risk summary
- Model metadata panel
- Benchmark evidence panel
- Matches table
- Scored events table
- FastAPI docs

## Demo Talking Points

- The UI is a local tennis analytics dashboard backed by validated FastAPI responses.
- Probabilities are point-level probabilities, not match-win probabilities or betting odds.
- Risk scores are statistical anomaly signals for review only. They are not proof of misconduct or match-fixing.
- Surface metadata is unavailable in the current sample, so the clay-court visual theme is a demo presentation theme, not a data claim.

## Milestone 4E — Narrative Polish

Milestone 4E adds the final frontend narrative polish pass:

### KPI Strip Reordering

The top KPI strip was reordered from an engineering-debug layout to a meaningful demo narrative:

| Old Order | New Order |
|---|---|
| Scored Events | Validated Scored Events |
| Unique Matches | Matches in Demo |
| Odds Model | Point Model AUC |
| Risk Config | Calibration (Brier) |
| Events/sec | Scoring Throughput |
| p95 Latency | p95 Latency |

Risk Config was removed from the top KPI strip and remains visible in the Model Metadata panel.

### Humanized Labels

All underscore/raw technical labels have been replaced with human-readable equivalents:

- `return_point_win_pct` → "Return point win %"
- `serve_point_win_pct` → "Serve point win %"
- `label_point_winner_is_player_a` → "Player A point winner label"
- `fake_labels_used=false` → "No fake labels used"
- `baseline_deviation_score_v1` → "Baseline deviation score"
- `HistGradientBoostingClassifier` → "HistGradientBoosting classifier"

Humanization utilities are implemented in `frontend/src/utils/formatting.js`.

### Replay ID Handling

Synthetic match IDs are now secondary when real player names exist:

- Match titles show "Player A vs Player B" as primary
- Replay IDs appear as small labeled pills: "Replay: synthetic_ma…692463"
- Applies to: matches table, scored events table, match analytics panel, risk overview

### Model Comparison Panel

A new `ModelComparisonPanel.jsx` component provides honest context comparing our point-level model to public tennis prediction references. It includes:

- Our validated metrics (test AUC, Brier, throughput)
- Three public reference benchmarks (TennisBets-style, SportBot-style, CourtCruncher-style)
- A fair comparison verdict explaining why direct comparison is not valid
- A "what would make it comparable" roadmap

Full analysis documented in `docs/model_comparison_analysis.md`.

## Limitations

- The dashboard reads the static local scored sample through the API.
- No authentication or production deployment is included.
- Kafka runtime remains optional and was not required for this demo path.
- The court-surface theme switcher is frontend-only because reliable surface metadata is unavailable.

