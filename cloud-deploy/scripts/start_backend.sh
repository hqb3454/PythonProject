#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/campus-assistant}"
REPO_DIR="${REPO_DIR:-$APP_ROOT/repo}"
export RAG_MCP_URL="${RAG_MCP_URL:-http://127.0.0.1:8766/mcp}"
export API_HOST="${API_HOST:-127.0.0.1}"
export API_PORT="${API_PORT:-8000}"
export API_RELOAD="${API_RELOAD:-false}"

cd "$REPO_DIR/ai-coding-app/backend"
"$APP_ROOT/venv/bin/python" -m uvicorn app:app --host "$API_HOST" --port "$API_PORT" --workers 4
