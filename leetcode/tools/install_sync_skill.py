"""Install this repository's reusable skill and bind it to this checkout."""

import argparse
import json
import os
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, help='Override the skill directory (useful for an isolated installation)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    source = root / '.codex/skills/leetcode-notebook-sync'
    codex_dir = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
    destination = args.dest or codex_dir / 'skills/leetcode-notebook-sync'
    if destination.resolve() == source.resolve():
        parser.error('Install outside the version-controlled source skill directory')
    files = ['SKILL.md', 'agents/openai.yaml', 'scripts/run.py']
    for relative in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
    (destination / 'repo.json').write_text(json.dumps({'repo': str(root)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Installed skill: {destination.resolve()}')
    print(f'Bound repository: {root}')


if __name__ == '__main__':
    main()
