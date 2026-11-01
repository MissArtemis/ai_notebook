"""保留原 Notebook 解法，补充对照解法、笔记与可运行样例，并独立校验。"""
from pathlib import Path
from itertools import product
import contextlib
import heapq
import io
import json
import random
import re

REPO = next(p for p in Path(__file__).resolve().parents if (p / "leetcode").is_dir())
NOTE = REPO / "leetcode/note/leetcode_1541_minimum_insertions.md"
NB = REPO / "leetcode/daily_challenge/1541.ipynb"
OUT = REPO / "leetcode/note/publish/LeetCode1541_12张图文/源文件"


def oracle(s):
    """Dijkstra：消费原字符成本 0，插入字符成本 1。

    状态 (输入位置, 未闭合左括号数, 是否已读取半个右括号组)。
    按合法语言的字符转移搜索，不使用任何贪心规则。
    """
    limit = 2 * len(s)  # 每个输入字符可单独扩展为 ())，插入最多 2n
    start = (0, 0, 0)
    dist = {start: 0}
    queue = [(0, start)]
    while queue:
        cost, state = heapq.heappop(queue)
        if cost != dist[state]:
            continue
        pos, left, half = state
        if pos == len(s) and left == 0 and half == 0:
            return cost
        for ch in "()":
            if ch == "(":
                if half:
                    continue
                next_left, next_half = left + 1, 0
            else:
                if left == 0:
                    continue
                next_left, next_half = (left - 1, 0) if half else (left, 1)
            for consume in (True, False):
                if consume and (pos == len(s) or s[pos] != ch):
                    continue
                next_cost = cost + (0 if consume else 1)
                if next_cost > limit:
                    continue
                target = (pos + int(consume), next_left, next_half)
                if next_cost < dist.get(target, float("inf")):
                    dist[target] = next_cost
                    heapq.heappush(queue, (next_cost, target))
    raise AssertionError(s)


def cell(kind, source, name):
    data = {"cell_type": kind, "id": name, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        data.update(execution_count=None, outputs=[])
    return data


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    nb = json.loads(NB.read_text(encoding="utf-8"))
    original = next(c for c in nb["cells"] if c["cell_type"] == "code" and "class Solution:" in "".join(c["source"]))
    original_source = "".join(original["source"])
    note = NOTE.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", note, re.S)
    compact = blocks[0].strip()
    need = next(b.strip() for b in blocks if b.startswith("class Solution:") and "need = 0" in b)
    need_nb = need.replace("class Solution:", "class Solution2:", 1)
    cells = [
        cell("markdown", "# 1541. 平衡括号字符串的最少插入次数\n\n题目：[力扣 1541](https://leetcode.cn/problems/minimum-insertions-to-balance-a-parentheses-string/)\n\n一个 `(` 匹配两个连续的 `)`。和 1021 的普通括号匹配相比，关闭单位从 `)` 变成 `))`，输入也不再保证平衡。\n\n## Solution 1：我的修正版，按右括号分组\n\n`left_cnt` 是当前尚未匹配的左括号数，不是左括号总数。每组 `))` 消耗一个左括号；单独的 `)` 补齐一组，没有左括号就补一个 `(`。扫描完补 `2 * left_cnt`。\n\n以下保留原代码逻辑。时间 O(n)，额外空间 O(1)。", "1541intro"),
        original,
        cell("markdown", "## 两个实际踩坑\n\n1. 检查 `s[i + 1]` 只需 `i < len(s) - 1`。原来的 `i < len(s) - 2` 会把 `())` 中现有的两个连续右括号拆开，错算成 3，正确是 0。\n2. `(` 的答案是 2；不能直接返回 `insert_cnt`，要结算剩余左括号。1021 输入合法会自然归零，本题不会。\n\n## Solution 2：逐字符统计欠下的右括号\n\n`need` 表示当前还欠多少个右括号。遇到 `(`，若旧 `need` 是奇数，先补一个 `)` 完成旧半组，再 `need += 2`。遇到 `)` 先减一；若变成 -1，补一个 `(`，当前右括号已满足一半，令 `need = 1`。最后加上 `need`。\n\n这份代码更简洁，两种解法的复杂度相同。单独提交时将 `Solution2` 改成 `Solution`。", "1541need"),
        cell("code", need_nb + "\n", "1541sol2"),
        cell("markdown", "## 与 1021 对照：计数器为什么有效？\n\n| 内容 | 1021 | 1541 |\n| --- | --- | --- |\n| 关闭单位 | 一个 `)` | 连续的 `))` |\n| 计数含义 | 未闭合左括号数，即深度 | 未匹配左括号数，或右括号需求 |\n| 处理右括号 | 一个字符令深度减一 | 一组字符令左计数减一 |\n| 输入 | 保证合法 | 可能不平衡 |\n| 末尾处理 | 深度自然归零 | 补 `2 * left_cnt` 或 `need` |\n| 额外空间 | Python 结果列表 O(n) | 只返回次数 O(1) |\n\n同类左括号栈只需要长度时，可以压缩成计数器。分组法一次完成整个关闭单位；逐字符法还要知道有没有半组，用 `need` 的奇偶性表达。多类型括号或需要匹配下标时，单一计数通常不够。\n\n不能只算全串数量：`))(` 左 1 右 2，仍需插入 3 次；`倍数正确` 也不能替代连续性，`()()))` 的答案是 3。\n\n详细题解与正确性说明：[1541 学习笔记](../note/leetcode_1541_minimum_insertions.md)。", "1541compare"),
        cell("markdown", "## 样例与边界对照\n\n比较 `ans == expected`，同时检查两种解法。", "1541examples"),
        cell("code", '''cases = [
    ("(()))", 1), ("())", 0), ("))())(", 3),
    ("((((((", 12), (")))))))", 5),
    ("(", 2), (")", 2), ("))", 1), ("()", 1),
    ("()(", 3), ("))(", 3), ("()()))", 3), (")()(", 5),
]
for solution in (Solution(), Solution2()):
    for s, expected in cases:
        ans = solution.minInsertions(s)
        assert ans == expected, (type(solution).__name__, s, ans, expected)
    print(f"{type(solution).__name__}: {len(cases)} 个样例全部通过")
''', "1541tests"),
    ]
    env = {}
    count = 0
    for c in cells:
        if c["cell_type"] == "code":
            count += 1
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                exec(compile("".join(c["source"]), str(NB), "exec"), env)
            c["execution_count"] = count
            c["outputs"] = [{"name": "stdout", "output_type": "stream", "text": stream.getvalue().splitlines(keepends=True)}] if stream.getvalue() else []
    nb["cells"] = cells
    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    compact_env = {}
    exec(compact, compact_env)
    funcs = [env["Solution"]().minInsertions, compact_env["Solution"]().minInsertions, env["Solution2"]().minInsertions]
    total = 0
    for length in range(1, 10):
        for chars in product("()", repeat=length):
            s = "".join(chars)
            expected = oracle(s)
            assert all(f(s) == expected for f in funcs), (s, expected, [f(s) for f in funcs])
            total += 1
    rng = random.Random(1541)
    for _ in range(100):
        s = "".join(rng.choice("()") for _ in range(rng.randint(10, 35)))
        expected = oracle(s)
        assert all(f(s) == expected for f in funcs), s
    for s, expected in [("(" * 100000, 200000), (")" * 100000, 50000), ("())" * 33333, 0)]:
        assert all(f(s) == expected for f in funcs)
    result = {
        "sample_cases_per_implementation": len(env["cases"]),
        "implementations": ["原始修正版", "等价紧凑分组版", "need 版"],
        "oracle": "独立 Dijkstra 插入/消费字符状态图，不调用贪心转移",
        "exhaustive_lengths": "1—9", "exhaustive_strings": total,
        "random_seed": 1541, "random_oracle_cases": 100, "large_cases": 3,
        "status": "passed", "platform_submission": "未实际提交到力扣评测",
    }
    (OUT / "代码校验.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "配套代码.py").write_text(original_source.rstrip() + "\n\n\n" + need_nb + "\n", encoding="utf-8")
    (OUT / "提交版_分组.py").write_text(compact + "\n", encoding="utf-8")
    (OUT / "提交版_need.py").write_text(need + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
