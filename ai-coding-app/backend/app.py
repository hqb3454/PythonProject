# -*- coding: utf-8 -*-
"""FastAPI backend for the campus coding assistant demo."""

from __future__ import annotations

from typing import Any, Dict, List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import assistant_engine
import mcp_client


class AssistantRequest(BaseModel):
    question: str = Field("", description="User question or task")
    code: str = Field("", description="Optional code snippet")
    language: str = Field("python", description="Target programming language")
    top_k: int = Field(10, ge=1, le=50)
    top_n: int = Field(5, ge=1, le=50)


class AddKnowledgeRequest(BaseModel):
    corpus: Literal["code", "course"]
    filename: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


app = FastAPI(
    title="Campus Coding Assistant",
    description="Vue + FastAPI + MCP RAG demo for campus coding scenarios.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _query_text(payload: AssistantRequest) -> str:
    question = payload.question.strip()
    code = payload.code.strip()
    return "\n".join(part for part in [question, code] if part).strip()


async def _search(corpus: Literal["code", "course"], payload: AssistantRequest) -> Dict[str, Any]:
    query = _query_text(payload)
    if not query:
        raise HTTPException(status_code=400, detail="question 或 code 不能为空")
    tool = "search_code_kb" if corpus == "code" else "search_course_kb"
    try:
        return await mcp_client.call_tool(
            tool,
            {
                "query": query,
                "top_k": payload.top_k,
                "top_n": min(payload.top_n, payload.top_k),
            },
        )
    except Exception as exc:
        return {
            "ok": False,
            "tool": tool,
            "raw_text": "",
            "references": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


async def _handle(mode: Literal["chat", "generate", "explain", "debug", "testcase"], payload: AssistantRequest) -> Dict[str, Any]:
    if mode == "chat":
        course = await _search("course", payload)
        code = await _search("code", payload)
        raw_context = "\n\n".join(part for part in [course["raw_text"], code["raw_text"]] if part)
        references: List[Dict[str, Any]] = course["references"] + code["references"]
        mcp_status = {"course": course, "code": code}
    else:
        result = await _search("code", payload)
        raw_context = result["raw_text"]
        references = result["references"]
        mcp_status = {"code": result}

    composed = assistant_engine.compose_response(
        mode=mode,
        query=payload.question,
        code=payload.code,
        language=payload.language,
        raw_context=raw_context,
    )
    return {
        "mode": mode,
        "answer": composed["answer"],
        "generated_code": composed["generated_code"],
        "test_cases": composed["test_cases"],
        "diagnostics": composed["diagnostics"],
        "references": references,
        "raw_context": raw_context,
        "provider": composed["provider"],
        "mcp_status": mcp_status,
    }


@app.get("/api/health")
async def health() -> Dict[str, Any]:
    tools_info: Dict[str, Any] | None = None
    try:
        tools_info = await mcp_client.list_tools()
    except Exception as exc:
        tools_info = {"ok": False, "url": mcp_client.MCP_URL, "tools": [], "error": f"{type(exc).__name__}: {exc}"}

    try:
        probe = await mcp_client.call_tool("search_course_kb", {"query": "数据结构", "top_k": 1, "top_n": 1})
        return {"ok": True, "mcp": {**tools_info, "probe": probe["raw_text"][:160]}}
    except Exception as exc:
        return {"ok": False, "mcp": {**(tools_info or {}), "url": mcp_client.MCP_URL, "error": f"{type(exc).__name__}: {exc}"}}


@app.post("/api/chat")
async def chat(payload: AssistantRequest) -> Dict[str, Any]:
    return await _handle("chat", payload)


@app.post("/api/code/generate")
async def generate_code(payload: AssistantRequest) -> Dict[str, Any]:
    return await _handle("generate", payload)


@app.post("/api/code/explain")
async def explain_code(payload: AssistantRequest) -> Dict[str, Any]:
    return await _handle("explain", payload)


@app.post("/api/code/debug")
async def debug_code(payload: AssistantRequest) -> Dict[str, Any]:
    return await _handle("debug", payload)


@app.post("/api/testcase/generate")
async def generate_testcases(payload: AssistantRequest) -> Dict[str, Any]:
    return await _handle("testcase", payload)


@app.post("/api/kb/add")
async def add_knowledge(payload: AddKnowledgeRequest) -> Dict[str, Any]:
    try:
        result = await mcp_client.call_tool(
            "add_to_kb",
            {
                "corpus": payload.corpus,
                "filename": payload.filename,
                "content": payload.content,
            },
        )
        return {
            "ok": True,
            "message": result["raw_text"],
            "references": result["references"],
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"MCP add_to_kb 调用失败：{type(exc).__name__}: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
