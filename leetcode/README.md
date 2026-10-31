# 力扣笔记

整理自 [公开主页](https://leetcode.cn/u/4bg5t/)，最近内容同步：**2026-10-31**。

原代码逐字保留，只加少量独立注释。比赛代码来自本人排行榜中的通过提交；片段与占位简短标明。

## 题解（15 篇）

| 笔记 | 来源 |
| --- | --- |
| [301. 删除无效的括号](daily_challenge/no301.ipynb) | [原文](https://leetcode.cn/problems/remove-invalid-parentheses/solution/301-shan-chu-wu-xiao-de-gua-hao-bfs-zui-hsh84/) |
| [279. 完全平方数：BFS、DFS 与 DP](daily_challenge/no279.ipynb) | [原文](https://leetcode.cn/problems/perfect-squares/solution/cong-num-squarechai-jie-bfsdfshe-dp-by-4-ykk0/) |
| [1021. 删除最外层的括号](daily_challenge/no1021.ipynb) | [原文](https://leetcode.cn/problems/remove-outermost-parentheses/solution/1021-shan-chu-zui-wai-ceng-de-gua-hao-sh-0p55/) |
| [1541. 平衡括号字符串的最少插入次数](daily_challenge/1541.ipynb) | [原文](https://leetcode.cn/problems/minimum-insertions-to-balance-a-parentheses-string/solution/1541-ping-heng-gua-hao-zi-fu-chuan-de-zu-i608/) |
| [2333. 最小差值平方和](daily_challenge/no2333.ipynb) | [原文](https://leetcode.cn/problems/minimum-sum-of-squared-difference/solution/2333zhe-ye-neng-jiao-mediumcong-liang-ba-50lm/) |
| [2916. 子数组不同元素数目的平方和 II](daily_challenge/no2916.ipynb) | [原文](https://leetcode.cn/problems/subarrays-distinct-element-sum-of-squares-ii/solution/2916xian-duan-shu-xian-bie-ji-zhao-bei-b-fj90/) |
| [4068. 会议收益：搜索到二分优化 DP](daily_challenge/no4068.ipynb) | [原文](https://leetcode.cn/problems/subarrays-distinct-element-sum-of-squares-ii/solution/4068kai-hui-zhuan-qian-mo-yu-ye-zhuan-qi-akyz/) |
| [3551. 数位和排序需要的最小交换次数](daily_challenge/no3551.ipynb) | [原文](https://leetcode.cn/problems/minimum-swaps-to-sort-by-digit-sum/solution/python3-pai-xu-hou-shu-quan-bfs-bing-cha-j0ku/) |
| [3644. 排序排列：错位元素按位与](daily_challenge/no3644.ipynb) | [原文](https://leetcode.cn/problems/maximum-k-to-sort-a-permutation/solution/3644ti-mu-rang-wo-pai-xu-wo-que-zhi-xie-6sxl7/) |
| [743. 网络延迟时间：Dijkstra 模板](daily_challenge/no743.ipynb) | [原文](https://leetcode.cn/problems/network-delay-time/solution/743-wang-luo-yan-chi-shi-jian-yong-yi-da-23q4/) |
| [2093. 前往目标城市的最小费用：分层 Dijkstra](daily_challenge/no2093.ipynb) | [原文](https://leetcode.cn/problems/minimum-cost-to-reach-city-with-discounts/solution/2093-qian-wang-mu-biao-cheng-shi-de-zui-zt831/) |
| [465. 最优账单平衡：贪心踩坑、DFS 与状态压缩 DP](daily_challenge/no465.ipynb) | [原文](https://leetcode.cn/problems/optimal-account-balancing/solution/465qian-du-huan-qing-liao-li-kou-huan-bu-eszd/) |
| [666. 路径总和 IV：节点编码与 DFS](daily_challenge/no666.ipynb) | [原文](https://leetcode.cn/problems/path-sum-iv/solution/666-lu-jing-zong-he-iv-de-jie-dian-bian-4l18r/) |
| [3882. 网格图中最小异或路径：集合 DP 与滚动数组](daily_challenge/no3882.ipynb) | [原文](https://leetcode.cn/problems/minimum-xor-path-in-a-grid/solution/3882-wang-ge-tu-zhong-zui-xiao-yi-huo-lu-6pwv/) |
| [3619. 总价值可以被 K 整除的岛屿数目：DFS](daily_challenge/no3619.ipynb) | [原文](https://leetcode.cn/problems/count-islands-with-total-value-divisible-by-k/solution/3619-zong-jie-zhi-ke-yi-bei-k-zheng-chu-kysza/) |

## 讨论（3 篇）

| 笔记 | 来源 |
| --- | --- |
| [第 523 场周赛](contests/weekly_523.ipynb) | [原文](https://leetcode.cn/discuss/post/sLnQAI/) |
| [第 193 场双周赛](contests/biweekly_193.ipynb) | [原文](https://leetcode.cn/discuss/post/JelbXH/) |
| [第 524 场周赛：公开文章与比赛通过代码](contests/weekly_524_public.ipynb) | [原文](https://leetcode.cn/discuss/post/lYH5ET/) |

## 本地周赛复盘

| 比赛 | 题解 | 代码 |
| --- | --- | --- |
| 第 524 场周赛 | [异或负责吓人，颜色负责认爹，区间负责让我加班](contests/weekly_524_solution.md) | [weekly_524.ipynb](contests/weekly_524.ipynb) |

## 复用与校验

[任务说明与复用流程](SYNC_TASK.md) · [来源清单](sources.json)

```bash
python leetcode/tools/sync_leetcode.py fetch
python leetcode/tools/verify_notebooks.py --online --execute
```

仓库已有历史材料保留。4068 会议文章挂在 2916 题下，按实际内容命名；双周赛 193 第四题只有未完成占位。
