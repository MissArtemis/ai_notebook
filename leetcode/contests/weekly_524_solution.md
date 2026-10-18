# 分享丨力扣524周赛：异或负责吓人，颜色负责认爹，区间负责让我加班

这场第 524 场周赛，四道题的工作安排很明确：第一题数重复，第二题认路，第三题认爹，第四题看看我还能不能正常下班。🙂

第一题把“相邻元素不能相等”包装成了“按位异或非零”，第二题让我跟着箭头走，第三题给树上了颜色，第四题则给了两堆区间，问怎么花最少的次数把目标盖住。

看完这一场，感觉自己从数组保洁，干到了网格导航，再转岗树木户籍管理，最后去工地铺地毯。

先把路线放前面：**第一题统计相邻相等的次数；第二题模拟并记录访问位置；第三题按颜色确定边的方向，再检查父子数量；第四题合并目标区间，用“当前能接上的区间里，选伸得最远的”做贪心。**

下面按 `weekly_524.ipynb` 中的四份实现展开，保留原代码。第四题代码额外补上本地运行需要的 `List` 导入。

## 第一题：使相邻元素按位异或非零的最少删除次数

[4083. 题目链接](https://leetcode.cn/problems/minimum-deletions-to-make-array-sharp/)

题目要求删除一些元素，让剩下的每一对相邻元素异或都不为零。

看到“按位异或”，脑子已经开始翻位运算模板了。冷静一下，这里只需要一个性质：

```text
a XOR b == 0，当且仅当 a == b。
```

翻译成人话：相邻的数别一样就行。

位运算刚进会议室，发现自己只是来帮忙改了个需求文案。

比如：

```text
原数组：[1, 1, 2, 2, 2, 3]
分成段：[1, 1] [2, 2, 2] [3]
保留后：[1]    [2]       [3]
删除数：  1  +    2    +   0  = 3
```

一段连续相等的数，长度为 `k`，最多只能留下一个，至少要删 `k - 1` 个。每段留一个以后，相邻两段的值本来就不同，正好构造出合法答案。

而长度为 `k` 的一段里，恰好有 `k - 1` 对相邻相等的元素。所以代码直接数这些相等对，连分段数组都不用真的建。

```python
# Q1 4083
class Solution:
    def minDeletions(self, nums: list[int]) -> int:
        ans = 0
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1]:
                ans += 1

        return ans
```

注意这里数的是**连续重复**，不能给整个数组去重。比如 `[4, 4, 9, 4]` 只要删一个，留下 `[4, 9, 4]` 完全合法。

前后两个 `4` 中间隔着 `9`，人家没有挨着坐，不能因为重名就一起开除。

时间复杂度 `O(n)`，额外空间 `O(1)`。

## 第二题：有向网格中的最后访问单元格

[4084. 题目链接](https://leetcode.cn/problems/last-visited-cell-in-a-directional-grid/)

这题的网格里全是方向：`L、R、U、D`。从左上角出发，走到哪里就听哪里的指挥。

遇到网格题，我的手差点自己把 BFS 队列写出来。再看一眼，每个格子只有一个指定方向，根本没有岔路给我选。

导航都把路线定死了，我还准备开个会讨论最短路。

所以按题意模拟就够了：先把起点标成访问过，每次算出下一站；下一站越界或者已经访问过，就停在当前格子；否则更新位置，继续走。

这里最值得圈出来的是：**出问题的那一步不执行。**

比如：

```text
R D
U L

(0,0) → (0,1) → (1,1) → (1,0)
                               ↓ 想回到 (0,0)，但那里已经去过
                            停在 (1,0)
```

答案是 `[1, 0]`。不能先走回起点，再说“哎呀走重复了”。门禁刷不过，人还在门外。

```python
#Q2 4084
class Solution:
    def lastVisitedCell(self, grid: list[list[str]]) -> list[int]:
        record = {
            "L": (0, -1),
            "R": (0, 1),
            "U": (-1, 0),
            "D": (1, 0)
        }
        visited = set()
        m, n = len(grid), len(grid[0])
        visited.add((0, 0))
        i, j = 0, 0
        while 0 <= i < m and 0 <= j < n:
            di, dj = record[grid[i][j]]
            ni, nj = i + di, j + dj
            if not (0 <= ni < m and 0 <= nj < n) or (ni, nj) in visited:
                break
            visited.add((ni, nj))
            i, j = ni, nj

        return [i, j]
```

`visited` 里一开始就放 `(0, 0)`，也是同一个道理：起点已经访问过，不能等第二次回来才给它登记。

访问集合不用回退。这道题没有换条路再试的过程，走过的地方永远算走过。

每个格子最多进入一次，时间复杂度 `O(mn)`，额外空间 `O(mn)`。

## 第三题：找到颜色树的根

[4085. 题目链接](https://leetcode.cn/problems/find-root-of-a-colored-tree/)

这题给一棵无向树，让我们选一个根，使它同时满足：每个节点最多有两个孩子；同一层颜色相同，层与层之间按下面的顺序循环：

```text
R → B → W → R → B → W → ...
```

根可以从三种颜色里的任意一种开始，但后面的顺序固定。

表面上看，要找根，好像可以每个节点都当一次根，跑一遍遍历验货。`n` 最大十万，这样最坏要 `O(n²)`。

每个节点都参加一次根节点竞聘，面试官先退休了。

主笔记里的做法抓住了另一个信息：**颜色已经替每条边定好了父子关系。**

对一条连接 `R` 和 `B` 的边，方向只能是 `R → B`；连接 `B` 和 `W`，只能是 `B → W`；连接 `W` 和 `R`，只能是 `W → R`。

不是看节点编号，也不是看 `edges` 里谁写在前面。颜色一亮，辈分就定了。

如果两端颜色相同，这条边怎么定向都不可能满足下一层换色，直接返回 `-1`。

代码用 `parent_record` 记录谁的父亲是谁，用 `children_record` 记录每个人有几个孩子。定向的过程中，如果某个节点已经有父亲，又冒出第二个，就不合法；所有边处理完，再检查有没有超过两个孩子的节点。

最后，没有父亲的那个节点就是根。

```python
#Q3 4085

from collections import defaultdict


class Solution:
    def findColoredRoot(self, edges: list[list[int]], colors: str) -> int:
        color_mapping = {
            "R": "B",
            "B": "W",
            "W": "R"
        }
        color_indexing = {i: colors[i] for i in range(len(colors))}
        children_record = defaultdict(lambda: [])
        parent_record = defaultdict(lambda: None)
        n = len(edges)
        for i in range(n):
            u, v = edges[i][0], edges[i][1]
            if color_mapping[color_indexing[u]] == color_indexing[v]:
                children_record[u].append(v)
                if parent_record[v] is not None:
                    return -1
                parent_record[v] = u
            elif color_mapping[color_indexing[v]] == color_indexing[u]:
                children_record[v].append(u)
                if parent_record[u] is not None:
                    return -1
                parent_record[u] = v
            else:
                return -1
        for key in children_record:
            if len(children_record[key]) > 2:
                return -1
        for i in range(len(colors)):
            if parent_record[i] is None:
                return i
        return -1
```

这里还得解释一下：为什么没有再从根出发 DFS，检查整棵树？

题目已经保证输入是一棵树，也就是连通、无环，而且有 `n - 1` 条边。把每条边定向以后，所有节点的入度之和就是 `n - 1`。

前面的检查保证每个节点入度最多为 `1`。因此恰好有一个节点入度为 `0`，其余节点入度都是 `1`。沿父亲关系往上走，又不可能成环，最终只能回到这个唯一的根。

每条父子边都按同一套颜色规则前进，所以从根走同样多步，得到的颜色自然相同。这样，“每层颜色一致”也就跟着成立了。

树的基本性质已经把证明补上了，遍历可以少加一次班。

题目还保证无向树里每个节点的度最多为 `3`，但这不代表自动满足二叉树性质：根没有父亲，度为 `3` 就意味着它有三个孩子。代码里的孩子数量检查仍然有必要。

比如一个 `R` 节点连着三个 `B` 节点，颜色没意见，二叉树有意见。

时间复杂度 `O(n)`，额外空间 `O(n)`。原代码中的 `n = len(edges)` 统计的是边数，循环负责逐条处理边；节点数量仍然用 `len(colors)`。

## 第四题：覆盖目标区间的最少区间

[4086. 题目链接](https://leetcode.cn/problems/minimum-interval-selection-to-cover-target-intervals/)

前三题分别在数人、走路、认爹，第四题开始铺地毯。

给两组闭区间：`availableIntervals` 是能选的地毯，`targetIntervals` 是必须盖住的地方。选尽量少的地毯，把目标里的**每一个实数点**都覆盖到；做不到就返回 `-1`。

题目对地毯长度挺宽容，可以重叠，也可以多盖，但对漏缝零容忍。

### 先合并目标，弄清楚到底要盖哪里

主笔记先按左端点排序，再合并重叠或端点相接的目标区间。

比如题目中的目标：

```text
[1,3], [2,5], [7,8], [10,13], [11,15], [12,13]

合并后：
[1,5], [7,8], [10,15]
```

需求单总算整理好了。`5` 到 `7` 之间、`8` 到 `10` 之间的空白不用专门覆盖。

注意闭区间 `[1,2]` 和 `[2,4]` 可以接起来；`[1,2]` 和 `[3,4]` 中间却有缺口，不能因为整数 `2` 后面是 `3` 就觉得接上了。

`2.5`：我也是实数，我也在目标里，你们开会能不能带上我？

### 每次补覆盖，都选当前能接上的、右端点最远的

接着把可选区间也按左端点排序。代码里几个变量可以这样看：

- `cur_end`：上一次选中的区间到哪里结束。
- `cur_start`：这一轮要从哪个位置继续接。
- `i`：可选区间扫描到了哪里。
- `max_end`：这一轮所有能接上的候选，最远能到哪里。

处理某个目标 `[target_start, target_end]` 时，先设置：

```python
cur_start = max(cur_end, target_start)
```

上一个区间已经盖过来的部分可以接着用；如果两个目标之间有空白，就直接跳到新目标的左端点，不需要给空白额外买地毯。

只要 `cur_end` 还没达到当前目标的右端点，就扫描所有满足 `左端点 <= cur_start` 的候选，从中取最大的右端点。能推进就选一次、计数加一，再从新的末端继续接。

代码里只记最远的右端点，没有记录具体选了哪一条，因为题目只问数量。

```python
from typing import List

#Q4 4086
class Solution:
    def minSelection(self, availableIntervals: List[List[int]], targetIntervals: List[List[int]]) -> int:
        sorted_target = sorted(targetIntervals,key=lambda x:x[0])
        merged_interval = []
        for i in range(len(sorted_target)):
            if not merged_interval:
                merged_interval.append(sorted_target[i])
            else:

                prev_end = merged_interval[-1][-1]
                cur_start = sorted_target[i][0]
                cur_end = sorted_target[i][1]
                if cur_start<=prev_end:
                    if cur_end>prev_end:
                        merged_interval[-1][-1] = cur_end
                    else:
                        continue
                else:
                    merged_interval.append(sorted_target[i])
        print(merged_interval)
        ans = 0
        sorted_aval = sorted(availableIntervals, key=lambda x:x[0])
        cur_end = float('-inf')
        i = 0

        for target_start,target_end in merged_interval:
            cur_start = max(cur_end,target_start)

            while cur_end < target_end:
                max_end = cur_end
                while i < len(sorted_aval):
                    if sorted_aval[i][0] <= cur_start:
                        max_end = max(max_end,sorted_aval[i][1])
                        i+=1
                    else:
                        break

                if max_end < cur_start or max_end == cur_end:
                    return -1

                ans+=1
                cur_end = max_end
                cur_start = cur_end

        return ans
```

### 为什么这个贪心靠谱？一次选择，尽量多铺一点

在当前需要接上的位置，任何合法方案都得找一条能覆盖这里的区间。

如果某个最优方案选了较短的那条，把它换成代码挑出的、右端点最远的那条，当前要覆盖的部分仍然覆盖到了，后面能走到的位置还不会更差，选取数量也没增加。

所以总能把一个最优方案的这一步换成我们的选择，之后再对剩余部分重复这个过程。

地毯都按一条计费了，同样花一次，当然尽量铺远一点。

可选区间只扫描一次也没关系：本轮看过但没选的区间，右端点都不会超过本轮的 `max_end`。等走到那个最远端点，它们也帮不了我们继续往前，因此不用回头翻旧候选。

### 两个全局变量别在换目标时清零

`cur_end` 和 `i` 都在外层目标循环之外初始化，这一点很关键。

比如目标是 `[1,2]`、`[8,9]`，可选区间只有 `[1,10]`。选一次，两个目标都盖好了。

如果每换一个目标就重新统计，第一块地毯还没收起来，账单已经又收了一遍。

同样，遇到不需要覆盖的空白时可以跳过去。例如可选区间 `[1,2]`、`[8,9]` 正好分别覆盖上述两个目标，答案就是 `2`，中间不用补区间。

### 失败条件和单点区间，也得看一眼

原代码的失败判断是：

```python
if max_end < cur_start or max_end == cur_end:
    return -1
```

前者表示连这次要接的位置都盖不到，后者表示这一轮已经无法把右端点往前推进。

别随手把它改成 `max_end <= cur_start`：题目允许单点闭区间 `[x,x]`。比如目标和可选区间都只有 `[5,5]`，这一点确实能盖住，答案是 `1`。刚跳到新目标时，最远只能到它的起点，也可能已经完成了这个单点目标。

对有长度的目标，如果只能盖到起点、后面接不上，下一轮的“无法推进”会正确返回 `-1`。

时间复杂度是 `O(a log a + t log t)`，其中 `a`、`t` 分别是可选区间数和目标区间数。排序以后，目标和候选都只线性扫描，额外空间是 `O(a + t)`。

原实现里还有两个值得在复盘时记下的小细节：`print(merged_interval)` 是调试输出，提交时可以去掉；`sorted()` 只新建了外层列表，合并时直接修改内层区间，也会修改传入的 `targetIntervals`。算法结果不受影响，但在本地复用输入时，要先做一份深拷贝。

调试日志还在认真报幕，原数组已经被顺手装修了。下次复盘，记得同时看看结果和现场。

## 这场带走的经验

第一题提醒我，遇到位运算，先把条件翻译一下，有时最后只剩一个 `==`。

第二题提醒我，网格不一定要搜索。只有一条路，就先把这条路走明白，尤其分清楚“准备走”和“真的走了”。

第三题最有意思：题目让我找根，颜色却已经把父子关系写好了。把边的方向确定下来，根自己就露出来了。

第四题则把“合并区间”和“贪心覆盖”接到了一起：先整理需求，再一段一段往前铺，目标之间允许跳空，已经买过的覆盖记得接着用。

这一场写完，算法工具箱没多掏几件，阅读理解和边界条件倒是轮流检查了我的精神状态。😂

大家这场在哪题停得最久？是第三题突然发现颜色能认爹，还是第四题被区间缝里的 `2.5` 拦住了？

#力扣 #LeetCode #周赛524 #算法复盘 #Python #刷题日常
