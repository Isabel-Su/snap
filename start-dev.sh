#!/usr/bin/env bash
set -euo pipefail

# start-dev.sh
# Starts: react dev-proxy, expo web, and python services (app, PythonImpactCharts, Scroller)
# Usage: ./start-dev.sh [--port PROXY_PORT]
# Example: ./start-dev.sh --port 3001

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REACT_DIR="${ROOT_DIR}/reactFrontEnd"
LOG_DIR="${ROOT_DIR}/logs"
PID_DIR="${ROOT_DIR}/.pids"
PROXY_PORT=3001

# parse optional args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PROXY_PORT="$2"; shift 2 ;;
    *)
      echo "Unknown arg: $1"; exit 1 ;;
  esac
done

mkdir -p "$LOG_DIR" "$PID_DIR"

echo "Starting dev environment"

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  echo "Activated .venv"
else
  echo "No .venv found at .venv/bin/activate — continuing without venv activation"
fi

# Start dev-proxy
echo "Starting dev-proxy (PORT=${PROXY_PORT})..."
(cd "$REACT_DIR" && PORT=${PROXY_PORT} npm run dev-proxy > "${LOG_DIR}/dev-proxy.log" 2>&1) &
pid=$!
echo $pid > "${PID_DIR}/dev-proxy.pid"
sleep 0.5

echo "Starting Expo web (expo start --web)..."

(cd "$REACT_DIR" && npm run web > "${LOG_DIR}/web.log" 2>&1) &
pid=$!
echo $pid > "${PID_DIR}/web.pid"

sleep 1

# Start Python services
echo "Starting Python services..."
python3 pulse_mock/app.py > "${LOG_DIR}/pulse_app.log" 2>&1 &
pid=$!
echo $pid > "${PID_DIR}/pulse_app.pid"
python3 pulse_mock/PythonImpactCharts.py > "${LOG_DIR}/impact.log" 2>&1 &
pid=$!
echo $pid > "${PID_DIR}/impact.pid"
python3 pulse_mock/Scroller.py > "${LOG_DIR}/scroller.log" 2>&1 &
pid=$!
echo $pid > "${PID_DIR}/scroller.pid"

sleep 0.5

# Print summary
echo "Started processes (PIDs written to ${PID_DIR}/):"
ls -l ${PID_DIR} || true

echo "Logs are in ${LOG_DIR}/ (tail -f them to watch output)"

echo "To stop everything: ./stop-dev.sh"
