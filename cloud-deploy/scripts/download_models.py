# -*- coding: utf-8 -*-
"""Download local embedding/rerank models for cloud deployment.

If the cloud host cannot access Hugging Face reliably, upload the local
F:\\PythonProject\\models directory to /opt/campus-assistant/models instead.
"""

from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import snapshot_download


MODEL_ROOT = Path(os.environ.get("RAG_MODEL_DIR", "/opt/campus-assistant/models"))
MODEL_ROOT.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("shibing624/text2vec-base-chinese", "text2vec-base-chinese"),
    ("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1", "mmarco-mMiniLMv2-L12-H384-v1"),
]


def main() -> None:
    for repo_id, local_name in MODELS:
        target = MODEL_ROOT / local_name
        print(f"Downloading {repo_id} -> {target}")
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(target),
            local_dir_use_symlinks=False,
        )
    print("Done.")


if __name__ == "__main__":
    main()
