# KMP 字符串匹配

## 思路
- 朴素匹配 BF 在失配时把模式串整体后移一位（主串指针 i 回溯），最坏 O(n·m)。
- **KMP 的核心**：失配时**主串指针 i 绝不回溯**，只让模式串指针 j 按 `next` 数组回退。
  - 依据是：已匹配的部分本身就是模式串的前缀，模式串自身的结构足以决定"能安全右移多少"。
- **next[j] 的定义**：`next[j]` = 模式串 `P[0..j-1]` 这个子串的**最长相等真前缀与真后缀的长度**。
  - 含义：j 位置失配时，j 应回退到 `next[j]`（前 next[j] 个字符已经匹配好了，不用再比）。
- 求 next 用**双指针自匹配**（类似自己匹配自己）：i 扫前缀尾、j 扫后缀尾，相等则双双前进，不等则 j 回退到 `next[j]`。
- nextval 优化：若 `P[j] == P[next[j]]`，这次比较注定还失败，直接令 `nextval[j] = nextval[next[j]]`，跳过无效比较。

## 代码

```python
from typing import List


def build_next(pattern: str) -> List[int]:
    """求 next 数组（下标从 0 起）。next[i] = P[0..i-1] 的最长相等真前后缀长度"""
    m = len(pattern)
    nxt = [0] * m
    j = 0                       # 当前已匹配的前缀长度
    for i in range(1, m):       # i 从 1 开始扫
        while j > 0 and pattern[i] != pattern[j]:
            j = nxt[j - 1]      # 失配：回退
        if pattern[i] == pattern[j]:
            j += 1
        nxt[i] = j
    return nxt


def build_nextval(pattern: str) -> List[int]:
    """nextval：跳过注定失败的比较"""
    m = len(pattern)
    nxt = build_next(pattern)
    nv = [0] * m
    for i in range(1, m):
        if pattern[i] == pattern[nxt[i]]:
            nv[i] = nv[nxt[i]]
        else:
            nv[i] = nxt[i]
    return nv


def kmp_search(text: str, pattern: str) -> int:
    """返回 pattern 在 text 中首次出现的下标，未找到返回 -1"""
    if not pattern:
        return 0
    n, m = len(text), len(pattern)
    nxt = build_next(pattern)
    j = 0
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = nxt[j - 1]      # 失配：按 next 回退，i 不动
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            return i - m + 1    # 匹配成功
    return -1


def kmp_find_all(text: str, pattern: str) -> List[int]:
    """找出所有匹配位置（可重叠）"""
    if not pattern:
        return []
    n, m = len(text), len(pattern)
    nxt = build_next(pattern)
    res, j = [], 0
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = nxt[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            res.append(i - m + 1)
            j = nxt[j - 1]      # 继续找下一个（关键：不能置 0，否则漏重叠匹配）
    return res


def brute_force(text: str, pattern: str) -> int:
    """朴素 BF，用于对比"""
    n, m = len(text), len(pattern)
    for s in range(n - m + 1):
        if text[s:s + m] == pattern:
            return s
    return -1


if __name__ == "__main__":
    print(build_next("abaabcac"))       # [0,0,1,1,2,0,1,0]
    print(build_next("abcdabca"))       # [0,0,0,0,1,2,3,1]
    print(kmp_search("ababcabcacbab", "abcac"))    # 6
    print(kmp_find_all("aaaaa", "aa"))             # [0, 1, 2, 3]
    print(brute_force("hello world", "world"))     # 6
```

## 复杂度
| 算法 | 预处理 | 匹配 | 总计 |
|---|---|---|---|
| BF 朴素 | 无 | O(n·m) | O(n·m) |
| KMP | O(m) | O(n) | **O(n+m)** |

空间复杂度：O(m)，存 next 数组。
为什么匹配是 O(n)：主串指针 i 只增不减，最多扫描 n 次；j 的回退总量也不超过匹配长度。

## 易错点
- **下标基准**：教材常从 1 开始（`next[1] = 0`），代码从 0 开始（`nxt[0] = 0`），含义相同但取值差 1，回退写成 `j = nxt[j-1]` 而不是 `nxt[j]`。混用会差一位导致死循环。
- 求 next 时 `for i in range(1, m)`，不要从 0 开始；`j` 初值为 0。
- 匹配成功的条件是 `j == m`，返回位置是 `i - m + 1`，不是 `i - j`（此时 j 已等于 m，恰好等价，但注意此时 j 已被修改，若之后还要用需先回退）。
- 找所有匹配时，成功后必须 `j = nxt[j-1]` 再继续，直接 `j = 0` 会漏掉重叠的匹配（如 "aaaaa" 中找 "aa"）。
- KMP 只做**精确匹配**；模糊匹配、正则、带通配符的匹配要用动态规划或自动机。
- next 数组只依赖模式串，所以**同一模式串匹配多个文本时可复用**，这是 KMP 在工程上的实际价值。
- Python 中 `str.find()` 用的是高度优化的混编算法，实际工程里通常比手写 KMP 更快；KMP 的学习价值在于理解"利用已匹配信息避免回溯"的思想。
