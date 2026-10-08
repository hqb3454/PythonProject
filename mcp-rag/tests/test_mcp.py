# -*- coding: utf-8 -*-
"""py3.12 集成自测：通过 MCP stdio 协议与 server.py 通信，覆盖 initialize / tools/list / tools/call
(search_code_kb / search_course_kb / add_to_kb)。"""
import json
import os
import subprocess
import sys

server = r"F:\PythonProject\mcp-rag\server.py"
proc = subprocess.Popen(
    [sys.executable, server],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    cwd=r"F:\PythonProject\mcp-rag",
)


def send(msg):
    proc.stdin.write((json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8"))
    proc.stdin.flush()
    return json.loads(proc.stdout.readline().decode("utf-8"))


def call_tool(name, args):
    r = send({"jsonrpc": "2.0", "id": "x", "method": "tools/call",
              "params": {"name": name, "arguments": args}})
    if "error" in r:
        return "ERROR: " + json.dumps(r["error"], ensure_ascii=False)
    return r["result"]["content"][0]["text"]


print("initialize:", send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})["result"]["serverInfo"])
tools = send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})["result"]["tools"]
print("tools:", [t["name"] for t in tools])

print("\n--- search_code_kb ---")
print(call_tool("search_code_kb", {"query": "二叉树的层序遍历", "top_n": 2})[:300])

print("\n--- search_course_kb ---")
print(call_tool("search_course_kb", {"query": "什么是二叉搜索树", "top_n": 2})[:300])

print("\n--- add_to_kb ---")
print(call_tool("add_to_kb", {
    "corpus": "code",
    "filename": "quick_sort.md",
    "content": "# 快速排序\n\n快速排序采用分治策略：选一个基准，把小于基准的放左边、大于基准的放右边，再递归排序两侧。\n\n```python\ndef quick_sort(nums):\n    if len(nums) <= 1:\n        return nums\n    pivot = nums[len(nums) // 2]\n    left = [x for x in nums if x < pivot]\n    mid = [x for x in nums if x == pivot]\n    right = [x for x in nums if x > pivot]\n    return quick_sort(left) + mid + quick_sort(right)\n```\n\n平均时间复杂度 O(n log n)。",
}))

print("\n--- search_code_kb (新增的快排) ---")
print(call_tool("search_code_kb", {"query": "快速排序的分治实现", "top_n": 2})[:300])

proc.terminate()
print("\nOK")
