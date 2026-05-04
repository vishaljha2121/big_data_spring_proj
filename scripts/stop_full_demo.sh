#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PID_DIR="${REPO_ROOT}/data/results/final_demo/pids"

stop_pid_file() {
  local pid_file="$1"
  local label="$2"
  if [[ ! -f "${pid_file}" ]]; then
    echo "${label}: no PID file"
    return 0
  fi
  local pid
  pid="$(cat "${pid_file}" 2>/dev/null || true)"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}" 2>/dev/null || true
    echo "${label}: stopped PID ${pid}"
  else
    echo "${label}: PID not running"
  fi
  rm -f "${pid_file}"
}

stop_pid_file "${PID_DIR}/frontend.pid" "frontend"
stop_pid_file "${PID_DIR}/api.pid" "api"
