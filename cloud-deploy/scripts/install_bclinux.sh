#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/campus-assistant}"
REPO_DIR="${REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

PKG_MANAGER=""
if command -v dnf >/dev/null 2>&1; then
  PKG_MANAGER="dnf"
elif command -v yum >/dev/null 2>&1; then
  PKG_MANAGER="yum"
else
  echo "Neither dnf nor yum was found. Please install Python, Node.js and Nginx manually."
  exit 1
fi

sudo mkdir -p "$APP_ROOT/models"
sudo chown -R "$USER":"$USER" "$APP_ROOT"

sudo "$PKG_MANAGER" install -y python3 python3-pip nginx curl ca-certificates

if ! python3 -m venv --help >/dev/null 2>&1; then
  sudo "$PKG_MANAGER" install -y python3-venv || true
fi

if ! command -v node >/dev/null 2>&1 || ! node -e "process.exit(Number(process.versions.node.split('.')[0]) >= 22 ? 0 : 1)"; then
  curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -
  sudo "$PKG_MANAGER" install -y nodejs
fi

python3 -m venv "$APP_ROOT/venv"
"$APP_ROOT/venv/bin/python" -m pip install --upgrade pip
"$APP_ROOT/venv/bin/python" -m pip install -r "$REPO_DIR/cloud-deploy/requirements-server.txt"

echo "APP_ROOT=$APP_ROOT"
echo "REPO_DIR=$REPO_DIR"
echo "Python venv: $APP_ROOT/venv"
echo "Next: prepare models under $APP_ROOT/models"
