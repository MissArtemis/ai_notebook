# 力扣笔记

整理自 [4bg5t 的公开主页](https://leetcode.cn/u/4bg5t/)，截至 **2026-10-17**：7 篇题解、2 篇讨论，两个列表均已翻页至末尾。

笔记保留状态、转移、边界和主要踩坑，使用短 Markdown 与代码注释说明。原文代码单元格逐字保留，新增注释单独放在相邻单元格；每版实现后的样例为补充验证代码。同名 `Solution` 顺序覆盖，每版样例紧随对应实现执行。

## 题解

| 题目 | Notebook | 要点 |
| --- | --- | --- |
| 279. 完全平方数 | [no279.ipynb](daily_challenge/no279.ipynb) | BFS、朴素 DFS、记忆化 DFS、迭代 DP 与通用模板 |
| 301. 删除无效的括号 | [no301.ipynb](daily_challenge/no301.ipynb) | BFS 层序、最少删除、收集同层全部答案 |
| 1021. 删除最外层的括号 | [no1021.ipynb](daily_challenge/no1021.ipynb) | 深度筛选、断点切片、偏移错误 |
| 1541. 平衡括号字符串的最少插入次数 | [1541.ipynb](daily_challenge/1541.ipynb) | 右括号分组、need 状态、边界与收尾 |
| 2333. 最小差值平方和 | [no2333.ipynb](daily_challenge/no2333.ipynb) | 逐次模拟瓶颈、排序削峰、整除与余数 |
| 2916. 子数组不同元素数目的平方和 II | [no2916.ipynb](daily_challenge/no2916.ipynb) | 平方差、最后出现位置、懒标记线段树 |
| 4068. 会议收益 | [no4068.ipynb](daily_challenge/no4068.ipynb) | DFS、BFS、基础 DP、二分与前缀最优值 |

4068 那篇原文发布在 2916 题下，笔记按标题和实际算法内容命名，并保留原始来源链接。

## 讨论

| 讨论 | Notebook | 要点 |
| --- | --- | --- |
| 第 523 场周赛 | [weekly_523.ipynb](contests/weekly_523.ipynb) | 连续斐波那契三项、质数贪心、订座记账、质数 0/1 背包 |
| 第 193 场双周赛 | [biweekly_193.ipynb](contests/biweekly_193.ipynb) | 负数配对、连续同余段、前缀树与逆序对题意 |

讨论中的部分题仅公开代码片段，笔记据此记录思路，不补写未公开的实现。双周赛第四题的 `return 0` 保留并标为**未完成占位**。依赖上下文的片段与错误代码放在 Markdown 代码块中，便于整本执行。

## 阅读与校验

安装 `jupyterlab`、`nbformat`、`nbclient`、`ipykernel` 后，在仓库根目录运行：

```bash
jupyter lab
python leetcode/tools/verify_notebooks.py
python leetcode/tools/verify_notebooks.py --online --execute
```

默认校验 Notebook 结构、原始代码 SHA-256 与补充单元格分类。`--online` 重新读取公开列表，核对覆盖范围与每段原代码；`--execute` 在独立内核执行各本笔记及样例，不保存运行输出。在线源内容发生变化时校验会失败，需要人工复核后更新。

[sources.json](sources.json) 保存来源链接、代码块位置与摘要，不复制冗长原文。原文中被省略的重复局部代码和文字示意也逐块登记，方便审计。

仓库原有的 `.py` 练习和 `note/` 历史材料保留；本次整理以以上 9 本 Notebook 为入口。
