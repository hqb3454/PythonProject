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
  echo "Neither dnf nor yum was found. Please install Python and Node.js manually."
  exit 1
fi

sudo mkdir -p "$APP_ROOT/models"
sudo chown -R "$USER":"$USER" "$APP_ROOT"

sudo "$PKG_MANAGER" install -y python3 python3-pip curl ca-certificates tar xz

if ! python3 -m venv --help >/dev/null 2>&1; then
  sudo "$PKG_MANAGER" install -y python3-venv || true
fi

install_node_binary() {
  local node_version="${NODE_VERSION:-22.20.0}"
  local node_dist="node-v${node_version}-linux-x64"
  local node_archive="/tmp/${node_dist}.tar.xz"
  local node_url="https://nodejs.org/dist/v${node_version}/${node_dist}.tar.xz"

  echo "Installing Node.js ${node_version} from official binary package..."
  curl -fsSL "$node_url" -o "$node_archive"
  sudo rm -rf "/opt/${node_dist}"
  sudo tar -xJf "$node_archive" -C /opt
  sudo ln -sf "/opt/${node_dist}/bin/node" /usr/local/bin/node
  sudo ln -sf "/opt/${node_dist}/bin/npm" /usr/local/bin/npm
  sudo ln -sf "/opt/${node_dist}/bin/npx" /usr/local/bin/npx
}

if ! command -v node >/dev/null 2>&1 || ! node -e "process.exit(Number(process.versions.node.split('.')[0]) >= 22 ? 0 : 1)"; then
  if curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -; then
    sudo "$PKG_MANAGER" install -y nodejs
  else
    echo "NodeSource does not support this OS release. Falling back to Node.js official binary."
    install_node_binary
  fi
fi

node --version
npm --version

python3 -m venv "$APP_ROOT/venv"
"$APP_ROOT/venv/bin/python" -m pip install --upgrade pip
"$APP_ROOT/venv/bin/python" -m pip install -r "$REPO_DIR/cloud-deploy/requirements-server.txt"
"$APP_ROOT/venv/bin/python" -c "import importlib.metadata as m; print('mcp', m.version('mcp'))"

echo "APP_ROOT=$APP_ROOT"
echo "REPO_DIR=$REPO_DIR"
echo "Python venv: $APP_ROOT/venv"
echo "Next: prepare models under $APP_ROOT/models"
