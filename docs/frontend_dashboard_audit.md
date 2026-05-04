# Frontend Dashboard Audit

## Purpose

Milestone 4B adds a minimal presentation-ready dashboard over the documented FastAPI service. It demonstrates the end-to-end local path from replay events to scored outputs and API-backed visualization.

## Stack

- Vite 2
- React 17
- Plain CSS
- No backend architecture changes

The conservative package versions support the local Node `v14.15.4` environment.

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

- Backend readiness/status banner
- Summary cards
- Scored events table
- Matches table
- In-page match detail panel
- Risk summary and top risk events
- Model metadata panel
- Benchmark evidence panel

## How To Run

```bash
.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000

cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Validation

```bash
.venv/bin/python scripts/validate_frontend_build.py
```

The script checks required files, installs dependencies if needed, runs `npm run build`, and writes `data/results/frontend_validation/frontend_validation_report.json`.

## Screenshots To Capture Manually

- Full dashboard top with readiness and summary cards
- Scored events table
- Match detail panel with probability timeline
- Risk summary panel
- Model metadata and benchmark panels

## Demo Talking Points

- Probabilities are point-level probabilities, not match-win probabilities or betting odds.
- Risk scores are statistical anomaly signals for review only. They are not proof of misconduct or match-fixing.
- The dashboard is backed by validated local FastAPI responses and does not require Kafka, PostgreSQL, or Redis.

## Limitations

- The dashboard reads the static local scored sample through the API.
- No authentication or production deployment is included.
- Kafka runtime remains optional and was not required for this demo path.
