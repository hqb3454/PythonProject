# -*- coding: utf-8 -*-
"""RAG 检索服务的 HTTP MCP server（Streamable HTTP transport）。

供「独立 Web 应用」作为 MCP client 调用，从而体现 MCP 高阶能力应用。
默认监听 http://127.0.0.1:8765/mcp

用法：
    python http_server.py   # 默认端口 8765
    python http_server.py 9000
"""

import sys

from mcp.server.fastmcp import FastMCP

import rag

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_PORT = 8765

mcp = FastMCP("rag-kb")


def _fmt(results):
    if not results:
        return "未检索到相关内容。"
    lines = ["检索到 %d 条相关内容（按语义相似度精筛排序）：" % len(results)]
    for i, item in enumerate(results, 1):
        lines.append("[%d] 来源: %s (chunk %s, 分 %.4f)" % (
            i, item["source"], item["chunk_index"], item["score"]))
        lines.append(item["text"])
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def search_code_kb(query: str, top_k: int = 10, top_n: int = 5) -> str:
    """在代码/算法知识库中做两阶段检索（向量召回 top-k -> cross-encoder 重排取 top-n），返回相关内容片段。"""
    return _fmt(rag.search("code", query, top_k=top_k, top_n=top_n))


@mcp.tool()
def search_course_kb(query: str, top_k: int = 10, top_n: int = 5) -> str:
    """在校园课程知识库中做两阶段检索（向量召回 top-k -> cross-encoder 重排取 top-n），返回相关内容片段。"""
    return _fmt(rag.search("course", query, top_k=top_k, top_n=top_n))


@mcp.tool()
def add_to_kb(corpus: str, filename: str, content: str) -> str:
    """向指定知识库（code 或 course）写入一段内容，自动分片、重建向量索引。用于扩充知识库。"""
    corpus = corpus.strip()
    if corpus not in ("code", "course"):
        raise ValueError("corpus 只能是 code 或 course")
    info = rag.add_to_kb(corpus, filename, content)
    return "已写入知识库 %s：%s（共 %d 个分片入库）。" % (corpus, info["path"], info["chunks"])


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    mcp.run(transport="streamable-http", host="127.0.0.1", port=port)
