# 快速排序

快速排序采用分治策略：选一个基准，把小于基准的放左边、大于基准的放右边，再递归排序两侧。

```python
def quick_sort(nums):
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    left = [x for x in nums if x < pivot]
    mid = [x for x in nums if x == pivot]
    right = [x for x in nums if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)
```

平均时间复杂度 O(n log n)。