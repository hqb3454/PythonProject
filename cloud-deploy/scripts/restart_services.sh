#!/bin/bash
# 校园代码智能助手 - 一键重启（幂等，确保端口不冲突）
# 架构：MCP(8766) 和后端(8000) 由 systemd 托管；
#       前端已由 nginx 接管 5180（静态 dist + 反代 /api），campus-frontend(Vite) 已停用。
# 用法: bash cloud-deploy/scripts/restart_services.sh
# 提示: 改动前端源码后，先执行 npm run build 再跑本脚本（或单独 reload nginx）。
set -u
APP_ROOT=/opt/campus-assistant
REPO_DIR=$APP_ROOT/repo
LOGDIR=$APP_ROOT/logs
mkdir -p "$LOGDIR"

echo "[1/4] 停止可能占用端口的旧进程..."
systemctl stop campus-mcp campus-backend 2>/dev/null
systemctl stop campus-frontend 2>/dev/null   # Vite 已被 nginx 取代，保持停止
pkill -f "[h]ttp_server.py" 2>/dev/null
pkill -f "[u]vicorn app:app" 2>/dev/null
sleep 2

echo "[2/4] 校验端口已释放..."
for port in 8766 8000 5180; do
  if ss -ltn 2>/dev/null | grep -q ":$port "; then
    echo "  端口 $port 仍被占用, 强制释放"
    fuser -k ${port}/tcp 2>/dev/null || true
    sleep 1
  fi
done

echo "[3/4] 通过 systemd 启动服务（MCP + 后端 + nginx）..."
systemctl daemon-reload 2>/dev/null
systemctl disable campus-frontend 2>/dev/null || true
systemctl enable --now campus-mcp campus-backend nginx 2>&1 | tail -3

echo "[4/4] 等待就绪并自检..."
sleep 18   # MCP 加载模型约需 10-15s
systemctl is-active campus-mcp campus-backend nginx
echo "--- 通过 nginx 统一入口做健康检查 ---"
curl -s --max-time 5 http://127.0.0.1:5180/api/health || echo "health 暂未就绪, 请稍后重试"
