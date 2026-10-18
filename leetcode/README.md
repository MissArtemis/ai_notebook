# 力扣笔记

整理自 [公开主页](https://leetcode.cn/u/4bg5t/)，最近内容同步：**2026-10-18**。

原代码逐字保留，只加少量独立注释。比赛代码来自本人排行榜中的通过提交；片段与占位简短标明。

## 题解（8 篇）

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

## 讨论（2 篇）

| 笔记 | 来源 |
| --- | --- |
| [第 523 场周赛](contests/weekly_523.ipynb) | [原文](https://leetcode.cn/discuss/post/sLnQAI/) |
| [第 193 场双周赛](contests/biweekly_193.ipynb) | [原文](https://leetcode.cn/discuss/post/JelbXH/) |

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
