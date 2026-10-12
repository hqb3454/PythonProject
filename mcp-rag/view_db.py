# -*- coding: utf-8 -*-
"""查看向量数据库（chromadb）内容：列出 collections、每条向量的 id/metadata/维度/文本。"""
import sys

import chromadb

DB = r"F:\PythonProject\mcp-rag\knowledge"
INCLUDE = ["embeddings", "documents", "metadatas"]


def main():
    client = chromadb.PersistentClient(path=DB)
    cols = client.list_collections()
    print("== collections:", [c.name for c in cols])

    for c in cols:
        cnt = c.count()
        print("\n=== collection:", c.name, "| 向量总数:", cnt)
        if not cnt:
            continue
        g = c.get(limit=5, include=INCLUDE)
        ids, docs, metas = g["ids"], g.get("documents") or [], g.get("metadatas") or []
        embs = g.get("embeddings")
        if embs is None:
            embs = []
        for i in range(len(ids)):
            emb = embs[i] if i < len(embs) else None
            vec = []
            if emb is not None:
                vec = [round(float(x), 4) for x in emb[:5]]
            print("  - id   :", ids[i])
            print("    meta :", metas[i] if i < len(metas) else {})
            print("    维度 :", len(emb) if emb is not None else 0, "| 向量前5维:", vec)
            if docs and i < len(docs):
                preview = " ".join(str(docs[i]).split())[:90]
                print("    文本 :", preview)
        print("    ... (当前仅展示前 5 条，共 %d 条)" % cnt)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
