#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$REPO_DIR/ai-coding-app/frontend"

npm install
npm run build

echo "Frontend built at $REPO_DIR/ai-coding-app/frontend/dist"
