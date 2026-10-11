# 云主机部署说明

本目录用于把 `校园代码智能助手` 迁移到云主机运行。建议云主机使用 Linux/Ubuntu，公网访问走 Nginx 的 80 端口，后端和 MCP 只监听云主机本机 `127.0.0.1`。

你的云主机信息：

- 公网 IPv4：`36.213.141.60`
- 内网 IPv4：`192.168.0.64`
- IPv6：`2409:8c85:2021:bb29:f8c5:27cd:ac1b:42d3`

## 关键结论

- 浏览器里的 `127.0.0.1` 指的是访问者自己的电脑，不是云主机，所以前端不能把 API 地址写死成 `http://127.0.0.1:8000`。
- 后端访问 MCP 时可以继续用 `http://127.0.0.1:8766/mcp`，因为后端和 MCP 都跑在同一台云主机上。
- 云主机对外建议只开放 `80` 或 `443`，不要把 MCP 的 `8766` 暴露到公网。
- ChromaDB 不需要单独下载安装数据库服务，它是 Python 包和本地持久化目录。第一次检索时会根据 `mcp-rag/kb` 自动构建 `mcp-rag/knowledge`。
- 模型权重不要进 Git。云主机上把模型下载/上传到 `/opt/campus-assistant/models`，然后设置 `RAG_MODEL_DIR=/opt/campus-assistant/models`。

## 推荐运行端口

| 组件 | 监听地址 | 端口 | 是否公网开放 |
| --- | --- | --- | --- |
| Nginx | `0.0.0.0` | `80` | 是 |
| FastAPI 后端 | `127.0.0.1` | `8000` | 否 |
| HTTP MCP RAG | `127.0.0.1` | `8766` | 否 |
| Vue 静态文件 | Nginx root | 无独立端口 | 通过 80 访问 |

最终访问地址：

```text
http://36.213.141.60/
```

## 云主机目录约定

```text
/opt/campus-assistant/
  repo/                         # git clone 后的项目根目录
  venv/                         # Python 虚拟环境
  models/
    text2vec-base-chinese/
    mmarco-mMiniLMv2-L12-H384-v1/
```

## 部署步骤

### 1. 登录云主机

```bash
ssh root@36.213.141.60
```

### 2. 安装基础依赖

建议把仓库 clone 到固定目录，方便 systemd 服务直接使用：

```bash
sudo mkdir -p /opt/campus-assistant
sudo chown -R "$USER":"$USER" /opt/campus-assistant
git clone <你的仓库地址> /opt/campus-assistant/repo
cd /opt/campus-assistant/repo
```

你的云主机镜像是 BC-Linux 21.10 U4 64 位，优先执行：

```bash
bash cloud-deploy/scripts/install_bclinux.sh
```

如果是 Ubuntu，执行：

```bash
bash cloud-deploy/scripts/install_ubuntu.sh
```

两个脚本都只是安装 Python、Node.js、Nginx 和 Python 依赖，不会上传模型，也不会自动修改云平台安全组。

### 3. 准备模型

方式 A：从本地上传模型目录到云主机：

先在云主机上创建目录：

```bash
ssh root@36.213.141.60 "mkdir -p /opt/campus-assistant/models"
```

然后在 Windows PowerShell 本地执行：

```powershell
scp -r "F:/PythonProject/models/text2vec-base-chinese" root@36.213.141.60:/opt/campus-assistant/models/
scp -r "F:/PythonProject/models/mmarco-mMiniLMv2-L12-H384-v1" root@36.213.141.60:/opt/campus-assistant/models/
```

如果你的云主机不是 root 用户，把 `root@36.213.141.60` 改成你的用户名。

上传完成后，在云主机验证：

```bash
cd /opt/campus-assistant/repo
source /opt/campus-assistant/venv/bin/activate
python cloud-deploy/scripts/verify_models.py
```

方式 B：在云主机下载模型。模型源可能因网络环境不同而变化，脚本只给出 Hugging Face/SentenceTransformers 常见下载方式：

```bash
source /opt/campus-assistant/venv/bin/activate
python cloud-deploy/scripts/download_models.py
```

如果下载失败，优先使用方式 A 上传本地已有模型。

### 4. 配置环境变量

```bash
sudo cp cloud-deploy/campus-assistant.env.example /etc/campus-assistant.env
sudo nano /etc/campus-assistant.env
```

默认值已经适合本机部署，通常只需要确认 `RAG_MODEL_DIR=/opt/campus-assistant/models`。

### 5. 构建前端

```bash
bash cloud-deploy/scripts/build_frontend.sh
```

前端默认使用 `/api` 调后端，云端由 Nginx 转发，不需要把公网 IP 写入 Vue 代码。

### 6. 安装 systemd 服务

```bash
sudo cp cloud-deploy/systemd/campus-mcp.service /etc/systemd/system/
sudo cp cloud-deploy/systemd/campus-backend.service /etc/systemd/system/
chmod +x cloud-deploy/scripts/*.sh
sudo systemctl daemon-reload
sudo systemctl enable --now campus-mcp campus-backend
```

检查状态：

```bash
systemctl status campus-mcp
systemctl status campus-backend
```

### 7. 配置 Nginx

如果你的云主机 80 端口因为 ICP 备案暂时不能用，可以先用 8080 端口测试：

```bash
sudo cp cloud-deploy/nginx/campus-assistant-8080.conf /etc/nginx/conf.d/campus-assistant.conf
sudo nginx -t
sudo systemctl reload nginx
```

然后在云平台安全组新增入向规则：TCP `8080`，授权对象可以先填你的当前公网 IP，测试阶段不要必须开放给所有人。访问：

```text
http://36.213.141.60:8080/
```

如果 8080 也受限，可以用 SSH 隧道在本地测试，不需要开放 HTTP 端口：

```bash
ssh -L 18080:127.0.0.1:8000 root@36.213.141.60
```

然后本地浏览器访问后端健康检查：

```text
http://127.0.0.1:18080/api/health
```

如果以后 80 端口可用，再使用正式 80 配置：

```bash
sudo cp cloud-deploy/nginx/campus-assistant.conf /etc/nginx/sites-available/campus-assistant.conf
sudo ln -sf /etc/nginx/sites-available/campus-assistant.conf /etc/nginx/sites-enabled/campus-assistant.conf
sudo nginx -t
sudo systemctl reload nginx
```

然后访问：

```text
http://36.213.141.60/
```

### 8. 验证

```bash
python cloud-deploy/scripts/smoke_test.py
```

也可以手动检查：

```bash
curl http://127.0.0.1:8000/api/health
curl http://36.213.141.60/api/health
```

## 关于在线模型

当前部署包默认使用本地 embedding 和 rerank 模型，原因是：

- 本地模型不依赖公网 API，演示更稳定。
- RAG 的向量维度和 ChromaDB 索引与 embedding 模型绑定，随意切换在线 embedding 模型需要重建向量库。
- rerank 在线化也需要额外 API key、费用和延迟控制。

如果后续要改在线模型，建议只把“大模型回答生成”接在线 API；embedding/rerank 仍保留本地模型，迁移风险最低。

## 防火墙建议

云平台安全组至少开放：

- `22`：SSH
- `80`：HTTP

如果没有 HTTPS，先不要开放 `443`。不要开放 `8000` 和 `8766`，它们只给 Nginx/后端本机访问。

你当前截图里的安全组只允许：

- TCP `22`：只允许 `112.3.215.73/32` 这个公网 IP SSH 登录。
- ICMP：允许所有 IP ping。

要从浏览器访问作品，还需要新增一条入向规则：TCP `80`，授权对象 `0.0.0.0/0`。如果以后配置 HTTPS，再新增 TCP `443`。
