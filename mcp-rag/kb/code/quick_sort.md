# 快速排序（Quick Sort）

## 一、核心思想

快速排序采用**分治（Divide & Conquer）**策略，核心三步：

1. **选基准（Pivot）**：从数组中选一个元素作为分界点。
2. **分区（Partition）**：将数组重排，使小于基准的放左边、大于基准的放右边。
3. **递归**：对左右两个子区间分别递归执行步骤 1-2，直到区间长度为 1。

> 关键洞察：一趟分区后，**基准元素的位置就是最终排序完成后的位置**，不再变动。

---

## 二、两种常见实现

### 2.1 原地排序版（推荐，空间 O(log n)）

使用双指针 `i`（左游标）和 `j`（右游标），向中间逼近，将不等于基准的元素交换到正确的一侧。

```python
def quick_sort_inplace(nums, left=None, right=None):
    """原地快速排序（闭区间 [left, right]）"""
    if left is None:
        left, right = 0, len(nums) - 1
    if left >= right:
        return

    # 分区：返回基准最终落点
    pivot_idx = _partition(nums, left, right)
    quick_sort_inplace(nums, left, pivot_idx - 1)
    quick_sort_inplace(nums, pivot_idx + 1, right)


def _partition(nums, left, right):
    """双指针分区，选最右元素为基准"""
    pivot = nums[right]          # 基准
    i = left - 1                 # i 指向"小于基准"区域的最后一个位置

    for j in range(left, right):
        if nums[j] <= pivot:
            i += 1
            nums[i], nums[j] = nums[j], nums[i]

    # 把基准放到中间
    nums[i + 1], nums[right] = nums[right], nums[i + 1]
    return i + 1


# 测试
if __name__ == "__main__":
    arr = [3, 6, 8, 10, 1, 2, 1]
    quick_sort_inplace(arr)
    print(arr)   # [1, 1, 2, 3, 6, 8, 10]
```

### 2.2 辅助空间版（简洁直观，空间 O(n)）

利用列表推导式快速拆分左右子数组，代码短但额外消耗空间。

```python
def quick_sort_extra(nums):
    """非原地，额外空间 O(n)，适合理解思路"""
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    left  = [x for x in nums if x < pivot]
    mid   = [x for x in nums if x == pivot]
    right = [x for x in nums if x > pivot]
    return quick_sort_extra(left) + mid + quick_sort_extra(right)
```

---

## 三、复杂度分析

| 场景 | 时间复杂度 | 空间复杂度 | 说明 |
|------|-----------|-----------|------|
| **平均情况** | O(n log n) | O(log n) | 每次分区大致对半分 |
| **最好情况** | O(n log n) | O(log n) | 基准恰好选中位数 |
| **最坏情况** | O(n²) | O(n) | 数组已有序，基准每次都选到最大/最小值 |
| **稳定性** | **不稳定** | — | 相等元素交换后相对顺序可能改变 |

> 注：原地版的空间是递归栈深度，平均 O(log n)，最坏 O(n)。

---

## 四、易错点与注意事项

1. **基准选择不当导致退化**
   - 固定选最左/最右元素，在**已排序数组**上会退化到 O(n²)。
   - **优化**：随机选基准，或"三数取中"（取首尾中三个数的中位数）。

2. **分区时等号方向写反**
   - `if nums[j] <= pivot:` 放 `i` 区；写成 `<` 会导致与基准相等的元素被分到两边，不影响正确性但可能增加递归深度。

3. **递归边界条件**
   - 一定是 `left >= right` 时返回，不能写 `left == right`（可能传空区间）。

4. **原地版忘记把基准交换到中间**
   - 循环结束后必须执行 `nums[i+1], nums[right] = nums[right], nums[i+1]`，否则基准仍在最右。

5. **python 默认递归深度限制**
   - 极端退化情况下递归深度可能超过 1000，触发 `RecursionError`。可用 `sys.setrecursionlimit()` 放宽，或改迭代版。

---

## 五、常见考题

1. **快排是稳定排序吗？为什么？**
   - 不是。分区时的交换会改变相等元素的相对顺序。

2. **已有序数组用快排会退化吗？怎么优化？**
   - 会退化到 O(n²)。优化：随机选基准，或三数取中。

3. **快排和归并排序的核心区别？**
   - 快排是"先分区再递归"，归并是"先递归再合并"。快排主要工作在分区（O(n)），归并主要工作在合并（O(n)）。

4. **快排适合链表吗？**
   - 不适合原地双指针版本（链表不支持随机访问），但归并排序非常适合链表。

5. **Top K 问题能用快排思想做吗？**
   - 可以。每次分区后只递归包含第 K 元素的那一侧，平均 O(n)。

---

## 六、快速记忆口诀

> 选基准、分左右，基准位置终不动；  
> 左小右大再递归，平均 n log n 稳；  
> 已排序时最吃亏，随机取中防退化。
