# LRU 缓存

## 思路
- **LRU（Least Recently Used）**：容量满时淘汰**最久未被访问**的数据。
- 需要两个操作都 O(1)：
  - 查询 O(1) → **哈希表**；
  - 维护访问顺序（把刚用的移到"最新"、淘汰"最旧"）O(1) → **双向链表**。
- 经典组合：**哈希表 + 双向链表**。
  - 链表头部（dummy head 之后）放最近使用的，尾部放最久未使用的；
  - `get` 命中后把该结点移到头部；
  - `put` 已存在则更新值并移到头部，不存在则插入头部，超容量则删除尾结点。
- 用**哨兵结点（dummy head/tail）**可以省去所有"头尾为空"的边界判断。
- Python 捷径：`collections.OrderedDict` 内置了顺序维护，`move_to_end` + `popitem(last=False)` 即可实现，代码量极小（面试手写推荐自己实现链表版）。

## 代码

```python
from collections import OrderedDict
from typing import Optional


class DLinkedNode:
    """双向链表结点"""

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: Optional["DLinkedNode"] = None
        self.next: Optional["DLinkedNode"] = None


class LRUCache:
    """哈希表 + 双向链表，get/put 均 O(1)"""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.cap = capacity
        self.cache = {}                     # key -> DLinkedNode
        # 哨兵结点，简化边界处理
        self.head = DLinkedNode()
        self.tail = DLinkedNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: DLinkedNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node: DLinkedNode) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _move_to_head(self, node: DLinkedNode) -> None:
        self._remove(node)
        self._add_to_head(node)

    def _pop_tail(self) -> DLinkedNode:
        node = self.tail.prev
        self._remove(node)
        return node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._move_to_head(node)            # 访问后变为最近使用
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
            return
        node = DLinkedNode(key, value)
        self.cache[key] = node
        self._add_to_head(node)
        if len(self.cache) > self.cap:
            removed = self._pop_tail()
            del self.cache[removed.key]     # 别忘了同步删哈希表

    def __len__(self) -> int:
        return len(self.cache)


class LRUCacheSimple:
    """用 OrderedDict 的简洁实现"""

    def __init__(self, capacity: int):
        self.cap = capacity
        self.od = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.od:
            return -1
        self.od.move_to_end(key)            # 移到末尾 = 最近使用
        return self.od[key]

    def put(self, key: int, value: int) -> None:
        if key in self.od:
            self.od[key] = value
            self.od.move_to_end(key)
            return
        self.od[key] = value
        if len(self.od) > self.cap:
            self.od.popitem(last=False)     # 弹出最前面的 = 最久未使用


if __name__ == "__main__":
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    print(c.get(1))      # 1  （1 变为最近使用）
    c.put(3, 3)          # 淘汰 key=2
    print(c.get(2))      # -1
    print(c.get(3))      # 3
    c.put(4, 4)          # 淘汰 key=1
    print(c.get(1))      # -1
    print(c.get(3))      # 3
    print(c.get(4))      # 4

    s = LRUCacheSimple(2)
    s.put(1, 1); s.put(2, 2)
    s.get(1); s.put(3, 3)
    print(s.get(2))      # -1
```

## 复杂度
| 操作 | 时间 | 说明 |
|---|---|---|
| get | O(1) | 哈希查找 + 链表摘接 |
| put | O(1) | 哈希插入 + 头插 + 可能删尾 |
| 空间 | O(capacity) | 哈希表与链表各存一份引用 |

对比：用数组/列表实现，get 是 O(1) 但"移动元素"是 O(n)，整体退化成 O(n)。

## 易错点
- 淘汰时必须**同时删除哈希表中的条目**，只删链表结点会留下悬挂引用，导致后续 `get` 到已删除的结点。
- `_move_to_head` 要先 `_remove` 再 `_add_to_head`，且 `_add_to_head` 中四条指针的赋值顺序必须正确（先接新结点的两端，再改原后继，最后改 head.next）。
- 用哨兵 head/tail 能消除所有空指针判断；不用哨兵时每个操作都要判"是否是头/尾结点"，极易漏。
- `put` 已存在的 key 时，除了更新 value 还要**移到头部**，否则淘汰顺序错误。
- 容量为 0 或负数要提前处理（抛异常或直接不缓存）。
- OrderedDict 版中 `move_to_end` 默认移到末尾，则 `popitem(last=False)` 弹最前面——**两端约定要一致**，混淆就会淘汰刚使用的数据。
- LRU 与 FIFO 的区别：FIFO 只在插入时排序，`get` 不改变顺序；LRU 的 `get` 会刷新"最近使用"标记。这也是 LFU（按访问频次）与 LRU 的根本差异。
- 实际工程中的 LRU 常用于：数据库缓冲池、Redis 的 maxmemory-policy（近似 LRU）、操作系统页面置换（LRU 的近似实现 Clock）。
