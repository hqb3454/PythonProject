# 大模型接入说明

后端现在采用 `RAG 检索 + 大模型生成` 的结构：

```text
Vue
  -> FastAPI
  -> HTTP MCP RAG 检索
  -> 大模型读取用户问题 + RAG 上下文
  -> 返回教学回答、代码、测试建议、诊断建议
```

如果没有配置大模型 key，系统仍会使用本地模板降级回答，但效果会明显弱于大模型。

## 不要把 key 写进代码

API key 只放环境变量或 `.env`，不要提交到 Git。

如果 key 已经发到聊天、截图、仓库或公开环境，建议立即去平台后台撤销并重新生成。

## OpenAI 配置

本地开发可以在 `ai-coding-app/backend/.env` 写：

```bash
OPENAI_API_KEY=你的新key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_TEMPERATURE=0.2
```

云主机可以写到 `/etc/campus-assistant.env`：

```bash
OPENAI_API_KEY=你的新key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_TEMPERATURE=0.2
```

## Kimi / Moonshot 配置

Kimi 提供 OpenAI-compatible API 时，使用同一套后端代码：

```bash
KIMI_API_KEY=你的kimi或moonshot key
KIMI_MODEL=moonshot-v1-8k
KIMI_BASE_URL=https://api.moonshot.ai/v1
LLM_TEMPERATURE=0.2
```

如果同时配置了 `KIMI_API_KEY` 和 `OPENAI_API_KEY`，当前代码优先使用 Kimi。

## 安装依赖

```bash
cd /opt/campus-assistant/repo
source /opt/campus-assistant/venv/bin/activate
python -m pip install -r cloud-deploy/requirements-server.txt
```

然后重启 FastAPI 后端。
