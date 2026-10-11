#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/campus-assistant}"
REPO_DIR="${REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

sudo mkdir -p "$APP_ROOT/models"
sudo chown -R "$USER":"$USER" "$APP_ROOT"

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nginx curl ca-certificates

if ! command -v node >/dev/null 2>&1 || ! node -e "process.exit(Number(process.versions.node.split('.')[0]) >= 22 ? 0 : 1)"; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

python3 -m venv "$APP_ROOT/venv"
"$APP_ROOT/venv/bin/python" -m pip install --upgrade pip
"$APP_ROOT/venv/bin/python" -m pip install -r "$REPO_DIR/cloud-deploy/requirements-server.txt"

echo "APP_ROOT=$APP_ROOT"
echo "REPO_DIR=$REPO_DIR"
echo "Python venv: $APP_ROOT/venv"
echo "Next: prepare models under $APP_ROOT/models"
