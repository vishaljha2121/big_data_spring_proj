# Centre Court Analytics Frontend

Presentation-ready Vite/React application for the file-backed FastAPI service. Milestone 4F pivots the single dashboard into a Centre Court Analytics product shell with sidebar navigation, multiple page modules, and a premium tennis analytics visual system.

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

## Product Shell

- Analytics: Dashboard, Match Browser, Players, Player Comparison, Tournaments, Surface Analytics, Rankings
- Replay: Replay Center, Point Timeline, Replay Manifest
- ML Model: Prediction Center, Model Performance
- Data Ops: Data Explorer, Validation, Pipeline Monitor, Reports

Real data comes from the documented FastAPI endpoints. Pages that need unsupported backend data are clearly labeled as planned or sample-derived.

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
- Player and ranking summaries are sample-derived from the local scored replay sample, not official ATP rankings.
