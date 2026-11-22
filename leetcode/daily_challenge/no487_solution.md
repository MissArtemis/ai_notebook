# 487. 最大连续 1 的个数 II｜滚动 DP：我把不存在的 0 也翻了

## 推荐解法：两个变量的滚动 DP（Solution 3）

从左到右扫一遍。`dp0` 记录不翻转时，以当前位置结尾的最长连续 `1`。`dp1` 记录最多翻转一个 `0` 时，以当前位置结尾的最长连续 `1`。每步更新全局最大值，时间 `O(n)`，额外空间 `O(1)`。

```python
#Solution 3 space-optimized dynamic programming
class Solution:
    def findMaxConsecutiveOnes(self, nums: list[int]) -> int:
        dp0 = dp1 = 0
        ans = 0
        for num in nums:
            if num == 1:
                dp0 +=1
                dp1 +=1
            else:
                dp1 = dp0+1
                dp0 = 0
            ans = max(ans,dp0,dp1)
        return ans
```

### 末尾遇到 0，翻转名额就花在这里

| 当前数字 | 更新后的 `dp0` | 更新后的 `dp1` |
| --- | --- | --- |
| `1` | 旧 `dp0 + 1` | 旧 `dp1 + 1` |
| `0` | `0` | 旧 `dp0 + 1` |

遇到 `1`，两种状态都可以把它接到尾巴上。遇到 `0`，不翻的话，连续 `1` 就在这里断了。想让它成为连续段的最后一个 `1`，就得翻当前这个 `0`，左边只能接一段原本就是 `1` 的后缀。

举个例子，扫完 `[1, 0, 1]` 后，`dp0 = 1`，`dp1 = 3`。再读到一个 `0`，如果写成 `dp1 += 1`，就会把 `[1, 0, 1, 0]` 算成长度 `4`。题目发了一张翻转券，我顺手报销了两次。正确的新 `dp1` 是旧 `dp0 + 1 = 2`，所以要先算 `dp1`，再把 `dp0` 清零。

每段连续区间都有一个右端点，所以每个位置只负责计算**以自己结尾**的最佳长度。把这些结果取最大值，就覆盖了所有候选区间。`dp1` 允许零次翻转，始终大于等于 `dp0`，原代码同时比较两者也能得到正确结果。

进阶里的无限流也可以用这套更新。每读到一个数就更新 `dp0`、`dp1` 和 `ans`，随时可以报告目前读到的部分的答案。

## 踩坑一：数组里全是 1，我还是翻了一个 0（Solution 1）

我的第一版从最近的 `0` 往两边数。`prev_sum` 是这个 `0` 左边连续 `1` 的长度，`prefix[-1]` 是当前末尾连续 `1` 的长度。两段加起来，再给中间翻掉的 `0` 加 `1`。

注释里写了 `prefix-sum`，这个数组实际记录的是每个位置结尾的连续 `1` 长度。遇到 `0` 就重新从零开始。两个 `0` 挨着时，后面那个 `0` 左边的连续 `1` 长度就是 `0`。

问题出在那个固定的 `+1`。输入 `[1, 1]`，代码能算出 `0 + 2 + 1 = 3`。总共俩元素，第三个全靠我加得理直气壮。最初从下标 `1` 开始遍历的版本还有另一个边界问题，`[0]` 会直接返回初始值 `0`。下面的版本从下标 `0` 开始，并在最后把答案限制在数组长度以内。

这里的 `min(ans, len(nums))` 有具体依据。第一个 `0` 出现前，提前加的 `1` 可以由紧接开头那段 `1` 的第一个 `0` 补上，所以只要数组里有 `0`，这部分候选长度最终就能达到。全是 `1` 时，才需要把算出来的 `n + 1` 截回 `n`。

```python
# Solution 1
#  prefix-sum
class Solution:
    def findMaxConsecutiveOnes(self, nums: list[int]) -> int:
        ans = 0
        prefix = [0]
        prev_sum = 0
        for i in range(len(nums)):
            if i>= 1 and nums[i] == 0 and nums[i-1] == 0:
                prev_sum = 0
                prefix.append(0)
            elif i>= 1 and nums[i] == 0 and nums[i-1]!=0:
                prev_sum = prefix[-1]
                prefix.append(0)
                
            else:
                prefix.append(prefix[-1] + nums[i])
            ans = max(ans,prev_sum + prefix[-1]+1)
        return min(ans, len(nums))

```

时间 `O(n)`，额外空间 `O(n)`。每步只读取 `prefix` 的最后一项，历史长度可以用一个变量省掉。

## 踩坑二：DP 表填完了，答案该从哪儿拿（Solution 2）

二维表把推荐解里的两个状态逐行记了下来。`dp[i][0]` 和 `dp[i][1]` 都要求以 `i` 结尾。第一个数是 `1` 时，两种状态都是 `1`。第一个数是 `0` 时，两个状态分别是 `0` 和 `1`，后者可以翻转这个 `0`。因此 `dp[0][1]` 可以直接初始化为 `1`。

我一开始写到了 `print(dp)`，看着整张表还挺有成就感。力扣要的是返回值，我给它交了一张表。

用 `[1, 1, 0, 0]` 看第二列就明白了：

| `i` | 当前数字 | `dp[i][0]` | `dp[i][1]` |
| --- | --- | --- | --- |
| 0 | 1 | 1 | 1 |
| 1 | 1 | 2 | 2 |
| 2 | 0 | 0 | 3 |
| 3 | 0 | 0 | 1 |

最长的一段在下标 `2` 结束，所以取第二列的最大值 `3`。直接返回 `dp[-1][1]` 会只得到最后一行的 `1`。

```python
#Solution 2 DP
class Solution:
    def findMaxConsecutiveOnes(self, nums: list[int]) -> int:
        dp = [[0] * 2 for _ in range(len(nums))]
        dp[0][0] = nums[0]
        dp[0][1] = 1
        for i in range(1, len(nums)):
            if nums[i] == 1:
                dp[i][0]=dp[i-1][0] + 1
                dp[i][1] = dp[i-1][1] + 1
            else:
                dp[i][0] = 0
                dp[i][1] = dp[i-1][0] + 1
        # print(dp)
        return max(row[1] for row in dp)
        

        
```

时间 `O(n)`，额外空间 `O(n)`。观察到下一行只用上一行，便可以把整张表压缩成开头的两个变量，同时在遍历中更新答案。

## 笔记样例

这个单元格调用的是 Solution 3。单独运行时，先执行开头的滚动 DP 代码块。

```python
nums = [1, 0, 1, 1, 0, 1]
solution = Solution().findMaxConsecutiveOnes(nums)
print(solution)
```

输出 `4`。翻转第一个 `0` 可得到开头四个连续的 `1`，翻转第二个 `0` 则可以得到末尾四个连续的 `1`。
