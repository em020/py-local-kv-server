#!/usr/bin/env bash
# stop.sh — stop the KV server managed by start.sh.
#
# Usage:
#   ./stop.sh
#
# The script stops the process recorded in kv_server.pid and removes stale PID
# state when the managed process is no longer running.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/kv_server.pid"

if [[ ! -f "$PID_FILE" ]]; then
    echo "KV server is not running."
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "Stale PID file found (PID $PID no longer alive). Removing..."
    rm -f "$PID_FILE"
    exit 0
fi

echo "Stopping KV server (PID $PID) ..."
kill "$PID"

for _ in {1..50}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        rm -f "$PID_FILE"
        echo "KV server stopped."
        exit 0
    fi
    sleep 0.1
done

echo "KV server did not stop after SIGTERM." >&2
exit 1
