# Tennis Scoring Dashboard

Minimal Vite/React dashboard for the file-backed FastAPI service.

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

## Build

```bash
cd frontend
npm run build
```

## Configuration

Copy `.env.example` if needed:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The dashboard uses only documented endpoints from `docs/api_contract.md`.
