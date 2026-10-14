# -*- coding: utf-8 -*-
"""本地模型加载层。

本py文件完成的工作:导入本地embedding模型,对传入数据库的文本进行向量化以及对用户提出的问题进行向量化。导入重排模型,顺便完成重排功能.

- embedding：sentence-transformers（text2vec-base-chinese，中文语义向量），用于「召回」阶段；
- 重排：cross-encoder（mmarco-mMiniLMv2-L12-H384-v1），用于「精筛」阶段对 (query, chunk) 打分。

两个模型均为本地文件（默认放在 F:\\PythonProject\\models），离线加载、无需联网调用。


通过os.environ.get获取环境变量 RAG_MODEL_DIR,而不使用固定目录,这样在迁移到另一台主机或者云主机的时候，只需要把模型下载到另一台主机即可,并且添加环境变量
虽然和修改路径差不多，但是添加到环境变量之后，以后需要模型路径时直需要使用RAG_MODEL_DIR即可，很方便


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
