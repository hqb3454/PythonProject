# -*- coding: utf-8 -*-
"""Smoke test for cloud deployment."""

from __future__ import annotations

import json
import urllib.request


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    health = get_json("http://127.0.0.1:8000/api/health")
    print("Backend health:")
    print(json.dumps(health, ensure_ascii=False, indent=2)[:1200])
    if not health.get("ok"):
        raise SystemExit("Backend health failed")


if __name__ == "__main__":
    main()
