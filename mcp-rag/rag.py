# -*- coding: utf-8 -*-
"""RAG 检索核心（第二版）。

- 知识库升级为 chromadb 持久化向量库（knowledge/ 目录）；
- 每次把一个文档「分片」成多个 chunk，每个 chunk 生成向量入库，chunk 归属记录在 metadata；
- 两阶段检索：
    1) 召回：query 转向量，与 chromadb 中向量做余弦相似度，取 top_k（初筛）；
    2) 重排：用 cross-encoder 对 (query, chunk) 逐个打分，取其中 top_n（精筛）。
       重排只取决于模型打分，完全忽略召回阶段的顺序；
- 用户可在对话中通过 add_to_kb 扩充知识库；
- 每次检索前检测 kb 目录签名（文件清单+修改时间），有变化自动重建索引。

对外暴露：
    list_corpora()
    ensure_index(corpus)
    search(corpus, query, top_k, top_n) -> list[dict]
    add_to_kb(corpus, filename, content) -> dict
"""

import json
import os
import re

import chromadb

import chunks
from embedder import embed_texts, embed_query, rerank

BASE = os.path.dirname(os.path.abspath(__file__))
KB_ROOT = os.path.join(BASE, "kb")
DB_DIR = os.path.join(BASE, "knowledge")
MANIFEST_FILE = os.path.join(BASE, "knowledge", "manifest.json")

_TEXT_EXTS = (".md", ".txt", ".py", ".c", ".cpp", ".java", ".js", ".ts", ".go", ".json")

_client = None
_collections = {}
_manifest = {}


def _get_client():
    global _client
    if _client is None:
        os.makedirs(DB_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=DB_DIR)
    return _client


def _load_manifest():
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as fh:
                _manifest.update(json.load(fh))
        except Exception:
            pass
    else:
        os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)


def _save_manifest():
    with open(MANIFEST_FILE, "w", encoding="utf-8") as fh:
        json.dump(_manifest, fh, ensure_ascii=False)


def list_corpora():
    if not os.path.isdir(KB_ROOT):
        return []
    return sorted(
        d for d in os.listdir(KB_ROOT)
        if os.path.isdir(os.path.join(KB_ROOT, d)) and not d.startswith(".")
    )


def _dir_signature(corpus):
    folder = os.path.join(KB_ROOT, corpus)
    parts = []
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and os.path.splitext(name)[1].lower() in _TEXT_EXTS:
                try:
                    mtime = int(os.path.getmtime(path))
                except OSError:
                    mtime = 0
                parts.append("%s@%s" % (name, mtime))
    return "|".join(parts)


def _load_entries(corpus):
    """读取知识库目录下所有文本文件并分片，返回条目列表。"""
    folder = os.path.join(KB_ROOT, corpus)
    entries = []
    if not os.path.isdir(folder):
        return entries
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        if os.path.splitext(name)[1].lower() not in _TEXT_EXTS:
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read().strip()
        if text:
            entries.extend(chunks.chunk_document(name, text))
    return entries


def rebuild(corpus):
    """(强制) 重建指定知识库的向量索引，并更新签名。"""
    client = _get_client()
    try:
        client.delete_collection(corpus)
    except Exception:
        pass
    col = client.get_or_create_collection(
        name=corpus, metadata={"hnsw:space": "cosine"}
    )
    entries = _load_entries(corpus)
    if entries:
        ids = ["%s#%d" % (e["source"], e["chunk_index"]) for e in entries]
        docs = [e["text"] for e in entries]
        metas = [{"source": e["source"], "chunk_index": e["chunk_index"]} for e in entries]
        embeddings = embed_texts(docs)
        col.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
    _collections[corpus] = col
    _manifest[corpus] = _dir_signature(corpus)
    _save_manifest()
    return {"corpus": corpus, "chunks": len(entries)}


def ensure_index(corpus):
    """确保索引为最新：仅在 kb 目录签名变化时重建，返回 collection 对象。"""
    sig = _dir_signature(corpus)
    if corpus in _collections and _manifest.get(corpus) == sig:
        return _collections[corpus]
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
    rebuild(corpus)
    return _collections[corpus]


def search(corpus, query, top_k=10, top_n=5):
    """两阶段检索：chromadb 召回 top_k，cross-encoder 重排取 top_n。"""
    top_k = max(1, min(int(top_k or 10), 50))
    top_n = max(1, min(int(top_n or 5), top_k))
    col = ensure_index(corpus)
    count = col.count()
    if count == 0:
        return []
    k = min(top_k, count)
    q = embed_query(query)
    res = col.query(
        query_embeddings=[q],
        n_results=k,
        include=["documents", "metadatas"],
    )
    recall_docs = res["documents"][0]
    recall_metas = res["metadatas"][0]

    # 重排：完全按 cross-encoder 打分，忽略召回顺序
    ranked = rerank(query, recall_docs, top_n)
    results = []
    for score, idx, _passage in ranked:
        meta = recall_metas[idx]
        results.append({
            "score": score,
            "source": meta.get("source", ""),
            "chunk_index": meta.get("chunk_index", -1),
            "text": recall_docs[idx],
        })
    return results


def add_to_kb(corpus, filename, content):
    """把内容写入知识库并立即重建该库，返回写入路径。"""
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", filename).strip() or "note.md"
    folder = os.path.join(KB_ROOT, corpus)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, safe_name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    rebuilt = rebuild(corpus)
    return {"path": path, **rebuilt}


_load_manifest()
