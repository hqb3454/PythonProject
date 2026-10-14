# 回溯与 DFS 模板

## 思路
- **回溯 = 递归 + 状态回退**，本质是对"决策树"做深度优先遍历，属于暴力搜索但可通过剪枝大幅加速。
- 通用框架（三步）：
  1. **做选择**：把当前选项加入路径；
  2. **递归**：进入下一层决策；
  3. **撤销选择**：把选项从路径移除，回到进入前的状态（这步就是"回溯"）。
- 两个终止条件：找到解（记录答案，视需求决定是否继续）、路径走完/不合法（直接返回）。
- 两类剪枝：
  - **可行性剪枝**：当前路径已经不可能满足约束，立即返回（如总和已超目标）；
  - **去重剪枝**：同一层重复使用相同元素会产生重复解，用 `i > start and nums[i] == nums[i-1] then continue` 跳过。
- 常见题型：全排列、子集、组合总和、N 皇后、数独、括号生成、单词搜索、分割回文串。

## 代码

```python
from typing import List


def permutations(nums: List[int]) -> List[List[int]]:
    """全排列：每层从剩余元素中选一个，用 used 标记"""
    res, path = [], []
    used = [False] * len(nums)

    def dfs():
        if len(path) == len(nums):
            res.append(path[:])          # 注意要拷贝
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            dfs()
            path.pop()                   # 撤销选择
            used[i] = False              # 撤销标记
    dfs()
    return res


def subsets(nums: List[int]) -> List[List[int]]:
    """子集：每个元素选或不选，用 start 保证不重复"""
    res, path = [], []

    def dfs(start: int):
        res.append(path[:])              # 每个结点都是一个答案
        for i in range(start, len(nums)):
            path.append(nums[i])
            dfs(i + 1)                   # 下一层只能从 i+1 开始
            path.pop()
    dfs(0)
    return res


def combination_sum(candidates: List[int], target: int) -> List[List[int]]:
    """组合总和：元素可重复使用，和等于 target（先排序便于剪枝）"""
    candidates.sort()
    res, path = [], []

    def dfs(start: int, remain: int):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remain:
                break                    # 可行性剪枝：后面的更大，直接停
            path.append(candidates[i])
            dfs(i, remain - candidates[i])   # 传 i 而非 i+1：允许重复使用
            path.pop()
    dfs(0, target)
    return res


def subsets_with_dup(nums: List[int]) -> List[List[int]]:
    """含重复元素的子集：先排序，同层跳过相同元素"""
    nums.sort()
    res, path = [], []

    def dfs(start: int):
        res.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                 # 去重剪枝
            path.append(nums[i])
            dfs(i + 1)
            path.pop()
    dfs(0)
    return res


def solve_n_queens(n: int) -> List[List[str]]:
    """N 皇后：逐行放皇后，用三个集合记录冲突的列与对角线"""
    res = []
    queens = []                          # queens[row] = col
    cols, diag1, diag2 = set(), set(), set()

    def dfs(row: int):
        if row == n:
            board = []
            for c in queens:
                board.append("." * c + "Q" + "." * (n - c - 1))
            res.append(board)
            return
        for col in range(n):
            d1, d2 = row - col, row + col   # 主对角线/副对角线的特征值
            if col in cols or d1 in diag1 or d2 in diag2:
                continue
            cols.add(col); diag1.add(d1); diag2.add(d2)
            queens.append(col)
            dfs(row + 1)
            queens.pop()                  # 回溯：撤销三处状态
            cols.remove(col); diag1.remove(d1); diag2.remove(d2)
    dfs(0)
    return res


def generate_parenthesis(n: int) -> List[str]:
    """括号生成：左括号数不超过 n，右括号数不超过左括号数"""
    res, path = [], []

    def dfs(left: int, right: int):
        if len(path) == 2 * n:
            res.append("".join(path))
            return
        if left < n:
            path.append("(")
            dfs(left + 1, right)
            path.pop()
        if right < left:                 # 剪枝：右括号不能多于左括号
            path.append(")")
            dfs(left, right + 1)
            path.pop()
    dfs(0, 0)
    return res


if __name__ == "__main__":
    print(permutations([1, 2, 3]))
    print(subsets([1, 2, 3]))
    print(combination_sum([2, 3, 6, 7], 7))    # [[2,2,3],[7]]
    print(subsets_with_dup([1, 2, 2]))
    print(solve_n_queens(4))
    print(generate_parenthesis(3))
```

## 复杂度
| 问题 | 时间 | 空间 |
|---|---|---|
| 全排列 | O(n·n!) | O(n) 递归栈（不含结果） |
| 子集 | O(n·2ⁿ) | O(n) |
| 组合总和 | 指数级，剪枝后大幅下降 | O(target/最小值) |
| N 皇后 | 最坏 O(n!)，剪枝后远小于此 | O(n) |
| 括号生成 | O(第 n 个卡特兰数) | O(n) |

回溯类问题**没有多项式解法**，复杂度天然指数级，剪枝是唯一的优化手段。

## 易错点
- **`res.append(path[:])` 必须拷贝**：直接 `append(path)` 存的是引用，后续 `path.pop()` 会让结果全部变成空列表。
- 撤销选择必须**完整撤销**所有修改：N 皇后里 cols/diag1/diag2/queens 四处都要回退，漏一处就会污染兄弟分支。
- `dfs(i)` 与 `dfs(i+1)` 的区别：传 `i` 表示当前元素**可重复使用**（组合总和），传 `i+1` 表示**每个元素只能用一次**（子集、组合）。
- 去重剪枝的必要条件是**先排序**，否则相同元素不相邻，`nums[i] == nums[i-1]` 判断失效。
- 去重用的是 `i > start`（同层跳过）而不是 `i > 0`（会错误地跳过跨层的合法解）。
- 可行性剪枝用 `break` 而不是 `continue`：数组已排序，当前元素超限则后面全部超限。
- 递归深度过大时会栈溢出，可用 `sys.setrecursionlimit()` 或改写为显式栈迭代版。
- 判断"要不要终止搜索"：只要一个解就在找到时 `return`（但要小心撤销状态），要所有解则继续遍历。
