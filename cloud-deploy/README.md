# 云主机 SSH 隧道测试部署说明

本目录用于把 `校园代码智能助手` 放到云主机上运行，但不开放 Web 公网端口。当前方案适合学习、测试和比赛前自测：

- 不使用 Nginx。
- 不使用 `80`、`8080`、`443`、`8443`。
- 云平台安全组只需要开放 `22`，用于 SSH/VSCode Remote SSH。
- Vue、FastAPI、MCP 都只监听云主机自己的 `127.0.0.1`。
- 你在本地电脑通过 SSH 隧道访问云主机里的 Vue 页面。

你的云主机信息：

- 公网 IPv4：`36.213.141.60`
- 内网 IPv4：`192.168.0.64`
- IPv6：`2409:8c85:2021:bb29:f8c5:27cd:ac1b:42d3`

## 运行结构

云主机内部运行：

```text
Vue dev server: 127.0.0.1:5180
FastAPI 后端:   127.0.0.1:8000
HTTP MCP RAG:   127.0.0.1:8766
```

你的本地电脑建立 SSH 隧道：

```text
本地 127.0.0.1:5180 -> 云主机 127.0.0.1:5180
本地 127.0.0.1:8000 -> 云主机 127.0.0.1:8000
```

然后你在本地浏览器打开：

```text
http://127.0.0.1:5180/
```

页面其实是云主机上的 Vue 服务返回的。

## 关于 `/api`

前端 Vue 代码默认请求 `/api`，例如：

```text
/api/health
/api/chat
/api/code/generate
```

在这个 SSH 隧道测试方案里，不需要 Nginx。Vue 开发服务器 Vite 会把 `/api` 转发到云主机内部的 FastAPI：

```text
Vue/Vite 127.0.0.1:5180
  -> /api
  -> FastAPI 127.0.0.1:8000
```

FastAPI 再访问 MCP：

```text
FastAPI 127.0.0.1:8000
  -> MCP 127.0.0.1:8766/mcp
```

## 目录约定

```text
/opt/campus-assistant/
  repo/                         # git clone 后的项目根目录
  venv/                         # Python 虚拟环境
  models/
    text2vec-base-chinese/
    mmarco-mMiniLMv2-L12-H384-v1/
```

`/opt` 不是必须，但适合放这种长期运行的应用。如果你只想临时测试，也可以放在 `/root/campus-assistant`，但要同步修改 `APP_ROOT`。

## 1. 登录云主机并 clone 项目

```bash
ssh root@36.213.141.60
```

```bash
sudo mkdir -p /opt/campus-assistant
sudo chown -R "$USER":"$USER" /opt/campus-assistant
git clone <你的仓库地址> /opt/campus-assistant/repo
cd /opt/campus-assistant/repo
```

如果你通过 VSCode Remote SSH 操作，也是在云主机终端里执行这些命令。

## 2. 安装运行依赖

你的镜像是 BC-Linux 21.10 U4 64 位，执行：

```bash
bash cloud-deploy/scripts/install_bclinux.sh
```

这个脚本不会安装 Linux 系统，也不会配置公网 Web 服务。它只安装：

- Python / pip / venv
- Node.js / npm
- curl / ca-certificates
- Python 依赖：FastAPI、MCP、ChromaDB、sentence-transformers 等

如果安装 Node.js 时出现 `This script is intended for RPM-based systems`，这是 NodeSource 没有识别 BC-Linux 发行版导致的。新版 `install_bclinux.sh` 会自动回退到 Node.js 官方二进制包安装。

如果是 Ubuntu，才使用：

```bash
bash cloud-deploy/scripts/install_ubuntu.sh
```

## 3. 上传本地模型

先在云主机上创建模型目录：

```bash
mkdir -p /opt/campus-assistant/models
```

然后在 Windows PowerShell 本地执行：

```powershell
scp -r "F:/PythonProject/models/text2vec-base-chinese" root@36.213.141.60:/opt/campus-assistant/models/
scp -r "F:/PythonProject/models/mmarco-mMiniLMv2-L12-H384-v1" root@36.213.141.60:/opt/campus-assistant/models/
```

如果 `scp` 慢，可以先压缩再上传：

```powershell
cd F:/PythonProject
tar -czf models.tar.gz models/text2vec-base-chinese models/mmarco-mMiniLMv2-L12-H384-v1
scp models.tar.gz root@36.213.141.60:/opt/campus-assistant/
```

云主机上解压：

```bash
cd /opt/campus-assistant
tar -xzf models.tar.gz
```

验证模型目录：

```bash
cd /opt/campus-assistant/repo
source /opt/campus-assistant/venv/bin/activate
python cloud-deploy/scripts/verify_models.py
```

## 4. 启动三个服务

终端 1：启动 MCP。

```bash
cd /opt/campus-assistant/repo
source /opt/campus-assistant/venv/bin/activate
export APP_ROOT=/opt/campus-assistant
export REPO_DIR=/opt/campus-assistant/repo
export RAG_MODEL_DIR=/opt/campus-assistant/models
bash cloud-deploy/scripts/start_mcp.sh
```

终端 2：启动 FastAPI。

```bash
cd /opt/campus-assistant/repo
source /opt/campus-assistant/venv/bin/activate
export APP_ROOT=/opt/campus-assistant
export REPO_DIR=/opt/campus-assistant/repo
bash cloud-deploy/scripts/start_backend.sh
```

终端 3：启动 Vue。

```bash
cd /opt/campus-assistant/repo
export APP_ROOT=/opt/campus-assistant
export REPO_DIR=/opt/campus-assistant/repo
bash cloud-deploy/scripts/start_frontend_dev.sh
```

## 5. 在本地电脑建立 SSH 隧道

在你自己的 Windows PowerShell 里执行：

```powershell
ssh -L 5180:127.0.0.1:5180 -L 8000:127.0.0.1:8000 root@36.213.141.60
```

这个 SSH 窗口保持打开。然后本地浏览器访问：

```text
http://127.0.0.1:5180/
```

如果你本地 `5180` 已经被占用，可以换成本地 `15180`：

```powershell
ssh -L 15180:127.0.0.1:5180 -L 18000:127.0.0.1:8000 root@36.213.141.60
```

然后访问：

```text
http://127.0.0.1:15180/
```

注意：这种情况下页面仍然正常，因为页面的 `/api` 请求会先到本地 `15180`，再通过 SSH 隧道进入云主机的 Vite，最后由 Vite proxy 转给云主机的 FastAPI。

## 6. 验证后端

在云主机上执行：

```bash
cd /opt/campus-assistant/repo
source /opt/campus-assistant/venv/bin/activate
python cloud-deploy/scripts/smoke_test.py
```

或者在已经建立 SSH 隧道的本地电脑访问：

```text
http://127.0.0.1:8000/api/health
```

如果你用的是 `18000` 映射：

```text
http://127.0.0.1:18000/api/health
```

## 安全组要求

只需要开放：

```text
TCP 22
```

不需要开放：

```text
80
8080
443
8443
5180
8000
8766
```

你的安全组里，TCP `22` 当前只允许 `112.3.215.73/32`。如果你当前电脑公网 IP 不是这个，VSCode SSH、`ssh`、`scp` 都会连不上，需要把授权对象改成你当前公网 IP。

## 关于 ChromaDB

ChromaDB 不需要单独安装数据库服务。它是 Python 依赖包，数据会生成在：

```text
mcp-rag/knowledge
```

这个目录不需要提前上传。云主机第一次检索时，会根据：

```text
mcp-rag/kb
```

自动重建向量库。

## 关于在线模型

当前方案使用本地 embedding/rerank 模型，适合比赛演示和离线稳定运行。

后续如果接在线模型，建议只把“最终回答生成”接在线 LLM。embedding/rerank 仍保留本地模型，因为 ChromaDB 的向量索引和 embedding 模型绑定，随意更换 embedding 模型需要重建索引。
