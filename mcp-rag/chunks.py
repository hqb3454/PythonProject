# -*- coding: utf-8 -*-
"""文档分片。

策略（自选）：
1) 先按「空行 + 标题」把文档切成语义段；
2) 相邻小段聚合到接近 CHUNK_SIZE，保持语义连贯；
3) 单个超长段再按字符窗口切分，并保留 CHUNK_OVERLAP 重叠，避免切断语义。
"""

import re

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

_HEADING_RE = re.compile(r"^#{1,6}\s+\S.*$", re.MULTILINE)


def split_paragraphs(text):
    """按空行切段落；再按 markdown 标题进一步切分，保证标题独立成段。"""
    # 先按标题切：在每个标题前插入分隔符，再按空行切
    text = _HEADING_RE.sub(lambda m: "\n\n" + m.group(0), text)
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return parts


def _hard_split(text, size, overlap):
    """对超长文本按字符窗口硬切，保留重叠。"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        out.append(text[i:i + size])
        i += size - overlap
        if i >= n:
            break
    return out


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """把一个文档切分成若干 chunk，返回 list[str]。"""
    paras = split_paragraphs(text)
    chunks = []
    buffer = ""
    for para in paras:
        # 单段超长：先刷空 buffer，再硬切该段
        if len(para) > size:
            if buffer:
                chunks.append(buffer)
                buffer = ""
            chunks.extend(_hard_split(para, size, overlap))
            continue
        if buffer and len(buffer) + len(para) + 1 > size:
            chunks.append(buffer)
            buffer = para
        else:
            buffer = (buffer + "\n" + para) if buffer else para
    if buffer:
        chunks.append(buffer)
    return [c for c in chunks if c.strip()]


def chunk_document(source, text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """返回该文档的分片条目列表，带 source 与 chunk_index 归属。"""
    return [
        {"source": source, "chunk_index": i, "text": c}
        for i, c in enumerate(chunk_text(text, size, overlap))
    ]
