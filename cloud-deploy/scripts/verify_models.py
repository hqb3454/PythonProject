# -*- coding: utf-8 -*-
"""Verify that required local RAG models exist on the deployment host."""

from __future__ import annotations

import os
from pathlib import Path


MODEL_ROOT = Path(os.environ.get("RAG_MODEL_DIR", "/opt/campus-assistant/models"))
REQUIRED = [
    "text2vec-base-chinese",
    "mmarco-mMiniLMv2-L12-H384-v1",
]


def main() -> None:
    missing = []
    for name in REQUIRED:
        path = MODEL_ROOT / name
        if not path.exists():
            missing.append(str(path))
            print(f"missing: {path}")
        else:
            files = [p.name for p in path.iterdir()]
            print(f"ok: {path} ({len(files)} entries)")

    if missing:
        raise SystemExit("Model directory check failed.")

    print("All required model directories exist.")


if __name__ == "__main__":
    main()
