#!/bin/bash
# 校园代码智能助手 - 一键重启（幂等，确保端口不冲突）
# 用法: bash cloud-deploy/scripts/restart_services.sh
set -u
APP_ROOT=/opt/campus-assistant
REPO_DIR=$APP_ROOT/repo
LOGDIR=$APP_ROOT/logs
mkdir -p "$LOGDIR"

echo "[1/4] 停止可能占用端口的旧进程..."
systemctl stop campus-mcp campus-backend campus-frontend 2>/dev/null
pkill -f "[h]ttp_server.py" 2>/dev/null
pkill -f "[u]vicorn app:app" 2>/dev/null
pkill -f "[v]ite --host 127.0.0.1 --port 5180" 2>/dev/null
sleep 2

echo "[2/4] 校验端口已释放..."
for port in 8766 8000 5180; do
  if ss -ltn 2>/dev/null | grep -q ":$port "; then
    echo "  端口 $port 仍被占用, 强制释放"
    fuser -k ${port}/tcp 2>/dev/null || true
    sleep 1
  fi
done

echo "[3/4] 通过 systemd 启动三服务..."
systemctl daemon-reload 2>/dev/null
systemctl enable --now campus-mcp campus-backend campus-frontend 2>&1 | tail -3

echo "[4/4] 等待就绪并自检..."
sleep 18
systemctl is-active campus-mcp campus-backend campus-frontend
echo "--- 后端健康检查 ---"
curl -s --max-time 5 http://127.0.0.1:8000/api/health || echo "health 暂未就绪, 请稍后重试"
