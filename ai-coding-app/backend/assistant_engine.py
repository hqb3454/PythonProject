# -*- coding: utf-8 -*-
"""Answer composition for the campus coding assistant.

支持两种大模型接入方式（自动选择可用者）：
1. Gemini（google-genai）：云主机默认，配置 GEMINI_API_KEY / GOOGLE_API_KEY 即可。
2. OpenAI / Kimi 等 OpenAI 兼容接口：配置 OPENAI_API_KEY 或 KIMI_API_KEY。

调用模型所需的 api key 写入环境变量（或 .env），不要写进 py 文件。
未配置任何 key 或调用失败时，回退到确定性的本地模板，保证 demo 始终可用。
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _context_excerpt(raw_context: str, limit: int = 1200) -> str:
    text = raw_context.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n..."


def _code_template(query: str, language: str) -> str:
    q = query.lower()
    if language.lower() != "python":
        return "// 当前演示版优先生成 Python 代码；可在后续扩展更多语言。"
    if "层序" in query or "bfs" in q:
        return """from collections import deque


def level_order(root):
    if root is None:
        return []
    queue = deque([root])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return result
"""
    if "二分" in query or "binary" in q:
        return """def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
    if "快速" in query or "快排" in query or "quick" in q:
        return """def quick_sort(nums):
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    left = [x for x in nums if x < pivot]
    mid = [x for x in nums if x == pivot]
    right = [x for x in nums if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)
"""
    return """def solve():
    \"\"\"根据题目要求补充输入解析、核心算法和输出逻辑。\"\"\"
    pass
"""


def _test_cases(query: str) -> List[str]:
    if "二分" in query or "binary" in query.lower():
        return [
            "binary_search([1, 3, 5, 7], 5) == 2",
            "binary_search([1, 3, 5, 7], 2) == -1",
            "binary_search([], 1) == -1",
        ]
    if "快速" in query or "快排" in query or "quick" in query.lower():
        return [
            "quick_sort([3, 1, 2]) == [1, 2, 3]",
            "quick_sort([2, 2, 1]) == [1, 2, 2]",
            "quick_sort([]) == []",
        ]
    if "层序" in query or "bfs" in query.lower():
        return [
            "空树应返回 []",
            "只有根节点的树应返回 [root.val]",
            "多层二叉树应按从上到下、从左到右输出",
        ]
    return [
        "覆盖空输入或边界输入",
        "覆盖一个最小有效样例",
        "覆盖一个包含重复值或异常路径的样例",
    ]


def _debug_suggestions(code: str, query: str) -> List[str]:
    suggestions = []
    text = f"{query}\n{code}"
    if "二分" in text and "left < right" in text:
        suggestions.append("二分查找若需要返回目标下标，通常循环条件应为 left <= right，否则单元素区间可能漏判。")
    if "quick_sort" in code and "len(" not in code:
        suggestions.append("递归排序需要明确终止条件，例如 len(nums) <= 1 时直接返回。")
    if "append(node.left)" in code and "if node.left" not in code:
        suggestions.append("树遍历入队前建议判断子节点是否为空，避免后续访问 None.val。")
    if not suggestions:
        suggestions.append("优先检查边界条件、循环终止条件、空输入处理和返回值格式是否与题目要求一致。")
    return suggestions


def _fallback_response(
    mode: str,
    query: str,
    code: str,
    language: str,
    raw_context: str,
) -> Dict[str, Any]:
    excerpt = _context_excerpt(raw_context)
    generated_code = _code_template(query, language) if mode in {"generate", "debug", "testcase"} else ""
    diagnostics = _debug_suggestions(code, query) if mode == "debug" else []
    tests = _test_cases(query) if mode in {"generate", "debug", "testcase"} else []

    if mode == "chat":
        answer = (
            "根据课程知识库，建议从概念、适用场景、复杂度和典型代码四个角度理解这个问题。\n\n"
            f"检索依据：\n{excerpt}"
        )
    elif mode == "explain":
        answer = (
            "这段代码可以按输入、核心状态、循环/递归推进、返回值四层来解释。"
            "结合知识库片段，重点关注算法不变量和复杂度。"
        )
    elif mode == "debug":
        answer = "我根据代码片段和知识库内容整理了可能的错误点，并给出一个可运行的修复参考。"
    elif mode == "testcase":
        answer = "下面给出覆盖边界、常规路径和异常/重复数据路径的测试建议。"
    else:
        answer = "下面是结合知识库内容生成的代码参考，建议在湛卢 IDE 中继续调试和补充单元测试。"

    return {
        "answer": answer,
        "generated_code": generated_code,
        "test_cases": tests,
        "diagnostics": diagnostics,
        "provider": "deterministic-fallback",
    }


def _llm_config(which: str = "default") -> Optional[Dict[str, str]]:
    """返回大模型配置。which="fast" 时使用轻量模型（响应快），否则用默认模型。"""
    kimi_key = os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if kimi_key:
        if which == "fast":
            # 快速档优先用轻量模型；未配置或无权限时回退到主模型
            # （主模型若为 kimi-k2 等推理模型，会走“免思考”快速模式，见 _maybe_call_llm）
            model = (
                os.environ.get("KIMI_FAST_MODEL")
                or os.environ.get("LLM_FAST_MODEL")
                or os.environ.get("KIMI_MODEL")
                or os.environ.get("LLM_MODEL")
                or "moonshot-v1-8k"
            )
        else:
            model = os.environ.get("KIMI_MODEL") or os.environ.get("LLM_MODEL") or "moonshot-v1-8k"
        return {
            "provider": "kimi-openai-compatible",
            "api_key": kimi_key,
            "base_url": os.environ.get("KIMI_BASE_URL")
            or os.environ.get("MOONSHOT_BASE_URL")
            or "https://api.moonshot.ai/v1",
            "model": model,
        }

    if openai_key:
        return {
            "provider": "openai",
            "api_key": openai_key,
            "base_url": os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1",
            "model": os.environ.get("OPENAI_MODEL") or os.environ.get("LLM_MODEL") or "gpt-4o-mini",
        }

    return None


def _system_prompt() -> str:
    return """你是校园代码智能助手，服务对象是正在学习数据结构、算法和编程课程的学生。

必须遵守：
1. 优先结合 RAG 知识库上下文回答；如果上下文不足，要明确说明，并给出通用推理。
2. 不要编造知识库来源，不要声称引用了不存在的文档。
3. 回答要适合教学：先讲思路，再给代码或排错建议。
4. 对代码生成、Bug 修复、测试生成任务，尽量给出可直接运行的 Python 示例。
"""


def _maybe_call_llm(prompt: str, model_kind: str = "default") -> Optional[Tuple[str, str]]:
    """尝试调用大模型，返回 (文本, provider 名称)；都不可用时返回 None。

    model_kind: "fast" 用轻量模型（响应快）；其他用默认模型（可能为推理模型，更慢更强）。
    优先级：Gemini (google-genai) -> OpenAI / Kimi (OpenAI 兼容)。
    openai 包在云主机上可能未安装，采用懒加载，缺失时安全跳过。
    """
    # 1) Gemini (google-genai)，云主机默认可用
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        try:
            from google import genai

            model = os.environ.get("CAMPUS_ASSISTANT_MODEL", "gemini-2.5-flash")
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(model=model, contents=prompt)
            text = getattr(response, "text", None)
            if text:
                return text.strip(), "google-genai"
        except Exception:
            pass  # 失败则继续尝试 OpenAI

    # 2) OpenAI / Kimi (OpenAI 兼容)
    config = _llm_config(model_kind)
    if config:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
            # 推理模型（如 kimi-k2 / deepseek-reasoner / o1 等）的温度有硬约束：
            #   - 正常思考：只允许 temperature=1，答案有时写在 reasoning_content；
            #   - 免思考快速档（standard 用）：kimi-k2 支持 thinking=disabled，此时必须 temperature=0.6，
            #     响应从 ~30s+ 降到秒级。
            model_l = config["model"].lower()
            is_reasoning = any(k in model_l for k in ("k2", "reason", "thinking", "r1", "deepseek-reasoner"))
            extra_kwargs: Dict[str, Any] = {}
            if model_kind == "fast" and is_reasoning:
                extra_kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
                temperature = 0.6
            elif is_reasoning:
                temperature = 1.0
            else:
                temperature = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
            resp = client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": _system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                **extra_kwargs,
            )
            msg = resp.choices[0].message
            text = getattr(msg, "content", None) or ""
            if not text:  # 推理模型偶尔把答案放在 reasoning_content
                text = getattr(msg, "reasoning_content", None) or ""
            if text:
                return text.strip(), f'{config["provider"]}:{config["model"]}'
        except Exception:
            pass

    return None


_HIT_RE = re.compile(r"^\[\d+\] 来源: (?P<source>.+?) \(chunk", re.M)


def _kb_direct_answer(raw_context: str, max_hits: int = 2, per_hit: int = 500) -> str:
    """chat 快速模式：不调用大模型，直接呈现知识库最相关的命中内容。

    raw_context 是 MCP 检索工具的人类可读输出，格式为：
        检索到 N 条相关内容（按语义相似度精筛排序）：
        [1] 来源: xxx.md (chunk 0, 分 -1.23)
        <内容>
        [2] ...
    """
    if not raw_context.strip():
        return (
            "（快速回答）知识库未检索到与问题直接相关的内容。\n\n"
            "建议切换到 **标准** 或 **详细** 模式，由大模型结合通用知识回答。"
        )

    matches = list(_HIT_RE.finditer(raw_context))
    if not matches:
        excerpt = _context_excerpt(raw_context, 600)
        return f"（快速回答 · 直接来自知识库检索，未调用大模型）\n\n{excerpt}"

    blocks = []
    for idx, m in enumerate(matches[:max_hits]):
        line_end = raw_context.find("\n", m.start())
        start = line_end + 1 if line_end != -1 else m.end()
        end_candidates = []
        if idx + 1 < len(matches):
            end_candidates.append(matches[idx + 1].start())
        tail = raw_context.find("\n检索到", start)  # 第二个知识库的段头
        if tail != -1:
            end_candidates.append(tail)
        end = min(end_candidates) if end_candidates else len(raw_context)
        content = raw_context[start:end].strip()
        if len(content) > per_hit:
            content = content[:per_hit].rstrip() + "\n..."
        blocks.append(f"**命中 {idx + 1}：{m.group('source')}**\n{content}")

    header = "（快速回答 · 直接来自课程知识库检索，未调用大模型——这正是本助手结合校内资料的优势）"
    return header + "\n\n" + "\n\n".join(blocks)


def compose_response(
    mode: str,
    query: str,
    code: str,
    language: str,
    raw_context: str,
    intensity: str = "standard",
) -> Dict[str, Any]:
    # chat 快速模式：不调大模型，直接基于知识库命中回答（响应接近即时）
    if mode == "chat" and intensity == "fast":
        fallback = _fallback_response(mode, query, code, language, raw_context)
        fallback["answer"] = _kb_direct_answer(raw_context)
        fallback["provider"] = "kb-direct(快速·未调大模型)"
        return fallback

    if mode == "chat" and intensity == "detailed":
        # 详细模式：默认模型（可为推理模型），要求讲解充分、含易错点，耗时较长
        prompt = f"""你是校园代码智能助手。请用中文**详细**回答，结合知识库上下文，避免编造来源。

要求：
1. 先讲清概念与原理，再分步骤展开；
2. 给出复杂度分析（如适用）；
3. **必须包含“易错点”小节**：列出初学者常犯错误、边界条件、与相似概念的混淆点；
4. 如有相似概念或替代方法，做简要对比；
5. 结构清晰，可用小标题与列表组织。

用户问题：{query}
代码片段：
{code or "无"}

知识库上下文：
{raw_context or "无命中"}
"""
        llm = _maybe_call_llm(prompt, model_kind="default")
    elif mode == "chat":
        # 标准模式：轻量模型 + 精简回答，优先保证响应速度
        prompt = f"""你是校园代码智能助手。请用中文回答，结合知识库上下文，避免编造来源。

要求：**精简**，控制在 250 字以内；先直接给结论，再用 1-2 句补充要点。
如需代码，只给最核心几行。

用户问题：{query}

知识库上下文：
{raw_context or "无命中"}
"""
        llm = _maybe_call_llm(prompt, model_kind="fast")
    else:
        prompt = f"""你是校园代码智能助手。请用中文回答，结合知识库上下文，避免编造来源。

任务类型：{mode}
用户问题：{query}
代码片段：
{code or "无"}

知识库上下文：
{raw_context or "无命中"}
"""
        llm = _maybe_call_llm(prompt)

    fallback = _fallback_response(mode, query, code, language, raw_context)
    if llm:
        fallback["answer"] = llm[0]
        fallback["provider"] = llm[1]
    return fallback
