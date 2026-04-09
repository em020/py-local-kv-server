#!/usr/bin/env bash
# restart.sh — restart the KV server managed by start.sh.
#
# Usage:
#   ./restart.sh [--host HOST] [--port PORT]
#
# If the server is running, it is stopped first using the PID from kv_server.pid.
# The script then delegates startup to start.sh with the same arguments.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/kv_server.pid"
START_SCRIPT="$SCRIPT_DIR/start.sh"

if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping KV server (PID $PID) ..."
        kill "$PID"

        for _ in {1..50}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 0.1
        done

        if kill -0 "$PID" 2>/dev/null; then
            echo "KV server did not stop after SIGTERM." >&2
            exit 1
        fi
    else
        echo "Stale PID file found (PID $PID no longer alive)."
    fi
    rm -f "$PID_FILE"
else
    echo "KV server is not running. Starting a new instance."
fi

if [[ $# -gt 0 ]]; then
    exec "$START_SCRIPT" "$@"
fi

exec "$START_SCRIPT"
