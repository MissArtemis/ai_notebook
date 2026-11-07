# 一份线段树模板，四道题

沿用原模板的 `tree、lazy、p/l/r` 和递归写法。四题共用同一个模板，各自只决定叶子代表什么、需要哪些操作。

| 题目 | 叶子表示什么 | 节点维护什么 | 使用的操作 |
| --- | --- | --- | --- |
| [60. 排列序列](https://leetcode.cn/problems/permutation-sequence/) | 数字是否还可用（0或1） | 可用数字数量 | 第k个、单点赋值 |
| [2916. 子数组不同元素数目的平方和 II](https://leetcode.cn/problems/subarrays-distinct-element-sum-of-squares-ii/) | 固定右端点时，以该下标为左端点的子数组的不同元素数 | 不同元素数之和 | 区间加、区间求和 |
| [4099. 将锁定数组排序的最少操作次数（526 Q3）](https://leetcode.cn/problems/minimum-operations-to-sort-with-locked-indices/) | 某个数在已扫描前缀中的出现次数 | 已出现的数字数量 | 单点加、前缀求和 |
| [4086. 覆盖目标区间的最少区间（524 Q4）](https://leetcode.cn/problems/minimum-interval-selection-to-cover-target-intervals/) | 按左端点排序后，每个可选区间的右端点 | 最大右端点 | 前缀最大值 |

## 公共模板

完整代码见同目录的 [segment_tree_template.py](segment_tree_template.py)。配套Jupyter已将模板放在第一个代码单元，按顺序运行即可。提交力扣时，复制公共模板和对应题目的 `Solution`，以及该题使用的导入语句。

本模板覆盖**区间加 + 区间和/最大值 + 单点赋值 + 按计数查第k个**。区间赋值或区间乘法等操作，需要另外设计懒标记。

- 数组下标从 **0** 开始，所有区间都是**闭区间**；初始数组必须非空，调用者保证下标合法。
- `mode="sum"`：左右区间相加，空区间的结果是0。
- `mode="max"`：左右区间取最大值，空区间的结果是负无穷。这样全是负数时也不会误返回0。
- `add(l, r, value)`：区间内每个值增加value；单点加就是 `add(i, i, value)`。
- `update(i, value)`：把这一点**直接改成**value。
- `kth(k)`：只用于sum模式，返回第k个计数所在的下标。每个叶子必须为非负整数，排名从1开始，且不能超过总计数。非负前提由调用者保证，模板不会逐个检查叶子。
- 模板内部不取模；第k个查询需要准确计数。

`tree[p]` 已经包含当前节点收到的更新；`lazy[p]` 记录已经反映在当前节点、尚未传给孩子的区间增量。整段命中时直接处理；进入孩子之前先下推，修改孩子之后再合并。

| 函数 | 作用 |
| --- | --- |
| `_build` | 建树 |
| `_pull` | 从左右孩子合并当前节点 |
| `_apply` | 把整段增加量作用到当前节点，并记录懒标记 |
| `_push` | 把懒标记下传给孩子 |
| `add` / `query` | 区间加 / 区间查询 |
| `update` | 单点赋值 |
| `kth` | 按左子树计数决定走左边还是右边 |

建树时间和空间都是O(n)；四种操作的单次时间均为O(log n)。

<!-- shared-template -->

```python
# 同一模板的基本用法
seg = SegmentTree([1, 2, 3])
assert seg.query(0, 2) == 6
seg.add(0, 1, 2)             # [3, 4, 3]
assert seg.query(0, 2) == 10
seg.update(1, 0)             # [3, 0, 3]
assert seg.query(0, 2) == 6
assert seg.kth(4) == 2       # 前3个计数在下标0，第4个在下标2

seg = SegmentTree([-5, -2, -8], mode="max")
assert seg.query(0, 2) == -2
seg.add(1, 2, 3)             # [-5, 1, -5]
assert seg.query(0, 2) == 1
assert seg.query(0, -1) == float("-inf")

# kth进入孩子之前也必须下推懒标记
seg = SegmentTree([0, 0, 0, 0])
seg.add(0, 3, 1)
assert seg.kth(3) == 2
print("公共模板示例通过")
```

## 例一：60. 排列序列

剩余m个数字时，固定当前位，后面有(m-1)!种排列。把排列编号k转成从0开始后：

- 当前位选择剩余数字中第 `k // fact[m-1] + 1` 小的数。
- 用 `k %= fact[m-1]` 得到所选分组内的排列编号。

叶子为1表示数字可用，为0表示已使用，因此 `kth(rank)` 返回对应下标，取走后用 `update(index, 0)` 删除。

注意：**排列编号k从0开始，数字排名rank从1开始，叶子下标index从0开始，实际数字是index+1。**

时间O(n log n)，空间O(n)。本题n不超过9，有序列表也足够；这里用于练习动态第k小。

```python
class Solution:
    def getPermutation(self, n: int, k: int) -> str:
        fact = [1] * (n + 1)
        for i in range(1, n + 1):
            fact[i] = fact[i-1] * i

        seg = SegmentTree([1] * n)
        answer = []
        k -= 1

        for m in range(n, 0, -1):
            size = fact[m-1]
            rank = k // size + 1
            k %= size

            index = seg.kth(rank)
            answer.append(str(index + 1))
            seg.update(index, 0)

        return ''.join(answer)
```

```python
solution60 = Solution()
assert solution60.getPermutation(3, 3) == "213"
assert solution60.getPermutation(4, 9) == "2314"
assert solution60.getPermutation(3, 1) == "123"
print(solution60.getPermutation(4, 9))
```

## 例二：2916. 子数组不同元素数目的平方和 II

保留原来的“枚举右端点”思路。处理右端点r时，叶子i表示 `nums[i:r+1]` 的不同元素数，i大于r的位置为0。

设当前数字上次出现于prev，没出现过就取-1。加入当前数字后，恰好只有左端点在 `[prev+1, r]` 的子数组，其不同元素数会加1。

原计数为c时，平方的增量为 `(c+1)^2-c^2 = 2c+1`。因此先查询这一段旧计数之和old_sum，平方和增量就是 `2*old_sum + 区间长度`，再执行区间加一。

ending表示以当前r为右端点的所有子数组的平方和。把每个右端点的ending累加，就是答案。新左端点r的原计数为0，第一次加一的贡献也包含在公式里。

必须**先查询旧和，再区间加一**。树里维护的是不同元素数之和，平方和由增量公式维护。

时间O(n log n)，空间O(n)。

```python
class Solution:
    def sumCounts(self, nums: list[int]) -> int:
        mod = 10**9 + 7
        seg = SegmentTree([0] * len(nums))
        last = {}
        ending = 0
        answer = 0

        for r, x in enumerate(nums):
            prev = last.get(x, -1)
            left = prev + 1

            old_sum = seg.query(left, r)
            ending += 2 * old_sum + (r-left+1)
            seg.add(left, r, 1)

            answer = (answer + ending) % mod
            last[x] = r

        return answer
```

```python
solution2916 = Solution()
assert solution2916.sumCounts([1, 2, 1]) == 15
assert solution2916.sumCounts([2, 2]) == 3
print(solution2916.sumCounts([1, 2, 1]))
```

## 例三：4099. 将锁定数组排序的最少操作次数（第526场周赛Q3）

沿用现有逻辑：**答案 = 必须解锁的位置数 + 逆序对数**。只替换原来树状数组统计逆序对的部分。

锁定位置i可以保留，当且仅当：

1. `nums[i] == i+1`，它已经在最终位置。
2. 前缀最大值不超过i+1，左边没有需要跨过这个位置的大数。

由于nums是1到n的排列，这两个条件保证左侧恰好是1到i，右侧都是更大的数。因此这些位置能成为排序过程的分界。其他锁定位置都必须解锁，若数量超过k就返回-1。

解锁后，可以在剩余分界之间分别用相邻交换排序。相邻交换的最少次数就是逆序对数，而且分界两侧没有跨越分界的逆序对。

统计逆序对时，叶子下标num-1表示数字num已经出现几次。扫描到第i个数时，前面共有i个数；`query(0, num-1)` 统计其中小于等于num的数量，二者相减得到前面大于num的数量。

这里叶子按**数字值**索引，跟原数组的位置下标含义不同。

时间O(n log n)，空间O(n)。

```python
class Solution:
    def minOperations(self, nums: list[int], locked: list[int], k: int) -> int:
        max_num = 0
        lock_cnt = 0
        n = len(nums)

        for i, num in enumerate(nums):
            max_num = max(max_num, num)
            if locked[i]:
                if num != i+1 or max_num > i+1:
                    lock_cnt += 1
                    if lock_cnt > k:
                        return -1

        seg = SegmentTree([0] * n)
        swap_cnt = 0

        for i, num in enumerate(nums):
            swap_cnt += i - seg.query(0, num-1)
            seg.add(num-1, num-1, 1)

        return swap_cnt + lock_cnt
```

```python
solution4099 = Solution()
assert solution4099.minOperations([2, 1, 3, 4], [0, 1, 0, 1], 1) == 2
assert solution4099.minOperations([3, 1, 2], [1, 0, 1], 2) == 4
assert solution4099.minOperations([2, 3, 1], [1, 0, 0], 0) == -1
# 3虽然已在正确位置，但左侧有4需要跨过它，因此仍必须解锁
assert solution4099.minOperations([1, 4, 3, 2], [0, 0, 1, 0], 0) == -1
print(solution4099.minOperations([2, 1, 3, 4], [0, 1, 0, 1], 1))
```

## 例四：4086. 覆盖目标区间的最少区间（第524场周赛Q4）

保留原来的**合并目标区间 + 每次选择右端点最远的候选**的贪心思路。

当前要接上的位置为cur_start，需要在所有左端点不超过cur_start的可选区间中，查询最大的右端点。

1. 把可选区间按左端点排序，叶子存对应区间的右端点。
2. `bisect_right(starts, cur_start)-1` 找到满足左端点条件的最后一个下标index。
3. `query(0, index)` 查询这些候选中最大的右端点；没有候选时返回负无穷。

每次选择能延伸最远的区间：任意合法方案都需要覆盖当前尚未覆盖的位置，把这一步换成能到达最远处的区间，不会增加选取数量，也不会缩短后续可达范围。

covered_end要跨目标区间保留；目标之间的空白可以跳过。覆盖的是**实数点**，接到右端点x后从x继续，不能从x+1继续。

失败条件沿用 `next_end < cur_start or next_end == covered_end`。不要改成 `next_end <= cur_start`：单点目标 `[5,5]` 可以被单点候选 `[5,5]` 覆盖。

这一题的线段树只做静态前缀最大值查询。原来的排序加双指针实现更简洁，预处理前缀最大值也能完成这些查询。本例用来理解max模式；贪心策略仍是求最少区间数的关键。

设可选区间数为a、目标区间数为t，时间O(a log a + t log t)，空间O(a+t)。每次成功选择都会到达一个严格更大的候选右端点，选择次数至多a。

```python
from bisect import bisect_right


class Solution:
    def minSelection(self, availableIntervals: list[list[int]],
                     targetIntervals: list[list[int]]) -> int:
        sorted_target = sorted(targetIntervals, key=lambda x: x[0])
        merged_target = []
        for start, end in sorted_target:
            if merged_target and start <= merged_target[-1][1]:
                merged_target[-1][1] = max(merged_target[-1][1], end)
            else:
                merged_target.append([start, end])

        sorted_available = sorted(availableIntervals, key=lambda x: x[0])
        starts = [start for start, end in sorted_available]
        seg = SegmentTree([end for start, end in sorted_available], mode="max")

        ans = 0
        covered_end = float('-inf')
        for start, end in merged_target:
            cur_start = max(start, covered_end)
            while covered_end < end:
                index = bisect_right(starts, cur_start) - 1
                next_end = seg.query(0, index)
                if next_end < cur_start or next_end == covered_end:
                    return -1

                ans += 1
                covered_end = next_end
                cur_start = covered_end

        return ans
```

```python
solution4086 = Solution()
available = [[1, 4], [1, 7], [3, 9], [5, 10], [10, 15]]
targets = [[1, 3], [2, 5], [7, 8], [10, 13], [11, 15], [12, 13]]
assert solution4086.minSelection(available, targets) == 3
assert solution4086.minSelection([[4, 6], [1, 4], [2, 5]], [[3, 4], [2, 5], [6, 7]]) == -1
assert solution4086.minSelection([[1, 2], [3, 4]], [[1, 4]]) == -1
assert solution4086.minSelection([[5, 5]], [[5, 5]]) == 1
assert solution4086.minSelection([[1, 10]], [[1, 2], [8, 9]]) == 1
assert solution4086.minSelection([[1, 2], [8, 9]], [[1, 2], [8, 9]]) == 2
assert solution4086.minSelection([[6, 7]], [[5, 5]]) == -1
print(solution4086.minSelection(available, targets))
```

## 复习时重点检查

1. **叶子代表什么？** 60与4099按数字值索引；2916按子数组左端点索引；4086按排序后的候选区间索引。
2. **节点如何合并？** 数量相加用sum，最远右端点用max；区间加对应的_apply也随之调整。
3. **赋值还是累加？** `update(i, 0)` 删除可用数字，`add(i, i, 1)` 增加计数。
4. **什么时候下推？** 要访问孩子时，包括部分区间查询、单点赋值和kth查询。
5. **第k个查询的前提？** sum模式、准确计数、非负整数叶子。
6. **线段树解决哪一步？** 先确定数学分组、增量公式、逆序对或贪心策略，再加速其中的查询与更新。
