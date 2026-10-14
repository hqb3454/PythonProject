# Trie 字典树（前缀树）

## 思路
- Trie 是一棵**多叉树**，用"边表示字符、结点表示前缀"，从根到某结点的路径拼起来就是一个字符串。
- 核心优势：**共享公共前缀**，把字符串集合的存储与查找都压缩到 O(总字符数)。
- 两个基本操作：
  - `insert(word)`：沿字符逐层走，没有结点就新建，最后在终点打上 `is_end` 标记。
  - `search(prefix)`：沿字符走，能走完说明前缀存在；终点 `is_end` 为 True 才是完整单词。
- 典型用途：前缀自动补全、拼写检查、词频统计、敏感词过滤、路由器最长前缀匹配、AC 自动机的基础。
- 与哈希表对比：哈希表查整词 O(1) 但**不支持前缀查询**；Trie 支持前缀查询且能按字典序遍历。

## 代码

```python
from typing import List, Dict, Optional


class TrieNode:
    """用字典存子结点，支持任意字符集"""

    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end: bool = False      # 是否有单词在此结束
        self.pass_count: int = 0       # 有多少单词经过该结点（前缀出现次数）
        self.word_count: int = 0       # 该单词被插入的次数（支持重复插入）


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            node.pass_count += 1
        node.is_end = True
        node.word_count += 1

    def search(self, word: str) -> bool:
        """完整单词是否存在"""
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """是否存在该前缀"""
        return self._find(prefix) is not None

    def count_prefix(self, prefix: str) -> int:
        """有多少单词以该前缀开头"""
        node = self._find(prefix)
        return node.pass_count if node else 0

    def words_with_prefix(self, prefix: str) -> List[str]:
        """返回所有以 prefix 开头的单词（DFS 收集）"""
        node = self._find(prefix)
        if node is None:
            return []
        res = []

        def dfs(cur: TrieNode, path: str):
            if cur.is_end:
                res.append(path)
            for ch, nxt in cur.children.items():
                dfs(nxt, path + ch)

        dfs(node, prefix)
        return res

    def erase(self, word: str) -> bool:
        """删除一个单词，返回是否删除成功"""
        node = self._find(word)
        if node is None or not node.is_end:
            return False
        node.is_end = False
        node.word_count -= 1
        cur = self.root
        for ch in word:                 # 沿路递减 pass_count
            cur = cur.children[ch]
            cur.pass_count -= 1
        return True

    def _find(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node


def longest_common_prefix(words: List[str]) -> str:
    """用 Trie 求一组字符串的最长公共前缀"""
    if not words:
        return ""
    t = Trie()
    for w in words:
        t.insert(w)
    node = t.root
    prefix = []
    # 只有一个子结点且不是单词结尾时才继续往下走
    while len(node.children) == 1 and not node.is_end:
        ch, node = next(iter(node.children.items()))
        prefix.append(ch)
    return "".join(prefix)


if __name__ == "__main__":
    t = Trie()
    for w in ["apple", "app", "application", "banana", "band"]:
        t.insert(w)
    print(t.search("app"))            # True
    print(t.search("ap"))             # False（只是前缀）
    print(t.starts_with("ap"))        # True
    print(t.count_prefix("app"))      # 3
    print(t.words_with_prefix("ban")) # ['banana', 'band']
    print(longest_common_prefix(["flower", "flow", "flight"]))  # 'fl'
```

## 复杂度
| 操作 | 时间 | 说明 |
|---|---|---|
| insert(word) | O(L) | L 为单词长度，逐字符走 |
| search / starts_with | O(L) | 与单词总数 n 无关，这是比"遍历所有单词"快的原因 |
| count_prefix | O(L) | 维护 pass_count 才能 O(1) 取到 |
| 空间 | O(ΣL) | 最坏是所有单词字符总数；字符集大时每个结点用哈希表更省空间 |

对比：用集合存单词再逐前缀判断是 O(n·L)，Trie 稳定 O(L)。

## 易错点
- **`is_end` 标记不能少**：它区分"前缀"和"完整单词"，只有它能判断 `search("ap")` 应为 False。
- 查前缀与查单词是两个方法，别混用；`starts_with` 不检查 `is_end`。
- 用字典存 children 时，`collections.defaultdict(TrieNode)` 要小心：访问不存在的键会自动创建结点，导致 `search` 误判为存在。**查询时应显式用 `in` 判断**。
- 删除操作要先确认单词存在，并沿路回退 `pass_count`；若要真正释放内存还需递归删除无用分支（一般题目不要求）。
- 递归 DFS 收集单词在树很深时可能栈溢出，可改成显式栈。
- 字符集固定为小写字母时可用数组 `[None]*26` 代替字典，速度更快，但要注意字符到下标转换 `ord(ch) - ord('a')`。
- Trie 的空间开销可能很大（每个字符一个结点），字符集大且无公共前缀时反而不如哈希表。
