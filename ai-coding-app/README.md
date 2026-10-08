# 校园代码智能助手

面向校园数据结构、算法与编程课程的 AI Coding 应用。系统使用 Vue 工作台、FastAPI 后端和现有 `mcp-rag` MCP Server，把课程/算法 Markdown 知识库接入代码生成、课程答疑、代码解释、Bug 修复、测试用例生成和知识库扩充流程。

## 架构

```text
Vue 工作台
  -> FastAPI backend
    -> HTTP MCP client
      -> mcp-rag/http_server.py
        -> ChromaDB 向量库
        -> text2vec-base-chinese embedding
        -> mmarco-mMiniLMv2-L12-H384-v1 rerank
```

现有 `mcp-rag/server.py` 仍保留 stdio MCP 能力，可供湛卢 IDE 直接调用；`mcp-rag/http_server.py` 面向独立 Web 应用提供 Streamable HTTP MCP 服务。

## 本地模型与知识库

- embedding：`F:\PythonProject\models\text2vec-base-chinese`
- rerank：`F:\PythonProject\models\mmarco-mMiniLMv2-L12-H384-v1`
- 知识库文档：`F:\PythonProject\mcp-rag\kb\code`、`F:\PythonProject\mcp-rag\kb\course`
- 向量库：`F:\PythonProject\mcp-rag\knowledge`

检索链路为“两阶段检索”：先用 embedding 在 ChromaDB 中召回 top-k，再用 cross-encoder 对候选片段重排 top-n。

## 启动

在三个终端中分别运行：

```powershell
cd F:\PythonProject\mcp-rag
F:\PythonProject\rag\.venv\Scripts\python.exe http_server.py 8766
```

```powershell
cd F:\PythonProject\ai-coding-app\backend
$env:RAG_MCP_URL = "http://127.0.0.1:8766/mcp"
F:\PythonProject\rag\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

```powershell
cd F:\PythonProject\ai-coding-app\frontend
npm install
npm run dev
```

访问 `http://127.0.0.1:5173`。HTTP MCP 默认使用 8766，避免和湛卢 IDE 或其他调试中的 MCP 服务抢占 8765。

如果配置了 `GEMINI_API_KEY` 或 `GOOGLE_API_KEY`，后端会尝试调用 `google-genai`；否则使用本地可演示的降级生成逻辑，仍会展示 RAG 引用、代码模板、测试用例和修复建议。

## API

- `GET /api/health`：检查后端和 HTTP MCP 连接。
- `POST /api/chat`：课程答疑，同时检索 course 和 code 知识库。
- `POST /api/code/generate`：算法/代码生成。
- `POST /api/code/explain`：代码解释。
- `POST /api/code/debug`：Bug 修复建议。
- `POST /api/testcase/generate`：测试用例生成。
- `POST /api/kb/add`：通过 MCP `add_to_kb` 扩充知识库。

## 演示脚本

1. 课程答疑：输入“什么是二叉搜索树”，查看回答和知识库命中。
2. 代码生成：输入“用 Python 实现二分查找，并说明复杂度”，查看生成代码和测试建议。
3. Bug 修复：切换到 Bug 修复，使用默认二分查找样例，查看循环条件建议。
4. 知识扩充：新增一段 Markdown 知识，再回到答疑或代码生成检索新增内容。

## 湛卢 IDE 使用说明

本作品把湛卢 IDE 的 AI Coding 能力融入开发流程：

- 用 agent 模式创建并调试 MCP Server。
- 使用 MCP 工具把本地 RAG 知识库接入 IDE。
- 通过代码生成完成前后端脚手架和接口封装。
- 通过智能调试修复 HTTP MCP client/server 兼容问题。
- 通过测试生成覆盖 stdio MCP、HTTP MCP、后端 API 和前端演示路径。
- 将“校园代码助手”开发方式沉淀为 MCP + Skill + RAG 的可复用范式。
