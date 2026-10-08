# -*- coding: utf-8 -*-
"""MCP stdio server - 智能代码辅助生成的知识检索服务（第二版）。

通过标准输入/输出与湛卢通信（JSON-RPC 2.0，每行一条 JSON 消息）。

工具：
    search_code_kb(query, top_k, top_n)   代码/算法知识库：召回 top_k -> 重排取 top_n
    search_course_kb(query, top_k, top_n) 课程知识库：召回 top_k -> 重排取 top_n
    add_to_kb(corpus, filename, content)  用户扩充知识库

命令行调试：
    python server.py --list
    python server.py --search code "二叉树的层序遍历"
"""

import json
import sys

# 强制 stdin/stdout/stderr 使用 UTF-8，避免在 Windows 管道下按 GBK 输出中文导致解码失败
for _stream in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

import rag

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "rag-kb"
SERVER_VERSION = "2.0.0"

_DESC = (
    "在{scope}知识库中做两阶段检索（向量召回 top-k -> cross-encoder 重排取 top-n），"
    "返回与查询最相关的内容片段。用于生成代码/答疑前检索参考资料。"
)


def _make_tool(name):
    scope = "代码/算法" if name == "search_code_kb" else "校园课程"
    return {
        "name": name,
        "description": _DESC.format(scope=scope),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索关键词或问题描述"},
                "top_k": {"type": "integer", "description": "召回初筛条数，默认 10", "minimum": 1, "maximum": 50},
                "top_n": {"type": "integer", "description": "重排精筛后返回条数，默认 5，不超过 top_k", "minimum": 1, "maximum": 50},
            },
            "required": ["query"],
        },
    }


TOOLS = [
    _make_tool("search_code_kb"),
    _make_tool("search_course_kb"),
    {
        "name": "add_to_kb",
        "description": "由用户/代理向指定知识库写入一段内容（自动分片并重建索引），用于扩充知识库。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "corpus": {"type": "string", "enum": ["code", "course"], "description": "目标知识库：code 或 course"},
                "filename": {"type": "string", "description": "新文档文件名，如 quick_sort.md"},
                "content": {"type": "string", "description": "要写入的文档内容"},
            },
            "required": ["corpus", "filename", "content"],
        },
    },
]


def _corpus_for(tool_name):
    return "code" if tool_name == "search_code_kb" else "course"


def _format_results(results):
    if not results:
        return "未检索到相关内容。"
    lines = ["检索到 %d 条相关内容（已按语义相似度精筛排序）：" % len(results)]
    for i, item in enumerate(results, 1):
        lines.append("")
        lines.append("[%d] 来源: %s (chunk %s, 重排分 %.4f)" % (
            i, item["source"], item["chunk_index"], item["score"]))
        lines.append(item["text"])
    return "\n".join(lines)


def _invoke_tool(name, arguments):
    arguments = arguments or {}
    if name in ("search_code_kb", "search_course_kb"):
        query = str(arguments.get("query", "")).strip()
        if not query:
            raise ValueError("query 不能为空")
        corpus = _corpus_for(name)
        return _format_results(rag.search(
            corpus,
            query,
            top_k=arguments.get("top_k", 10),
            top_n=arguments.get("top_n", 5),
        ))
    if name == "add_to_kb":
        corpus = str(arguments.get("corpus", "")).strip()
        filename = str(arguments.get("filename", "")).strip()
        content = str(arguments.get("content", "")).strip()
        if corpus not in ("code", "course"):
            raise ValueError("corpus 只能是 code 或 course")
        if not filename or not content:
            raise ValueError("filename 和 content 不能为空")
        info = rag.add_to_kb(corpus, filename, content)
        return "已写入知识库 %s：%s（共 %d 个分片入库）。" % (corpus, info["path"], info["chunks"])
    raise ValueError("未知工具: %s" % name)


def handle_message(msg):
    method = msg.get("method")
    msg_id = msg.get("id")
    if msg_id is None:
        return None
    try:
        if method == "initialize":
            return {"result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }}
        if method == "ping":
            return {"result": {}}
        if method == "tools/list":
            return {"result": {"tools": TOOLS}}
        if method == "tools/call":
            params = msg.get("params") or {}
            text = _invoke_tool(params.get("name"), params.get("arguments"))
            return {"result": {"content": [{"type": "text", "text": text}]}}
        return {"error": {"code": -32601, "message": "Method not found: %s" % method}}
    except Exception as exc:
        return {"error": {"code": -32603, "message": "%s: %s" % (type(exc).__name__, exc)}}


def serve():
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_message(msg)
        if resp is not None:
            resp["jsonrpc"] = "2.0"
            if "id" in msg:
                resp["id"] = msg["id"]
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def main():
    args = sys.argv[1:]
    if args and args[0] == "--list":
        print(json.dumps({"tools": TOOLS}, ensure_ascii=False, indent=2))
        return
    if args and args[0] == "--corpora":
        print(rag.list_corpora())
        return
    if args and args[0] == "--search":
        corpus = args[1] if len(args) > 1 else "code"
        query = " ".join(args[2:]) if len(args) > 2 else ""
        print(_format_results(rag.search(corpus, query)))
        return
    serve()


if __name__ == "__main__":
    main()
