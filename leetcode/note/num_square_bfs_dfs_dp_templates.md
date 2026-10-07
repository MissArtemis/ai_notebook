# 从num-square拆解BFS，DFS和DP

同一道题能用 BFS、DFS 和 DP，为什么看完三个答案，换一道题还是不会写？

我想借 `numSquares` 把它们放在一起拆开看：**状态怎么定义，下一步怎么走，什么时候结束，重复计算怎么省。**

读完这篇，希望你能留下三份模板，以及一条把它们串起来的思路：

> BFS 按步数找答案，DFS 向子问题问答案，DP 保存并复用子问题的答案。

代码使用 Python。先从一个熟悉的例子开始。

## 1. 三种写法，共用一个状态

[279. 完全平方数](https://leetcode.cn/problems/perfect-squares/description/)要求：把 `n` 拆成若干个完全平方数的和，求最少需要几个。平方数可以重复使用。

比如：

```text
13 = 9 + 4      → 2 个
12 = 4 + 4 + 4  → 3 个
```

换个角度：**每次从当前数字里减去一个正的完全平方数，最少减几次，才能到 0？**

先把三个问题写清楚：

| 问题 | 本题怎么填 |
| --- | --- |
| 状态是什么？ | `cur`：还剩多少没有凑出来 |
| 下一步怎么走？ | 选择 `r * r <= cur`，进入 `cur - r * r` |
| 什么时候结束？ | `cur == 0`，已经凑完 |

例如：

```text
13 --减 9--> 4 --减 4--> 0
```

这是一条走了两步的路线。也可以把每个剩余数值看成一个节点，“减去一个平方数”看成一条边，每条边的代价都是 `1`。

为什么只记录 `cur` 就够了？因为还剩同样的数，后面能选哪些平方数、最少还要几个，都相同。至于之前怎么走到这里，不影响这个子问题的答案。

**先找状态，再选写法。** 下面三种方法，都围绕同一条转移：

```text
cur → cur - r * r
```

## 2. BFS 模板：所有路线一起走一步

### 先理解“层”

BFS 使用队列，先放进去的状态先处理。

```text
第 0 层：还没减，剩余 13
第 1 层：减过一次，可能剩余 4、9、12
第 2 层：再减一次，从 4 可以到 0
```

第一次遇到 `0` 时，走过的层数就是答案。因为所有一步能到的状态先处理完，才会处理两步能到的状态。

**这个结论的前提是每一步的代价相同。** 本题每次都用掉一个平方数，所以成立。

### 可迁移的 BFS 模板

下面的 `is_goal` 和 `next_states` 是需要按题目填写的辅助函数；`next_states` 只生成合法的下一状态。

```python
from collections import deque


def bfs(start):
    queue = deque([start])
    visited = {start}
    steps = 0

    while queue:
        size = len(queue)  # 固定当前层的数量

        for _ in range(size):
            state = queue.popleft()
            if is_goal(state):
                return steps

            for nxt in next_states(state):
                if nxt in visited:
                    continue

                visited.add(nxt)  # 入队时标记
                queue.append(nxt)

        steps += 1

    return -1  # 队列耗尽，仍未到达目标
```

记住四件事：**起点入队 → 固定层大小 → 扩展并去重 → 层数加一。**

### 把模板填成本题

```python
from collections import deque
from math import isqrt


class Solution:
    def numSquares(self, n: int) -> int:
        queue = deque([n])
        visited = {n}
        steps = 0

        while queue:
            size = len(queue)

            for _ in range(size):
                cur = queue.popleft()
                if cur == 0:
                    return steps

                for r in range(isqrt(cur), 0, -1):
                    nxt = cur - r * r
                    if nxt in visited:
                        continue

                    visited.add(nxt)
                    queue.append(nxt)

            steps += 1

        return -1
```

`isqrt(cur)` 返回平方根的整数部分。例如 `isqrt(13) == 3`，所以能减的平方数是 `9、4、1`。

两个容易漏掉的细节：

- **用 `deque.popleft()` 出队。** `list.pop(0)` 会移动后面的元素，队列大时多出很多开销。
- **入队时就去重。** 同一个剩余数值第一次入队时，用的步数已经最少；再绕一条更长的路线到它，不会让答案更好。

这里的 `visited` 保存的是“已经到过哪些状态”，层数单独由外层循环维护。

## 3. DFS 模板：先把一个子问题问到底

### 先写一句话，定义返回值

写递归之前，先写：

```text
dfs(cur) = 凑出 cur，最少还需要几个完全平方数。
```

注意“还需要”三个字。函数返回的是**当前子问题的答案**，所以每选一个平方数，要给子问题的结果加 `1`。

对于 `13`：

```text
dfs(13) = min(
    dfs(4) + 1,   # 先选 9
    dfs(9) + 1,   # 先选 4
    dfs(12) + 1   # 先选 1
)
```

剩余为 `0` 时，不需要再选任何数：`dfs(0) = 0`。

### 求最少步数的 DFS 模板

`next_states` 同样只生成合法状态。这个模板要求递归能够结束；本题每次减去正数，剩余值会不断变小。

```python
def dfs(state):
    if is_goal(state):
        return 0

    best = float("inf")
    for nxt in next_states(state):
        best = min(best, dfs(nxt) + 1)

    return best
```

记住：**定义返回值 → 写结束条件 → 枚举选择 → 递归 → 合并结果。**

这里求最小值，用 `min` 合并；换成求方案数，通常用加法；求最大值则要改成 `max`，并重新考虑初始值和无解值。

### 把模板填成本题

```python
from math import isqrt


class Solution:
    def numSquares(self, n: int) -> int:
        def dfs(cur):
            if cur == 0:
                return 0

            best = float("inf")
            for r in range(isqrt(cur), 0, -1):
                best = min(best, dfs(cur - r * r) + 1)

            return best

        return dfs(n)
```

这份朴素 DFS 用来理解递归、小数据验证。它会反复计算相同的子问题，大数据下开销很大。

本题只传整数参数，没有修改共享的路径列表，因此不需要额外“撤销选择”。如果题目要收集具体路径，才常会看到 `path.append()`、递归、`path.pop()` 这一组回溯操作。

## 4. 给 DFS 加缓存，就走到了 DP

### 重复计算发生在哪里？

```text
13 → 9 → 8   # 先减 4，再减 1
13 → 12 → 8  # 先减 1，再减 4
```

两条路线都会问 `dfs(8)`：还剩 `8`，最少需要几个平方数？

第一次算完保存结果，第二次直接取，这就是**记忆化搜索**。

在上一段代码中，给 `dfs` 加上缓存即可：

```python
from functools import lru_cache
from math import isqrt


class Solution:
    def numSquares(self, n: int) -> int:
        @lru_cache(maxsize=None)
        def dfs(cur):
            if cur == 0:
                return 0

            best = float("inf")
            for r in range(isqrt(cur), 0, -1):
                best = min(best, dfs(cur - r * r) + 1)

            return best

        return dfs(n)
```

`lru_cache` 会记录“参数 → 返回值”。这里就是 `cur → 最少个数`。把函数定义在 `numSquares` 内部，不同输入会拥有各自的缓存。

手写缓存也做同一件事：进入函数时先检查 `memo[cur]`，有结果就直接返回；没有就计算，最后保存再返回。

**无论用 `lru_cache`，还是用 `record` 字典手动存结果，本质上都是记忆化 DFS，也都是自顶向下的 DP。**

它们的区别在于缓存怎么写。真正改变计算顺序的是下一节：把递归改成从小到大填表。

递归版本仍会占用调用栈，缓存不会消除递归深度问题。本题输入可到 `10^4`，递归版适合展示思路；大输入可以使用下面的迭代 DP。

## 5. DP 模板：先算小问题，再填大问题

### 把递归函数，翻译成数组

刚才的定义是：

```text
dfs(cur) = 凑出 cur 的最少个数
```

现在写成：

```text
dp[i] = 凑出 i 的最少个数
```

含义相同，只是递归按需要去问，数组按顺序提前算。

把 DFS 里的这句：

```python
best = min(best, dfs(cur - r * r) + 1)
```

翻译成：

```python
dp[i] = min(dp[i], dp[i - r * r] + 1)
```

`+1` 仍然表示这次新选了一个平方数。

### 写 DP 前，先填这五项

| 步骤 | 本题怎么填 |
| --- | --- |
| 定义状态 | `dp[i]` 表示凑出 `i` 的最少个数 |
| 初始化 | `dp[0] = 0`；其余先设为无穷大 |
| 写转移 | 枚举 `r * r <= i`，用 `dp[i - r * r] + 1` 更新 |
| 定顺序 | `i` 从小到大，因为依赖的下标比 `i` 小 |
| 取答案 | 返回 `dp[n]` |

“先定义、再初始化、写转移、定顺序、取答案”，比只背两层 `for` 循环更容易迁移到新题。

### 求最少步数的填表模板

下面是本题这类一维 DP 的结构；`previous_states(i)` 表示能转移到 `i` 的前置状态。计算 `i` 时，依赖项必须已经算好。

```python
dp = [float("inf")] * (target + 1)
dp[0] = 0

for i in range(1, target + 1):
    for prev in previous_states(i):
        dp[i] = min(dp[i], dp[prev] + 1)

answer = dp[target]
```

### 把模板填成本题

```python
from math import isqrt


class Solution:
    def numSquares(self, n: int) -> int:
        dp = [float("inf")] * (n + 1)
        dp[0] = 0

        for i in range(1, n + 1):
            for r in range(1, isqrt(i) + 1):
                dp[i] = min(dp[i], dp[i - r * r] + 1)

        return dp[n]
```

以 `13` 为例，要比较的是：

```text
选 1：dp[12] + 1 = 3 + 1 = 4
选 4：dp[9]  + 1 = 1 + 1 = 2
选 9：dp[4]  + 1 = 1 + 1 = 2

dp[13] = 2
```

这里枚举的平方数可以反复使用：`dp[i - r * r]` 的组成中允许已经有 `r * r`。因此，`12` 可以得到 `4 + 4 + 4`。

## 6. 放在一起看，三种模板怎么记？

| 写法 | 思考方式 | 保存什么 | 时间上界 | 额外空间上界 |
| --- | --- | --- | --- | --- |
| BFS | 减一次能到哪？再减一次呢？ | 队列、已访问状态 | `O(n√n)` | `O(n)` |
| 朴素 DFS | 选完这个数，剩下的最少要几个？ | 当前递归调用链 | 可能指数增长 | `O(n)` |
| 记忆化 DFS | 同一个剩余值的答案只算一次 | 子问题答案、调用栈 | `O(n√n)` | `O(n)` |
| 迭代 DP | 先算小剩余值，再组合出大值 | 每个数的最少个数 | `O(n√n)` | `O(n)` |

BFS 和记忆化 DFS 最多处理 `0` 到 `n` 这些状态，每个状态最多尝试 `√n` 个平方数；迭代 DP 也是这个上界。朴素 DFS 则会沿不同路线反复展开相同状态。

有一组区别很有用：

- **`visited`：这个状态是否已经到过？** BFS 第一次到达时步数已最少，可以跳过重复访问。
- **`memo` / `dp`：这个状态的答案是多少？** DFS 的不同调用需要取回具体结果，才能继续做 `min`。

所以，DFS 求最优结果时，不能直接照搬 BFS 的“访问过就跳过”。需要复用的是答案。

## 7. 套模板前，检查这四个坑

**① 减掉 `0`，状态永远不变。**

平方数从 `1 * 1` 开始。否则 DFS 可能一直调用自己，DP 也会出现无意义的自我依赖。

**② 从大到小枚举，不代表可以贪心。**

例如 `12`：每次选最大的平方数，会得到 `9 + 1 + 1 + 1`，共四个；但 `4 + 4 + 4` 只要三个。DFS 从大到小试，只是改变尝试顺序，仍然要比较所有选择。

**③ `+1` 加错了地方。**

本文的 `dfs(cur)` 返回“还需要几个”，所以选择一次后加 `1`。如果换了返回值定义，也要跟着检查合并逻辑。

**④ DP 顺序只背升序，却没看依赖。**

本题从小到大，是因为 `i - r * r < i`。换成别的题，顺序要重新根据依赖判断。

## 8. 换一道题，先把这四句话补完整

```text
我的状态是 ______。
从这个状态，合法的下一步是 ______。
当 ______ 时，搜索结束。
函数返回值 / dp 格子的含义是 ______。
```

再问自己：每步代价相同、目标是最少步数吗？可以考虑 BFS。能把问题拆成更小的子问题吗？先试着定义 DFS 的返回值。相同子问题会反复出现吗？加缓存。依赖顺序能确定吗？再把递归翻译成填表 DP。

可以拿[零钱兑换](https://leetcode.cn/problems/coin-change/)练一遍：把“能减的平方数”替换成“能用的硬币面额”，看看状态和转移怎么改，再想想“无法凑出”的情况该怎么表示。

**学完这题，试着合上代码：先写状态定义，再分别写出队列、递归和数组的版本。** 能自己把这三份模板还原出来，下次遇到类似问题就更容易动笔。

如果这篇帮你把 BFS、DFS 和 DP 连起来了，欢迎点赞、收藏，也欢迎关注，一起把刷题模板整理得更清楚。

配套代码：[原始 Notebook 与算法笔记](https://github.com/MissArtemis/ai_notebook/tree/main/leetcode/note)。
