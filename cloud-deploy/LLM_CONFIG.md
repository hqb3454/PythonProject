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
KIMI_MODEL=kimi-k2.6
KIMI_BASE_URL=https://api.moonshot.cn/v1
LLM_TEMPERATURE=0.2
```

如果同时配置了 `KIMI_API_KEY` 和 `OPENAI_API_KEY`，当前代码优先使用 Kimi。

> 注意：推理类模型（如 kimi-k2.x、deepseek-reasoner、o1）通常**只允许 temperature=1**。
> 代码会自动识别这类模型并强制 temperature=1，无需手动处理。

## 回答强度（chat 课程答疑）

chat 模式支持三档强度，由请求的 `intensity` 字段控制（fast / standard / detailed）：

| 档位 | 行为 | 模型 | 速度 |
|---|---|---|---|
| fast | 不调用大模型，直接呈现知识库命中内容 | 无 | 接近即时（~1s） |
| standard | 精简回答（≤250 字），**kimi-k2 免思考模式**（thinking=disabled + temperature=0.6） | `KIMI_MODEL` 免思考 | 快（~2–10s） |
| detailed | 详细讲解，含易错点小节 | `KIMI_MODEL`（kimi-k2.6，正常思考） | 慢（30–90s） |

可选环境变量：

```bash
# 仅当你的 key 能访问更轻的模型时才设置（如 moonshot-v1-8k）；
# 若 key 只有 kimi-k2 系列权限，请不要设置，standard 档会自动用 k2 免思考模式。
# KIMI_FAST_MODEL=moonshot-v1-8k
```

> 实测：kimi-k2.6 免思考模式回答一个概念问题约 1.6s；
> reasoning_effort=low 仍会思考较久（10–30s），不推荐作快速档。

其余模式（代码生成 / 解释 / 修复 / 测试）不受 intensity 影响，始终使用 `KIMI_MODEL`。

## 安装依赖

```bash
cd /opt/campus-assistant/repo
source /opt/campus-assistant/venv/bin/activate
python -m pip install -r cloud-deploy/requirements-server.txt
```

然后重启 FastAPI 后端。
