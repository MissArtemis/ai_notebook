"""Locate the bound notebook repository and run its maintained workflow tools."""

import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path)
    parser.add_argument('command', choices=['fetch', 'build', 'index', 'verify'])
    args, rest = parser.parse_known_args()
    root = args.repo
    if root is None:
        for parent in [Path.cwd(), *Path.cwd().parents]:
            if (parent / 'leetcode/sync_config.json').is_file():
                root = parent
                break
    if root is None:
        binding = Path(__file__).resolve().parents[1] / 'repo.json'
        if binding.exists():
            root = Path(json.loads(binding.read_text(encoding='utf-8'))['repo'])
    if root is None or not (root / 'leetcode/sync_config.json').is_file():
        parser.error('Run from ai_notebook, pass --repo PATH, or install with leetcode/tools/install_sync_skill.py')
    root = root.resolve()
    tool = 'verify_notebooks.py' if args.command == 'verify' else 'sync_leetcode.py'
    command = [sys.executable, '-u', str(root / 'leetcode/tools' / tool), '--repo', str(root)]
    if args.command != 'verify':
        command.append(args.command)
    raise SystemExit(subprocess.call([*command, *rest], cwd=root))


if __name__ == '__main__':
    main()
