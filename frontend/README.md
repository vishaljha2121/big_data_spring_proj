# CourtIQ Tennis Scoring Dashboard

Presentation-ready Vite/React dashboard for the file-backed FastAPI service. The default look is a clay-court inspired sports analytics control room with a frontend-only theme switcher for clay, hard, grass, and neutral themes.

## Run

Start the backend first:

```bash
.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000
```

Then run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

The dashboard uses `VITE_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.

## Build

```bash
cd frontend
npm run build
```

## Sections

- Hero and readiness badge
- Theme switcher
- KPI strip
- Selected match analytics
- Point probability timeline
- Risk summary
- Model artifact metadata
- Benchmark evidence
- Matches and scored events tables

## Configuration

Copy `.env.example` if needed:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The dashboard uses only documented endpoints from `docs/api_contract.md`.

## Demo Language

- Point probabilities are not betting odds or match-win probabilities.
- Risk scores are statistical anomaly signals only, not proof of misconduct or match-fixing.
- Surface metadata is unavailable in the current sample, so the clay theme is a demo visual theme by default.
