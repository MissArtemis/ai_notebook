# 可复用任务：力扣文章 → Jupyter → GitHub

下次可以直接发送：

> 使用 $leetcode-notebook-sync 同步我的力扣题解和讨论：增量拉取新增或修改文章，用简短 Markdown 和独立代码注释整理成 Jupyter，原代码保持完全一致。覆盖每篇文章涉及的各题与主要解法，标清错误片段和未完成代码。运行校验与样例后提交并推送 GitHub，最后给我变更数量和目录链接。

## 固定约定

- 主页：[4bg5t](https://leetcode.cn/u/4bg5t/)。仓库：[MissArtemis/ai_notebook](https://github.com/MissArtemis/ai_notebook)。读取 [sync_config.json](sync_config.json) 获取用户、远端和分支。
- 一篇题解一本 Notebook，一篇比赛讨论一本，讨论内按题分节。已有文件名不因文章标题微调而改变。
- Markdown 重写为简短学习笔记，代码从源块直接提取，不重排、不格式化、不改类名；新增注释放相邻 annotation 单元格。
- 原文只贴片段就保留片段，不虚构完整实现。错误片段与未完成占位写明状态；需要上下文的内容放 Markdown 代码块。
- 同名 Solution 的样例紧随对应实现。原始算法与补充样例分开登记；保存文件不含旧输出。
- 所有公开题解和讨论分页至末尾。只变更新增或修改文章；缺失文章不自动删除已有笔记；无变化时不生成空提交。
- 本流程由用户按需调用；没有设置周期性自动运行。

## 安装与入口

Python 3.10+；首次在仓库根目录执行：

```bash
python -m pip install -r leetcode/requirements-sync.txt
python leetcode/tools/install_sync_skill.py
```

安装位置默认是 `$CODEX_HOME/skills/leetcode-notebook-sync`；未设置 CODEX_HOME 时为 `~/.codex/skills/leetcode-notebook-sync`。本机仓库绑定只写安装目录的 repo.json，不提交 Git。skill 的维护源位于 [.codex/skills/leetcode-notebook-sync](../.codex/skills/leetcode-notebook-sync/SKILL.md)，修改后重新运行安装脚本即可更新。

## 一次同步

```bash
python leetcode/tools/sync_leetcode.py fetch
```

只写忽略目录 `.cache/leetcode-sync/`：

| 文件 | 用途 |
| --- | --- |
| snapshot.json | 全部公开文章、原始 Slate/Markdown、按顺序提取的代码块及指纹 |
| articles/*.md | 方便阅读的原文副本；原始节点和链接仍保存在 snapshot.json |
| plan.json | new / updated / unchanged / missing |
| curation.template.json | 本轮新增和更新文章的待整理模板，不覆盖已有 curation.json |

由 Codex 读取变化文章并精简说明，将模板另存为 `curation.json`。根据实际内容选择代码块，完成后将 status 设为 reviewed。这个人工语义步骤不能由机械截断原文代替。

```bash
python leetcode/tools/sync_leetcode.py build --curation .cache/leetcode-sync/curation.json
python leetcode/tools/verify_notebooks.py --online --execute
```

build 更新本轮笔记、sources.json 和目录；无新增/更新时不触碰已跟踪文件。默认 verifier 只校验本地结构与摘要；`--online` 核对当前公开列表和每个原代码块，`--execute` 独立内核运行，不保存输出。

完成后检查 Git diff。按本任务的提交推送授权，核对配置指定的远端与分支，显式暂存本次文件、commit、push，再比较本地 HEAD 与远端。不要强推或夹带其他工作区改动。抓取失败、校验失败或 missing 未解释时，不报告同步成功。

## curation.json 格式

顶层必须包含 `status: "reviewed"`、与 snapshot.json 一致的 `snapshot_fetched_at`，以及恰好覆盖 new/updated 的 entries。文章 id 和 kind 沿用快照；新笔记路径放在 `leetcode/` 下，已有笔记保持原路径。

```json
{
  "status": "reviewed",
  "snapshot_fetched_at": "从 snapshot.json 复制本轮值",
  "entries": [
    {
      "id": "从快照复制文章 id",
      "kind": "solution",
      "notebook": "leetcode/daily_challenge/no题号.ipynb",
      "title": "题号与简短标题",
      "summary": "一两句说明题意、核心状态或方法。",
      "cells": [
        {"type": "markdown", "text": "## 方法\n\n简短解释状态与转移。"},
        {"type": "annotation", "text": "状态变量含义。\n关键边界与处理顺序。"},
        {"type": "source", "block": 0, "presentation": "code"},
        {"type": "example", "text": "assert Solution().method(样例输入) == 预期结果"},
        {"type": "markdown", "text": "下面是需上下文的局部片段，仅用于阅读。"},
        {"type": "source", "block": 2, "presentation": "excerpt"}
      ],
      "omissions": [
        {"block": 1, "reason": "与完整解法重复的局部展开；关键点已合并到说明。"}
      ]
    }
  ]
}
```

上面只是格式示意，样例输入和题号必须替换。`block` 是 snapshot.json 中该文章 blocks 数组的零基下标，包含纯文本块，不能只按 Python 块计数。所有块必须且只能进入 source 或 omissions 一次，省略时写具体理由。`source` 不接受自定义代码文本；构建时从快照读取，保留字节级内容摘要。

annotation 接受普通说明文本，构建器逐行添加 `# `；example 是独立补充样例。`code` 只接受可编译的 Python 块；模板、错误版、跨语言片段应按实际状态用 excerpt，且正文解释用途。不要将原文里的复杂或不可信顶层代码直接放进正常执行路径，先阅读再决定展示方式。

更新文章时先读取现有 Notebook，保留有价值的人工笔记与例子，再重建完整的该篇 entries 内容；块编号可能改变，要按快照重新核对。来源清单逐块登记省略部分，方便日后审计。

## 校验脚本自身

```bash
python -m unittest discover -s leetcode/tools/tests -v
```

不联网的回归测试使用临时目录，验证增量判断、原代码一致性、无更新时的幂等行为、草稿拒绝、路径限制及不完整整理的拒绝行为。
