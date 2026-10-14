# 最短路径：Dijkstra / Bellman-Ford / Floyd

## 思路
- 三类最短路径问题：
  - **单源最短路径**（一个点到所有点）：Dijkstra（非负权）、Bellman-Ford（可含负权）；
  - **多源最短路径**（任意两点）：Floyd（动态规划）；
  - **无权图单源**：BFS 即可（首次到达即最短）。
- **Dijkstra（贪心）**：维护 dist 数组，每轮从未确定集合中选出 dist 最小的顶点 u，用 u 的所有出边做"松弛"（`dist[v] = min(dist[v], dist[u] + w)`）。
  - 正确性依赖：边权非负时，当前 dist 最小的顶点不可能再被更短路径更新。
- **Bellman-Ford**：对所有边松弛 n-1 轮；若第 n 轮仍能松弛，说明存在**负权回路**（最短路径无解）。
- **Floyd**（DP）：`dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])`，三重循环，k 必须在最外层。

## 代码

```python
import heapq
from typing import List, Dict, Tuple

INF = float("inf")


def dijkstra_heap(graph: Dict[int, List[Tuple[int, int]]], start: int, n: int):
    """堆优化 Dijkstra，适合稀疏图。graph[u] = [(v, w), ...]"""
    dist = [INF] * n
    dist[start] = 0
    pq = [(0, start)]                       # (当前距离, 顶点)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:                     # 惰性删除：过期的旧记录
            continue
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def dijkstra_matrix(mat: List[List[int]], start: int):
    """朴素 O(n^2) Dijkstra，适合稠密图。mat[i][j] 为边权，0 或 INF 表示无边"""
    n = len(mat)
    dist = [INF] * n
    visited = [False] * n
    dist[start] = 0
    for _ in range(n):
        u, best = -1, INF
        for i in range(n):                  # 线性扫描找最小，O(n)
            if not visited[i] and dist[i] < best:
                u, best = i, dist[i]
        if u == -1:
            break
        visited[u] = True
        for v in range(n):
            if not visited[v] and mat[u][v] and dist[u] + mat[u][v] < dist[v]:
                dist[v] = dist[u] + mat[u][v]
    return dist


def dijkstra_with_path(graph, start: int, n: int):
    """返回距离与前驱数组，可还原最短路径"""
    dist = [INF] * n
    prev = [-1] * n
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph.get(u, []):
            if d + w < dist[v]:
                dist[v] = d + w
                prev[v] = u                 # 记录前驱
                heapq.heappush(pq, (dist[v], v))
    return dist, prev


def build_path(prev, start: int, end: int) -> List[int]:
    """从 prev 数组还原 start -> end 的最短路径"""
    path, cur = [], end
    while cur != -1:
        path.append(cur)
        if cur == start:
            break
        cur = prev[cur]
    return path[::-1] if path[-1] == start else []


def bellman_ford(edges: List[Tuple[int, int, int]], n: int, start: int):
    """可处理负权边，返回 (dist, 是否有负权回路)。edges = [(u, v, w)]"""
    dist = [INF] * n
    dist[start] = 0
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:                     # 提前收敛
            break
    neg_cycle = any(dist[u] != INF and dist[u] + w < dist[v]
                    for u, v, w in edges)
    return dist, neg_cycle


def floyd(mat: List[List[int]]):
    """全源最短路径，mat[i][j] 为边权，无边用 INF，对角线为 0"""
    n = len(mat)
    dist = [row[:] for row in mat]
    for k in range(n):                      # k 必须在最外层
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


if __name__ == "__main__":
    g = {0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 5)], 3: []}
    print(dijkstra_heap(g, 0, 4))            # [0, 3, 1, 4]
    d, p = dijkstra_with_path(g, 0, 4)
    print(build_path(p, 0, 3))               # [0, 2, 1, 3]

    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)]
    print(bellman_ford(edges, 4, 0))         # ([0, 3, 1, 4], False)

    m = [[0, 4, 1, INF], [INF, 0, INF, 1], [INF, 2, 0, 5], [INF, INF, INF, 0]]
    print(floyd(m))                          # 全源最短距离矩阵
```

## 复杂度
| 算法 | 时间 | 空间 | 限制 |
|---|---|---|---|
| Dijkstra（朴素） | O(n²) | O(n) | 边权非负，适合稠密图 |
| Dijkstra（堆优化） | O(e log n) | O(n+e) | 边权非负，适合稀疏图 |
| Bellman-Ford | O(n·e) | O(n) | 可含负权，能检测负环 |
| Floyd | O(n³) | O(n²) | 可含负权，不能有负环 |

## 易错点
- **Dijkstra 遇到负权边会出错**：已确定的顶点可能后续被更短路径更新，贪心前提被破坏。有负权请换 Bellman-Ford。
- 堆优化版必须写 `if d > dist[u]: continue`（惰性删除），否则过期记录会被重复处理；这不是优化而是正确性所需。
- 不能用 `visited` 数组在堆优化版中标记"已确定"，因为一个顶点可能被多次入堆（每次距离变短都要入）。
- Floyd 的三重循环中 **k 必须在最外层**，写成最内层会得出错误结果（这是最经典的考点）。
- 初始化：自己到自己是 0，无边是 INF，不要用 0 表示无边（会与真实零权边混淆）。
- `INF` 参与加法可能溢出：C/C++ 里要用足够大的值并判断 `dist[u] != INF` 再松弛。
- 还原路径时必须检查 `path[-1] == start`，否则不可达时会返回一条残缺路径。
- 最短路径与最小生成树目标不同：前者求"两点间距离最小"，后者求"连通所有点总权值最小"，不要混用算法。
