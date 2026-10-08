# -*- coding: utf-8 -*-
"""HTTP MCP client wrapper for the campus coding assistant backend."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


MCP_URL = os.environ.get("RAG_MCP_URL", "http://127.0.0.1:8766/mcp")

_REFERENCE_RE = re.compile(
    r"^\[(?P<rank>\d+)\]\s+来源:\s+(?P<source>.+?)\s+"
    r"\(chunk\s+(?P<chunk>-?\d+),\s+(?:分|重排分)\s+(?P<score>-?\d+(?:\.\d+)?)\)"
)


def parse_references(raw_text: str) -> List[Dict[str, Any]]:
    """Parse the human-readable MCP RAG output into UI-friendly references."""
    references: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None
    text_lines: List[str] = []

    for line in raw_text.splitlines():
        match = _REFERENCE_RE.match(line.strip())
        if match:
            if current is not None:
                current["text"] = "\n".join(text_lines).strip()
                references.append(current)
            current = {
                "rank": int(match.group("rank")),
                "source": match.group("source"),
                "chunk_index": int(match.group("chunk")),
                "score": float(match.group("score")),
                "text": "",
            }
            text_lines = []
            continue
        if current is not None:
            text_lines.append(line)

    if current is not None:
        current["text"] = "\n".join(text_lines).strip()
        references.append(current)

    return references


async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call a tool exposed by the RAG MCP server."""
    async with streamablehttp_client(MCP_URL) as (read, write, _get_sid):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            text = "\n".join(
                getattr(content, "text", "")
                for content in result.content
                if getattr(content, "type", "text") == "text"
            ).strip()
            return {
                "ok": True,
                "tool": name,
                "raw_text": text,
                "references": parse_references(text),
            }


async def list_tools() -> Dict[str, Any]:
    """Return the tools currently published by the HTTP MCP server."""
    async with streamablehttp_client(MCP_URL) as (read, write, _get_sid):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.list_tools()
            tools = getattr(response, "tools", response[0] if isinstance(response, tuple) else response)
            return {
                "ok": True,
                "url": MCP_URL,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description or "",
                    }
                    for tool in tools
                ],
            }
