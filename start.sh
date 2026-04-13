#!/usr/bin/env bash
# start.sh — launch the KV server in the background.
#
# Usage:
#   ./start.sh [--host HOST] [--port PORT]
#
# Defaults: host=127.0.0.1  port=8000
#
# The script is idempotent: it does nothing if the service is already running.
# Logs (uvicorn + application) are appended to logs/kv_server.log.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${KV_HOST:-127.0.0.1}"
PORT="${KV_PORT:-8000}"
PID_FILE="$SCRIPT_DIR/kv_server.pid"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/kv_server.log"

# Parse optional --host / --port arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host) HOST="$2"; shift 2 ;;
        --port) PORT="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# Check if already running
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "KV server is already running (PID $PID)."
        exit 0
    else
        echo "Stale PID file found (PID $PID no longer alive). Removing..."
        rm -f "$PID_FILE"
    fi
fi

mkdir -p "$LOG_DIR"

echo "Starting KV server on $HOST:$PORT ..."
cd "$SCRIPT_DIR"

nohup uvicorn app.main:app \
    --host "$HOST" \
    --port "$PORT" \
    >> "$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"
echo "KV server started (PID $(cat "$PID_FILE"))."
echo "Logs: $LOG_FILE"
