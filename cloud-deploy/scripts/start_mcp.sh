#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/campus-assistant}"
REPO_DIR="${REPO_DIR:-$APP_ROOT/repo}"
export RAG_MODEL_DIR="${RAG_MODEL_DIR:-$APP_ROOT/models}"
export MCP_HOST="${MCP_HOST:-127.0.0.1}"
export MCP_PORT="${MCP_PORT:-8766}"

cd "$REPO_DIR/mcp-rag"
"$APP_ROOT/venv/bin/python" http_server.py "$MCP_PORT"
