# -*- coding: utf-8 -*-
"""本地模型加载层。

- embedding：sentence-transformers（text2vec-base-chinese，中文语义向量），用于「召回」阶段；
- 重排：cross-encoder（mmarco-mMiniLMv2-L12-H384-v1），用于「精筛」阶段对 (query, chunk) 打分。

两个模型均为本地文件（默认放在 F:\\PythonProject\\models），离线加载、无需联网调用。
可通过环境变量 RAG_MODEL_DIR 覆盖模型根目录。
"""

import os

from sentence_transformers import CrossEncoder, SentenceTransformer

_MODEL_ROOT = os.environ.get("RAG_MODEL_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models"
)

EMBED_MODEL_PATH = os.path.join(_MODEL_ROOT, "text2vec-base-chinese")
RERANK_MODEL_PATH = os.path.join(_MODEL_ROOT, "mmarco-mMiniLMv2-L12-H384-v1")

_embedder = None
_reranker = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_PATH, device="cpu")
    return _embedder


def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANK_MODEL_PATH, device="cpu", max_length=512)
    return _reranker


def embed_texts(texts):
    """批量对文本生成归一化向量，返回 list[list[float]]。"""
    if not texts:
        return []
    vectors = get_embedder().encode(list(texts), normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_query(text):
    """对单个查询生成归一化向量，返回 list[float]。"""
    return embed_texts([text])[0]


def rerank(query, passages, top_n):
    """用 cross-encoder 对 (query, passage) 重打分，返回按分数降序的前 top_n 条。

    注意：打分完全基于模型对语义相似度的判断，与召回阶段的初始顺序无关。
    返回 list[(score, passage_index_in_input, passage)]。
    """
    if not passages:
        return []
    pairs = [[query, p] for p in passages]
    scores = get_reranker().predict(pairs)
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [
        (float(scores[i]), i, passages[i])
        for i in ranked[:top_n]
    ]
