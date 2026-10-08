# -*- coding: utf-8 -*-
"""验证：以 MCP client 方式接入 RAG HTTP MCP server，列出工具并调用检索。"""
import asyncio
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://127.0.0.1:8765/mcp"


async def main():
    async with streamablehttp_client(URL) as (read, write, _get_sid):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("MCP tools:", [t.name for t in tools])

            res = await session.call_tool("search_code_kb", {"query": "二叉树的层序遍历", "top_n": 2})
            print("\n--- search_code_kb 调用结果 ---")
            for c in res.content:
                print(c.text[:500])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main())
