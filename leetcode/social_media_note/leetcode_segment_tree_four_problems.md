# 线段树到底存什么？用一份 Python 模板串起 4 道题

最近刷题，碰到了四道都能用线段树来写的题：排列序列、锁定数组排序、不同元素数目的平方和，还有区间覆盖。

刚开始看模板，我最容易卡在这一串东西上：`p * 2`、`p * 2 + 1`、`push`、`pull`、`lazy`。

代码看着都认识，合起来却不知道为什么要这样写。尤其是第 60 题：题目让我找一个排列，怎么就扯上线段树了？

后来我发现，得先把每道题翻译成一句具体的话，再去看模板。

这篇就按这个顺序来：**先解释题目为什么能用线段树，再确定每个位置存什么，最后把代码填进同一份模板。** 四题都使用下面这个 `SegmentTree`，内部代码不换。

## 1. 先把线段树理解成“分块记账”

假设有数组 `[1, 2, 3, 4]`，我们想反复查询某一段的和，还会修改里面的数字。

可以先把它分成两半，分别记下总和，再继续分，直到每块只剩一个数字：

```text
                     [0,3]：和为10
                    /            \
             [0,1]：和为3     [2,3]：和为7
               /     \          /     \
          [0]：1   [1]：2    [2]：3   [3]：4
```

问 `[0,1]` 的和，树里已经有这一块的答案，直接拿走。修改下标1的数字，就更新它所属的 `[1]`、`[0,1]`、`[0,3]`，另一半不用动。

这就是线段树的基本工作：**把一个范围不断分成两半，每一块保存一个可以由左右两块合并出来的结果。**

模板里的三个变量可以这样读：

| 变量 | 含义 |
| --- | --- |
| `p` | 当前这一块的节点编号 |
| `l, r` | 当前这一块负责的原数组下标范围，包含左右端点 |
| `tree[p]` | 当前这一块保存的结果 |

根节点编号为1。编号为p的节点，它的左孩子编号是 `p*2`，右孩子编号是 `p*2+1`。

注意：**p是树里的编号，l和r才是原数组的下标。**

### 一块里，究竟记什么账？

这才是换题时最需要重新想的地方。

如果每个位置存0或1，表示一个数字是否还可用，那么一段的和，就是这一段还有几个数字可以选。

如果每个位置存某个数字出现了几次，那么一段的和，就是某一段值域内出现过多少个数字。

如果每个位置存一个区间的右端点，那么一段的最大值，就是这些区间最远能到哪里。

同样在操作一棵树，叶子代表的东西可以不同，左右孩子的合并规则也可以不同。

### lazy：整块都加一个数，先记下来

如果一块有4个数字，现在每个数字都加2，那么这一块的总和直接加8就行。

暂时不用立刻修改下面的每个数字，先记录：

```text
tree[p]：这一块的总和已经加过8了。
lazy[p]：下面还没收到更新，每个数字以后还要加2。
```

所以，lazy记录的是**每个元素待下传的增加量**，不是整块总和的增加量。

之后真要进入孩子时，再把这笔增加量传下去。

```text
push：把之前记下的增加量往下传。
pull：孩子修改完，把结果往上重新合并。
```

记住：当前节点的 `tree[p]` 已经更新过，`push` 时不会再把同一笔增加量重复加到当前节点。

## 2. 四题共用的线段树模板

这份模板支持：

| 调用 | 含义 |
| --- | --- |
| `SegmentTree(nums)` | 建一棵维护区间和的树 |
| `SegmentTree(nums, mode="max")` | 建一棵维护区间最大值的树 |
| `add(l, r, value)` | 闭区间内每个元素增加value |
| `query(l, r)` | 查询闭区间的和或最大值 |
| `update(i, value)` | 把下标i的元素直接改成value |
| `kth(k)` | sum模式下，找到第k个计数所在的下标 |

统一约定：原数组下标从0开始，区间都是闭区间，初始数组非空，传入的非空区间下标合法。

`kth` 额外要求每个叶子是非负整数，排名从1开始，而且不能超过总计数。例如叶子 `[1,0,1,1]`，查询第2个，返回下标2。

建树时间和空间都是O(n)，单次查询、修改和第k个查询都是O(log n)。

```python
class SegmentTree:
    """区间加、区间查询、单点赋值；sum模式额外支持第k个计数。

    nums非空，下标从0开始，区间均为闭区间，调用者保证下标合法。
    mode='sum'维护区间和，mode='max'维护区间最大值。
    kth要求每个叶子的值都是非负整数，排名k从1开始。
    """

    def __init__(self, nums, mode="sum"):
        if not nums or mode not in ("sum", "max"):
            raise ValueError("nums必须非空，mode必须是sum或max")
        self.n = len(nums)
        self.mode = mode
        self.identity = 0 if mode == "sum" else float("-inf")
        self.merge = (lambda a, b: a + b) if mode == "sum" else max
        self.tree = [self.identity] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, nums)

    def _pull(self, p):
        self.tree[p] = self.merge(self.tree[p * 2], self.tree[p * 2 + 1])

    def _build(self, p, l, r, nums):
        if l == r:
            self.tree[p] = nums[l]
            return
        mid = (l + r) // 2
        self._build(p * 2, l, mid, nums)
        self._build(p * 2 + 1, mid + 1, r, nums)
        self._pull(p)

    def _apply(self, p, l, r, value):
        # 整段加value：区间和增加长度*value，区间最大值增加value。
        if self.mode == "sum":
            self.tree[p] += (r - l + 1) * value
        else:
            self.tree[p] += value
        self.lazy[p] += value

    def _push(self, p, l, r):
        if l == r or self.lazy[p] == 0:
            return
        mid = (l + r) // 2
        self._apply(p * 2, l, mid, self.lazy[p])
        self._apply(p * 2 + 1, mid + 1, r, self.lazy[p])
        self.lazy[p] = 0

    def add(self, left, right, value):
        """闭区间[left, right]内每个元素增加value。"""
        if left > right:
            return
        self._add(1, 0, self.n - 1, left, right, value)

    def _add(self, p, l, r, ql, qr, value):
        if ql <= l and r <= qr:
            self._apply(p, l, r, value)
            return
        self._push(p, l, r)
        mid = (l + r) // 2
        if ql <= mid:
            self._add(p * 2, l, mid, ql, qr, value)
        if qr > mid:
            self._add(p * 2 + 1, mid + 1, r, ql, qr, value)
        self._pull(p)

    def query(self, left, right):
        """查询区间和或最大值；空区间返回对应的单位元。"""
        if left > right:
            return self.identity
        return self._query(1, 0, self.n - 1, left, right)

    def _query(self, p, l, r, ql, qr):
        if ql <= l and r <= qr:
            return self.tree[p]
        self._push(p, l, r)
        mid = (l + r) // 2
        result = self.identity
        if ql <= mid:
            result = self.merge(result, self._query(p * 2, l, mid, ql, qr))
        if qr > mid:
            result = self.merge(result, self._query(p * 2 + 1, mid + 1, r, ql, qr))
        return result

    def update(self, index, value):
        """单点赋值：将nums[index]改为value，与add的增量含义不同。"""
        self._update(1, 0, self.n - 1, index, value)

    def _update(self, p, l, r, index, value):
        if l == r:
            self.tree[p] = value
            self.lazy[p] = 0
            return
        self._push(p, l, r)
        mid = (l + r) // 2
        if index <= mid:
            self._update(p * 2, l, mid, index, value)
        else:
            self._update(p * 2 + 1, mid + 1, r, index, value)
        self._pull(p)

    def kth(self, k):
        """sum模式：返回第k个计数所在的下标；叶子必须为非负整数。"""
        if self.mode != "sum" or not 1 <= k <= self.tree[1]:
            raise ValueError("kth要求sum模式，且1 <= k <= 总计数")
        return self._kth(1, 0, self.n - 1, k)

    def _kth(self, p, l, r, k):
        if l == r:
            return l
        # 区间加可能还未传给孩子，比较左子树计数前必须下推。
        self._push(p, l, r)
        mid = (l + r) // 2
        left_count = self.tree[p * 2]
        if k <= left_count:
            return self._kth(p * 2, l, mid, k)
        return self._kth(p * 2 + 1, mid + 1, r, k - left_count)
```

这段代码比较长，可以先对照函数名看它在做什么，不用一次背下来：

| 函数 | 可以怎么理解 |
| --- | --- |
| `_build` | 拆成左右两块，一直拆到单个元素，再合并 |
| `_pull` | 左右孩子已经算好，把当前节点重新算出来 |
| `_apply` | 当前这一整块都要加，先更新结果、记录lazy |
| `_push` | 要访问孩子了，把之前记录的增加量传下去 |
| `_add` | 整块命中就直接加；否则进入相关的孩子 |
| `_query` | 整块命中就直接返回；否则去相关的孩子里找 |
| `_update` | 找到一个叶子改值，再沿原路向上更新 |
| `_kth` | 看左边有几个，决定继续往哪边找 |

`tree` 和 `lazy` 都分配 `4*n` 个位置，是因为这份模板按父子编号存树，中间可能留空位。实际节点有 `2*n-1` 个，但最大编号不一定是 `2*n-1`，用 `4*n` 可以留够空间。

下面每题的代码，都配合上面这个公共类使用：复制公共类，再复制当前题的 `Solution` 和它使用的导入语句，就组成了完整代码。

## 3. 第60题：反复选出“剩余数字中的第几个”

[60. 排列序列](https://leetcode.cn/problems/permutation-sequence/)

### 为什么能用线段树？

题目给n和k，要找由1到n组成的所有排列中，按字典序排在第k个的排列。

我们可以从左到右，一位一位决定答案。每一位都要做两件事：

1. 在还没用的数字里，选出第几个小的。
2. 选完，把这个数字标记为已使用。

例如，剩余数字是：

```text
1、2、3、4
```

选第2小，选中2。接下来剩余数字是：

```text
1、3、4
```

再选第2小，这次就应该选3。

**线段树要帮忙的，就是数字不断被用掉后，仍然能快速找到剩余的第几个。**

### 先用阶乘算出：这一位该选第几个？

用 `n=4, k=9` 推演。第一位选定后，后面3个数字有 `3! = 6` 种排列，所以排列会按第一位分成四组：

```text
第1～6个：   1开头
第7～12个：  2开头
第13～18个： 3开头
第19～24个： 4开头
```

第9个在第二组，因此第一位选择第2小的可用数字，也就是2。

把排列编号改成从0开始，原来的第9个就变成编号8。每组有6个，整除就能得到它属于哪一组：

```text
rank = 8 // 6 + 1 = 2
```

进入这一组后，前面已经跳过了6个排列，组内编号就是：

```text
k = 8 % 6 = 2
```

剩m个数字时，对应的代码就是：

```python
size = fact[m-1]       # 当前位选定后，后面有多少种排列
rank = k // size + 1   # 选择剩余数字中第几小的
k %= size             # 进入这一组，继续找组内的排列
```

### 再用线段树找出：这个数字是谁？

每个数字对应一个位置，1表示可用，0表示已经使用：

```text
数字：1  2  3  4
下标：0  1  2  3
可用：1  1  1  1
```

这里树里维护的是**可用数字数量**，不是数字本身的和。

根的左半边有2个可用数字。找第2个，就进入左边。左边再看自己的左孩子，只有1个可用数字，于是跳过它，去右孩子找第1个。最终找到下标1，对应数字2。

选完执行 `update(1, 0)`：

```text
数字：1  2  3  4
可用：1  0  1  1
```

位置不会移动。下一轮找第2个时，线段树会跳过0，找到数字3。

完整过程如下，表里的k已经改成从0开始：

| 剩余数字 | k | 每组排列数 | 选第几小 | 选中数字 | 更新后的k |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1、2、3、4 | 8 | 6 | 2 | 2 | 2 |
| 1、3、4 | 2 | 2 | 2 | 3 | 0 |
| 1、4 | 0 | 1 | 1 | 1 | 0 |
| 4 | 0 | 1 | 1 | 4 | 0 |

最终得到 `2314`。

### 套用公共模板

```python
class Solution:
    def getPermutation(self, n: int, k: int) -> str:
        # fact[i]表示i!，包括fact[0]=1
        fact = [1] * (n + 1)
        for i in range(1, n + 1):
            fact[i] = fact[i-1] * i

        # 下标i对应数字i+1；所有数字一开始都可用
        seg = SegmentTree([1] * n)
        answer = []

        # 排列编号转成从0开始，方便整除分组
        k -= 1

        for m in range(n, 0, -1):
            # 剩m个数字时，每个候选数字开头的排列有(m-1)!个
            size = fact[m-1]
            rank = k // size + 1
            k %= size

            # 找出第rank个可用数字，返回的是原下标
            index = seg.kth(rank)
            answer.append(str(index + 1))

            # 选过的数字改成0，后面不会再被选中
            seg.update(index, 0)

        return ''.join(answer)
```

时间复杂度O(n log n)，空间复杂度O(n)。

这题里 `lazy` 一直为0，因为没有使用区间加。主要关注 `kth` 找数字、`update` 删除数字这两个操作就行。

## 4. 第4099题：统计前面有多少个数比当前数字大

[4099. 将锁定数组排序的最少操作次数](https://leetcode.cn/problems/minimum-operations-to-sort-with-locked-indices/)｜第526场周赛Q3

nums是1到n的一个排列。有些位置被锁定，只有两个相邻位置都解锁后，才能交换它们。也可以花一次操作解锁一个位置，但最多解锁k次。求排成升序需要的最少总操作数。

### 先判断哪些位置必须解锁

排序后的下标i应该放数字 `i+1`。

如果某个锁定位置上的数字不等于 `i+1`，那它必须移动，因此这个位置必须解锁。

但数字已经放对，也不代表它一定可以保留锁定。例如：

```text
nums = [1, 4, 3, 2]
              ↑
          下标2锁定
```

3确实已经在正确位置，可4和2还需要跨过它完成交换。相邻交换无法穿过锁定位置，所以这里仍然需要解锁。

因此，锁定位置i能够保留，需要同时满足：

```text
nums[i] == i+1
前缀最大值 <= i+1
```

为什么这两个条件就够了？nums是一个排列，前i+1个数互不相同，且都不超过i+1，那它们恰好就是1到i+1。当前位置已经是i+1，所以它左边都是更小的数，右边都是更大的数，两边不需要跨过它交换。

把不满足条件的锁定位置全部计入 `lock_cnt`。如果超过k，直接返回-1。

### 为什么还能用线段树？

必须解锁的位置处理完后，还需要计算交换次数。

一个前面的大数，要和后面的小数交换顺序，这样的一对就叫逆序对。通过相邻交换排序，最少交换次数等于逆序对数：每次交换相邻的逆序元素，恰好消掉一个逆序对。

保留的锁定位置已经把数字正确分开，两边没有跨过它的逆序对。因此可以分别排序各段，总交换次数仍然是整个数组的逆序对数。

于是答案为：

```text
必须解锁的位置数 + 逆序对数
```

问题落到这里，就变成了：

> 从左往右扫描，每遇到一个数字，查询前面出现过的数字里，有多少个比它大，然后把它记为已出现。

线段树能维护这个“出现过多少个”的计数。

### 叶子按数字值来排，别按原数组位置来排

数字num对应下标 `num-1`，叶子记录这个数字在已扫描前缀中出现了几次。

扫描到原数组下标i时，前面已经有i个数字。查询：

```python
seg.query(0, num-1)
```

得到前面小于等于num的数量。用i减掉它，就是前面大于num的数量。

例如扫描 `[3,1,2]`：

| 当前数字 | 前面已有几个数 | 前面小于等于它的数量 | 新增逆序对 |
| --- | ---: | ---: | ---: |
| 3 | 0 | 0 | 0 |
| 1 | 1 | 0 | 1 |
| 2 | 2 | 1 | 1 |

一共2个逆序对：`(3,1)` 和 `(3,2)`。

每轮都是先查询，再把当前数字计入线段树。

### 套用公共模板

```python
class Solution:
    def minOperations(self, nums: list[int], locked: list[int], k: int) -> int:
        n = len(nums)
        max_num = 0
        lock_cnt = 0

        for i, num in enumerate(nums):
            max_num = max(max_num, num)
            if locked[i]:
                # 自己没放对，或者左边有大数需要跨过自己
                if num != i+1 or max_num > i+1:
                    lock_cnt += 1
                    if lock_cnt > k:
                        return -1

        # 下标num-1记录数字num在已扫描前缀中的出现次数
        seg = SegmentTree([0] * n)
        swap_cnt = 0

        for i, num in enumerate(nums):
            # 前面共有i个数字，减掉其中小于等于num的数量
            swap_cnt += i - seg.query(0, num-1)

            # 当前数字加入已扫描前缀：对应位置加1
            seg.add(num-1, num-1, 1)

        return swap_cnt + lock_cnt
```

时间复杂度O(n log n)，空间复杂度O(n)。

这题和第60题都在维护数量。第60题是“用掉一个，改成0”，这题是“遇到一个，加1”；一个查询第几个，一个查询某段里有几个。

## 5. 第2916题：一批子数组的不同元素数同时加1

[2916. 子数组不同元素数目的平方和 II](https://leetcode.cn/problems/subarrays-distinct-element-sum-of-squares-ii/)

题目要求：对所有非空子数组，统计其中不同元素的数量，再把这些数量的平方加起来。

### 为什么能用线段树？

我们从左到右枚举子数组的右端点r。右端点固定后，剩下的区别就是左端点在哪里。

例如当前扫描到了 `[1,2]` 的末尾，可以考虑：

```text
左端点0：[1,2]，不同元素数为2
左端点1：[2]，  不同元素数为1
```

因此可以让下标i这个叶子，保存**以i为左端点、以当前r为右端点的子数组有多少种不同元素**。

如果新的数字加入后，一整段左端点对应的计数都会加1，就能用线段树的一次区间加来完成。

关键是先找出：到底是哪一段会加1？

### 当前数字上次出现在哪里？

设新数字x在下标r，它上次出现在prev，没有出现过就记为-1。

如果左端点不超过prev，这个子数组本来就包含x，再加入一个x，不同元素数不变。

如果左端点大于prev，这个子数组之前没有x，新加入后，不同元素数增加1。

所以需要加1的左端点范围恰好是：

```text
[prev+1, r]
```

比如从 `[1,2]` 扩展到 `[1,2,1]`，新的1上次出现在下标0：

```text
左端点0：[1,2] → [1,2,1]，不同元素数仍为2
左端点1：[2]   → [2,1]，  不同元素数从1变成2
左端点2：空    → [1]，    不同元素数从0变成1
```

变化的是下标 `[1,2]` 这一段。

右端点还没到达的位置，叶子暂时存0。这样新左端点r的贡献，也能一起包含在这次加1里。

### 树里存计数，平方和怎么求？

原来某个子数组有c种不同元素，现在变成c+1种，平方增加了多少？

```text
(c+1)² - c² = 2c+1
```

假设受影响的一段有length个左端点，它们的旧计数之和为old_sum。那么总平方增量就是：

```text
2 * old_sum + length
```

所以只要先查这一段旧计数的和，就能算出平方和增加多少，不需要把每个叶子的平方都算一遍。

维护两个变量：

- `ending`：以当前r为右端点的所有子数组，不同元素数的平方和。
- `answer`：已经处理过的所有右端点的ending之和。

每一轮做三件事：

```text
先查受影响区间的旧计数和。
用2*旧和+区间长度，更新ending。
给这段计数加1，再把ending加入answer。
```

用 `[1,2,1]` 推演：

| 右端点r | 当前数字 | 更新后的叶子计数 | ending | answer |
| --- | --- | --- | ---: | ---: |
| 0 | 1 | `[1,0,0]` | 1 | 1 |
| 1 | 2 | `[2,1,0]` | 5 | 6 |
| 2 | 1 | `[2,2,1]` | 9 | 15 |

最后一轮，受影响区间是 `[1,2]`，旧计数为 `[1,0]`，旧和为1、长度为2，平方增量为 `2*1+2=4`。因此ending从5变成9。

**一定要先查询旧和，再给区间加1。** 顺序反过来，公式里代入的就不再是旧计数了。

### 套用公共模板

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

            # 先查旧计数之和，计算平方和增加多少
            old_sum = seg.query(left, r)
            ending += 2 * old_sum + (r-left+1)

            # 这些左端点对应的不同元素数，都增加1
            seg.add(left, r, 1)

            # 每个子数组只在它的右端点这一轮被加入总答案
            answer = (answer + ending) % mod
            last[x] = r

        return answer
```

时间复杂度O(n log n)，空间复杂度O(n)。

这一次用到区间加，`lazy` 就真正起作用了：某一整块计数都加1时，先更新这一块的总和、记下标记，等需要进入孩子时再下传。

## 6. 第4086题：找所有能接上的区间中，谁到得最远

[4086. 覆盖目标区间的最少区间](https://leetcode.cn/problems/minimum-interval-selection-to-cover-target-intervals/)｜第524场周赛Q4

题目有两组闭区间：availableIntervals表示可以选择的区间，targetIntervals表示必须覆盖的范围。选尽量少的可选区间，覆盖目标里的每一个实数点，做不到返回-1。

### 先想每次该选谁

假设当前需要从位置x继续覆盖。

下一条区间必须能接上，也就是左端点不超过x。在这些区间里，我们选右端点最远的那一条。

为什么？假设某个最优方案这一步选得短一些，把它换成到得更远的区间，当前需要覆盖的位置仍然能覆盖到，后面能走到的位置也不会更差，使用数量没有增加。

因此每次都可以这样选，再继续处理后面的需求。

### 为什么能用线段树？

每次真正需要回答的问题是：

> 所有左端点不超过x的可选区间中，最大的右端点是多少？

先把可选区间按左端点排序，满足条件的区间就集中在最前面的一段。

如果叶子存对应区间的右端点，节点维护最大值，查询这一段，就能得到下一步最远能走到哪里。

这次树里保存的既不是可用数量，也不是不同元素数，而是**右端点的最大值**。

例如：

```text
可选区间：[1,4] [1,7] [3,9] [5,10] [10,15]
左端点：    1     1     3      5       10
叶子值：    4     7     9     10       15
```

当前x=1，查询前两个位置，得到7。当前x=7，查询前四个位置，得到10。

代码里用 `bisect_right(starts, x)-1` 找到最后一个左端点不超过x的位置index，然后查：

```python
seg.query(0, index)
```

它查询的是排好序后的候选区间下标，原坐标有多大、是否连续，都不影响这个索引方式。

### 目标先合并，已经覆盖到的地方要接着用

目标区间先按左端点排序，再合并重叠或端点相接的区间。例如：

```text
[1,3]、[2,5]、[7,8]、[10,13]、[11,15]
                     ↓
             [1,5]、[7,8]、[10,15]
```

维护 `covered_end`，表示之前选中的区间最远覆盖到哪里。它要放在外层循环之外，换目标时也保留。

比如目标是 `[1,2]`、`[8,9]`，可选区间是 `[1,10]`，选一次就都覆盖了。

目标之间的空白不用专门覆盖。开始处理下一段时，从 `max(start, covered_end)` 继续。

### 两个边界，别顺手改掉

题目覆盖的是实数点，`[1,2]` 和 `[3,4]` 中间有空隙，不能接成连续的 `[1,4]`。因此接到x之后，下一条还是从x接，不能把位置改成x+1。

失败判断用：

```python
if next_end < cur_start or next_end == covered_end:
    return -1
```

前者表示连当前需要接的位置都到不了；后者表示已经无法继续延伸。

不要把条件改成 `next_end <= cur_start`。目标和候选都只有 `[5,5]` 时，覆盖这个单点是合法的，答案为1。

### 套用公共模板

```python
from bisect import bisect_right


class Solution:
    def minSelection(self, availableIntervals: list[list[int]],
                     targetIntervals: list[list[int]]) -> int:
        # 合并目标；新建内层列表，不修改传入的目标区间
        sorted_target = sorted(targetIntervals, key=lambda x: x[0])
        merged_target = []
        for start, end in sorted_target:
            if merged_target and start <= merged_target[-1][1]:
                merged_target[-1][1] = max(merged_target[-1][1], end)
            else:
                merged_target.append([start, end])

        # 按左端点排序，叶子存对应候选区间的右端点
        sorted_available = sorted(availableIntervals, key=lambda x: x[0])
        starts = [start for start, end in sorted_available]
        seg = SegmentTree([end for start, end in sorted_available], mode="max")

        ans = 0
        covered_end = float('-inf')

        for start, end in merged_target:
            # 目标之间可以跳空；之前覆盖过来的部分继续使用
            cur_start = max(start, covered_end)

            while covered_end < end:
                # 找到所有左端点不超过cur_start的候选
                index = bisect_right(starts, cur_start) - 1

                # 查询这些候选中，最远能到达的右端点
                # 没有候选时index=-1，空区间查询返回负无穷
                next_end = seg.query(0, index)

                if next_end < cur_start or next_end == covered_end:
                    return -1

                ans += 1
                covered_end = next_end
                cur_start = covered_end

        return ans
```

这题不需要修改线段树：所有候选都提前放好，每次查询能接上的那一段的最大右端点即可。

也不必删除选过的候选。选完后covered_end只会增大，旧候选的右端点不会超过已经到达的位置，无法让下一步获得额外进展。

设可选区间数为a，目标区间数为t。每次成功选择都会到达一个严格更大的候选右端点，所以最多成功选择a次。加上排序，总时间复杂度为O(a log a + t log t)，空间复杂度为O(a+t)。

## 7. 把四题放在一起看

| 题目 | 一个叶子代表什么 | 每块维护什么 | 核心调用 |
| --- | --- | --- | --- |
| 60 排列序列 | 一个数字是否可用 | 可用数量之和 | `kth(rank)`、`update(index, 0)` |
| 4099 锁定数组排序 | 一个数字在已扫描前缀中出现几次 | 出现次数之和 | `query(0, num-1)`、单点加1 |
| 2916 不同元素数平方和 | 当前右端点下，一个左端点对应的不同元素数 | 计数之和 | 区间查旧和、区间加1 |
| 4086 覆盖目标区间 | 一个候选区间的右端点 | 最大右端点 | `mode="max"`、前缀查询 |

我觉得这几题最值得放在一起的地方，是同一个叶子下标，在不同题里含义完全不同。

第60题和第4099题按数字值索引，第2916题按子数组左端点索引，第4086题按排序后的候选区间索引。先想清楚这一层，才能知道传给 `query` 的两个数字到底代表什么。

最后把几个容易混的地方放在这里：

1. `add(i, i, 1)` 是原值加1，`update(i, 0)` 是直接改成0。
2. 第60题的排列编号从0开始，`kth` 的排名从1开始，返回的下标又从0开始。
3. 第2916题要先查询旧和，再区间加1。
4. `kth` 需要非负整数计数，树里的计数保持准确，不取模。
5. sum模式合并时相加，max模式合并时取最大值；整段加value时，前者增加长度乘value，后者增加value。
6. 第4086题覆盖实数点，保留全局覆盖末端，也要考虑单点区间。

再遇到一道题时，可以先试着填这句话：

> 我需要维护____，每次会修改____，并查询____。

比如第60题填出来就是：“我需要维护剩余数字，每次选走一个，并查询剩下的第几个。”

这句话说清楚了，再去看 `p*2` 和 `p*2+1`，它们就只是帮我们往左右两半走的编号。

大家学线段树时，最容易卡住的是“叶子到底存什么”，还是“lazy什么时候下推”？欢迎拿具体例子一起推。

#线段树 #LeetCode #Python #算法模板 #刷题复盘
