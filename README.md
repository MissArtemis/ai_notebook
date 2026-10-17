# AI Notebook

A personal knowledge base for organizing notes, explanations, and practical exercises related to artificial intelligence and its foundations.

## Contents

- Deep learning — concepts and notes
- Large language models — notes and related resources
- Machine learning — concepts and notes
- Statistics — mathematical foundations
- [`leetcode/`](./leetcode/README.md) — concise Jupyter notes synced from [my LeetCode profile](https://leetcode.cn/u/4bg5t/); see the index for current coverage and the [reusable sync workflow](./leetcode/SYNC_TASK.md)

## Working with the repository

Add notes and examples to the folder that best matches the topic. Keep filenames descriptive so that individual subjects are easy to find. Open the algorithm notebooks with JupyterLab:

```bash
jupyter lab
```

To validate source-code fidelity and execute all curated LeetCode notebooks in fresh kernels:

```bash
python leetcode/tools/verify_notebooks.py --online --execute
```

This repository is maintained as a personal learning resource. Content may be incomplete or updated as understanding develops.
