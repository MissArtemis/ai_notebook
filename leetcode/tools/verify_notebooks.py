"""Validate the curated notebooks; optionally compare public sources and execute cells."""

import argparse
import json
from pathlib import Path

from leetcode_source import fetch_post, list_posts, require, sha256


ROOT = Path(__file__).resolve().parents[2]


def check_coverage(manifest, user_slug):
    posts = list_posts(user_slug)
    for kind, count_key in [('solution', 'solutions'), ('discussion', 'discussions')]:
        expected = {entry['id'] for entry in manifest['sources'] if entry['kind'] == kind}
        actual = {post['id'] for post in posts if post['kind'] == kind}
        require(actual == expected, f'{kind} coverage changed: online={actual}, recorded={expected}')
        require(len(actual) == manifest['coverage'][count_key], f'{kind} count mismatch')
    print(f'Public coverage: {len(posts)} posts; pagination exhausted')
    return {(post['kind'], post['id']): post for post in posts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--online', action='store_true', help='Check all profile pages and compare code with live public posts')
    parser.add_argument('--execute', action='store_true', help='Execute each notebook in a fresh Python kernel; do not save outputs')
    args = parser.parse_args()
    import nbformat

    root = args.repo.resolve()
    manifest = json.loads((root / 'leetcode/sources.json').read_text(encoding='utf-8'))
    config = json.loads((root / 'leetcode/sync_config.json').read_text(encoding='utf-8'))
    posts = check_coverage(manifest, config['user_slug']) if args.online else {}
    total = 0
    executed = 0
    for entry in manifest['sources']:
        path = (root / entry['notebook']).resolve()
        require(path.is_relative_to((root / 'leetcode').resolve()), 'Notebook path leaves leetcode/')
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        require(notebook.metadata.leetcode.source_id == entry['id'], f'{path}: source mismatch')
        cells = {cell.id: cell for cell in notebook.cells}
        require(len(cells) == len(notebook.cells), f'{path}: duplicate cell ids')
        live = fetch_post(posts[(entry['kind'], entry['id'])], config['user_slug']) if args.online else None
        if live is not None:
            fingerprint_key = 'source_content_sha256' if entry.get('source_content_sha256') else 'source_slate_sha256'
            require(entry.get(fingerprint_key) == live[fingerprint_key] and entry['title'] == live['title'],
                    f'{path}: article content changed; fetch and review it before publishing')
        online = live['blocks'] if live else None
        tracked_cells = set()
        for block in entry['blocks']:
            cell = cells[block['cell_id']]
            tracked_cells.add(cell.id)
            text = cell.source
            if block['presentation'] == 'excerpt':
                prefix = '```' + block.get('fence_language', 'python') + '\n'
                require(text.startswith(prefix) and text.endswith('\n```'), f'{path}: malformed excerpt')
                text = text[len(prefix):-len('\n```')]
            else:
                require(cell.cell_type == 'code', f'{path}: expected code cell')
                compile(text, str(path), 'exec')
            require(sha256(text) == block['sha256'], f'{path}: changed original block {block["index"]}')
            require(cell.metadata.leetcode_source.sha256 == block['sha256'], f'{path}: metadata hash mismatch')
            require(cell.metadata.leetcode_source.id == entry['id'] and cell.metadata.leetcode_source.block == block['index'],
                    f'{path}: metadata block mismatch')
            if online is not None:
                original = online[block['index']]
                require(original['code'] == text, f'{path}: live source differs at block {block["index"]}')
            total += 1
        if online is not None:
            inventory = entry['blocks'] + entry['omitted_blocks']
            require({b['index'] for b in inventory} == set(range(len(online))), f'{path}: incomplete block inventory')
            require(len(inventory) == len(online), f'{path}: repeated block inventory')
            for block in inventory:
                require(sha256(online[block['index']]['code']) == block['sha256'], f'{path}: source inventory changed')
        for cell in notebook.cells:
            if cell.cell_type == 'code' and cell.id not in tracked_cells:
                require(cell.metadata.get('role') in {'annotation', 'example'}, f'{path}: unclassified added code')
                if cell.metadata.role == 'annotation':
                    require(all(not line.strip() or line.lstrip().startswith('#') for line in cell.source.splitlines()),
                            f'{path}: annotation must contain only comments')
        if args.execute:
            from nbclient import NotebookClient
            NotebookClient(notebook, timeout=60, kernel_name='python3',
                           resources={'metadata': {'path': str(path.parent)}}).execute()
            executed += 1
        print(f'OK {entry["notebook"]}: {len(entry["blocks"])} original blocks')
    print(f'Validated {len(manifest["sources"])} notebooks, {total} exact source blocks; executed {executed} notebooks')


if __name__ == '__main__':
    main()
