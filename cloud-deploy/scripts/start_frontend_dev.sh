#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/campus-assistant}"
REPO_DIR="${REPO_DIR:-$APP_ROOT/repo}"

cd "$REPO_DIR/ai-coding-app/frontend"
npm install
npm run dev
