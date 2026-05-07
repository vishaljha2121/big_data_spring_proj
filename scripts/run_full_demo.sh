#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

API_PORT="8000"
FRONTEND_PORT="5173"
SKIP_VALIDATION="0"
NO_FRONTEND_INSTALL="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-validation)
      SKIP_VALIDATION="1"
      shift
      ;;
    --no-frontend-install)
      NO_FRONTEND_INSTALL="1"
      shift
      ;;
    --api-port)
      API_PORT="${2:?--api-port requires a value}"
      shift 2
      ;;
    --frontend-port)
      FRONTEND_PORT="${2:?--frontend-port requires a value}"
      shift 2
      ;;
    -h|--help)
      cat <<USAGE
Usage: bash scripts/run_full_demo.sh [options]

Options:
  --skip-validation        Skip API contract validation before launch.
  --no-frontend-install    Do not run npm install before starting Vite.
  --api-port PORT          Backend port, default 8000.
  --frontend-port PORT     Frontend port, default 5173.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

PYTHON="${REPO_ROOT}/.venv/bin/python"
LOG_DIR="${REPO_ROOT}/data/results/final_demo/logs"
PID_DIR="${REPO_ROOT}/data/results/final_demo/pids"
API_LOG="${LOG_DIR}/api.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"
API_PID_FILE="${PID_DIR}/api.pid"
FRONTEND_PID_FILE="${PID_DIR}/frontend.pid"

mkdir -p "${LOG_DIR}" "${PID_DIR}"

cleanup() {
  set +e
  if [[ -f "${FRONTEND_PID_FILE}" ]]; then
    FRONTEND_PID="$(cat "${FRONTEND_PID_FILE}" 2>/dev/null || true)"
    if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
      kill "${FRONTEND_PID}" 2>/dev/null || true
    fi
    rm -f "${FRONTEND_PID_FILE}"
  fi
  if [[ -f "${API_PID_FILE}" ]]; then
    API_PID="$(cat "${API_PID_FILE}" 2>/dev/null || true)"
    if [[ -n "${API_PID}" ]] && kill -0 "${API_PID}" 2>/dev/null; then
      kill "${API_PID}" 2>/dev/null || true
    fi
    rm -f "${API_PID_FILE}"
  fi
}

trap cleanup INT TERM EXIT

require_file() {
  if [[ ! -e "${REPO_ROOT}/$1" ]]; then
    echo "Missing required file: $1" >&2
    exit 1
  fi
}

wait_for_url() {
  local url="$1"
  local label="$2"
  local attempts=60
  for _ in $(seq 1 "${attempts}"); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  echo "${label} did not become ready at ${url}" >&2
  return 1
}

cd "${REPO_ROOT}"

# Auto-detect full demo scored dataset for broader coverage
if [[ -z "${TENNIS_SCORED_EVENTS_PATH:-}" ]]; then
  FULL_DEMO="${REPO_ROOT}/data/results/streaming_scoring/scored_events_demo_full.jsonl"
  if [[ -f "${FULL_DEMO}" ]]; then
    export TENNIS_SCORED_EVENTS_PATH="${FULL_DEMO}"
    echo "Using full demo scored dataset: ${FULL_DEMO}"
  fi
fi

if [[ ! -x "${PYTHON}" ]]; then
  echo "Missing executable Python venv at ${PYTHON}. Create it and install requirements first." >&2
  exit 1
fi

require_file "scripts/run_api.py"
require_file "api/app/main.py"
require_file "frontend/package.json"
require_file "frontend/src/App.jsx"
require_file "data/models/odds/latest.json"
require_file "data/models/risk/latest.json"
require_file "data/results/replay_dry_run/sample_events.jsonl"

if [[ ! -f "data/results/streaming_scoring/scored_events_sample.jsonl" ]]; then
  echo "Scored event output missing; regenerating 1000-event local scoring sample."
  "${PYTHON}" scripts/run_scoring_from_jsonl.py \
    --input-events data/results/replay_dry_run/sample_events.jsonl \
    --odds-latest data/models/odds/latest.json \
    --risk-latest data/models/risk/latest.json \
    --output-jsonl data/results/streaming_scoring/scored_events_sample.jsonl \
    --output-parquet data/results/streaming_scoring/scored_events_sample.parquet \
    --max-events 1000 \
    --report data/results/streaming_scoring/scoring_run_report.json
fi

if [[ "${SKIP_VALIDATION}" != "1" ]]; then
  echo "Validating API contract before launch..."
  "${PYTHON}" scripts/validate_api_contract.py
fi

echo "Starting FastAPI on http://127.0.0.1:${API_PORT} ..."
"${PYTHON}" scripts/run_api.py --host 127.0.0.1 --port "${API_PORT}" >"${API_LOG}" 2>&1 &
echo "$!" > "${API_PID_FILE}"
if ! wait_for_url "http://127.0.0.1:${API_PORT}/health" "FastAPI /health"; then
  echo "FastAPI failed to start. Last API log lines:" >&2
  tail -40 "${API_LOG}" >&2 || true
  exit 1
fi
if ! wait_for_url "http://127.0.0.1:${API_PORT}/ready" "FastAPI /ready"; then
  echo "FastAPI readiness failed. Last API log lines:" >&2
  tail -40 "${API_LOG}" >&2 || true
  exit 1
fi

if [[ "${NO_FRONTEND_INSTALL}" != "1" && ! -d "frontend/node_modules" ]]; then
  echo "Installing frontend dependencies..."
  (cd frontend && npm install)
fi

echo "Starting Vite dashboard on http://127.0.0.1:${FRONTEND_PORT} ..."
if [[ ! -x "frontend/node_modules/.bin/vite" ]]; then
  echo "Missing frontend/node_modules/.bin/vite. Run npm install or omit --no-frontend-install." >&2
  exit 1
fi
(cd frontend && VITE_API_BASE_URL="http://127.0.0.1:${API_PORT}" ./node_modules/.bin/vite --host 127.0.0.1 --port "${FRONTEND_PORT}") >"${FRONTEND_LOG}" 2>&1 &
echo "$!" > "${FRONTEND_PID_FILE}"
if ! wait_for_url "http://127.0.0.1:${FRONTEND_PORT}" "Frontend"; then
  echo "Frontend failed to start. Last frontend log lines:" >&2
  tail -40 "${FRONTEND_LOG}" >&2 || true
  exit 1
fi

cat <<URLS

Demo is running.
Backend:  http://127.0.0.1:${API_PORT}
API docs: http://127.0.0.1:${API_PORT}/docs
Frontend: http://127.0.0.1:${FRONTEND_PORT}

Logs:
  ${API_LOG}
  ${FRONTEND_LOG}

Press Ctrl+C to stop both processes, or run:
  bash scripts/stop_full_demo.sh

URLS

wait
