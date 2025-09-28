#!/usr/bin/env bash
set -euo pipefail

PID_DIR=".pids"

if [ ! -d "$PID_DIR" ]; then
  echo "No PID directory found; nothing to stop."
  exit 0
fi

for f in "$PID_DIR"/*.pid; do
  [ -e "$f" ] || continue
  pid=$(cat "$f")
  if kill -0 "$pid" 2>/dev/null; then
    echo "Stopping PID $pid from $f"
    kill "$pid"
    sleep 0.2
  else
    echo "PID $pid not running"
  fi
  rm -f "$f"
done

echo "Stopped processes and removed PID files."
