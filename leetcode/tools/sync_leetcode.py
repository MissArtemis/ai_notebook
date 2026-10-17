"""Incremental public-post fetch, reviewed notebook build, and index generation."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

from leetcode_source import fetch_post, list_posts, reading_text, require, sha256


DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def repo_path(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to((root / 'leetcode').resolve()), f'Output must stay within leetcode/: {relative}')
    require('..' not in Path(relative).parts and not Path(relative).is_absolute(), f'Use a repository-relative path: {relative}')
    return path


def identity(item):
    return item['kind'], item['id']


def compare(snapshot, manifest):
    previous = {identity(entry): entry for entry in manifest.get('sources', [])}
    result = {'new': [], 'updated': [], 'unchanged': [], 'missing': []}
    for post in snapshot['posts']:
        old = previous.pop(identity(post), None)
        if old is None:
            status = 'new'
        elif old.get('source_content_sha256'):
            status = 'unchanged' if old['source_content_sha256'] == post['source_content_sha256'] else 'updated'
        else:
            # First-run compatibility with the original 2026-10-17 manifest.
            same = old.get('source_slate_sha256') == post['source_slate_sha256'] and old['title'] == post['title']
            status = 'unchanged' if same else 'updated'
        result[status].append({'id': post['id'], 'kind': post['kind'], 'title': post['title'],
                               'notebook': old.get('notebook') if old else None})
    result['missing'] = [{'id': entry['id'], 'kind': entry['kind'], 'title': entry['title'], 'notebook': entry['notebook']}
                         for entry in previous.values()]
    return result


def fetch(root, cache):
    config = load(root / 'leetcode/sync_config.json')
    posts = [fetch_post(post, config['user_slug']) for post in list_posts(config['user_slug'])]
    snapshot = {'profile': config['profile'], 'user_slug': config['user_slug'],
                'fetched_at': datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'), 'posts': posts}
    manifest = load(root / 'leetcode/sources.json') if (root / 'leetcode/sources.json').exists() else {'sources': []}
    plan = compare(snapshot, manifest)
    write(cache / 'snapshot.json', snapshot)
    write(cache / 'plan.json', plan)
    for post in posts:
        require(re.fullmatch(r'[A-Za-z0-9_-]+', post['id']), 'Unsafe public article identifier')
        folder = cache / 'articles'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (post['id'] + '.md')).write_text('# ' + post['title'] + '\n\n' + post['url'] + '\n\n' + reading_text(post), encoding='utf-8')
    drafts = []
    for item in plan['new'] + plan['updated']:
        drafts.append({'id': item['id'], 'kind': item['kind'], 'notebook': item['notebook'] or '',
                       'title': '', 'summary': '', 'cells': [], 'omissions': []})
    # Never overwrite an agent's working curation.json; this is a fresh reference scaffold.
    write(cache / 'curation.template.json', {'status': 'draft', 'snapshot_fetched_at': snapshot['fetched_at'], 'entries': drafts})
    print(json.dumps({key: len(value) for key, value in plan.items()}, ensure_ascii=False))
    print(f'Reading copies and snapshot: {cache}')
    return snapshot, plan


def make_notebook(post, spec, fetched_at):
    require(spec.get('title') and spec.get('summary') and spec.get('cells'), f"Write concise notes before building {post['id']}")
    cells = []
    retained = []
    used = set()

    def cell(kind, text, metadata=None):
        item = {'cell_type': kind, 'id': f'cell-{len(cells):03d}', 'metadata': metadata or {}, 'source': text.splitlines(keepends=True)}
        if kind == 'code':
            item.update(execution_count=None, outputs=[])
        cells.append(item)
        return item['id']

    intro = f"# {spec['title']}\n\n{spec['summary']}\n\n[原文]({post['url']}) · 整理于 {fetched_at[:10]}。原代码保持原样；补充注释另放单元格。"
    cell('markdown', intro)
    for item in spec['cells']:
        kind = item['type']
        if kind == 'markdown':
            cell('markdown', item['text'])
        elif kind == 'annotation':
            cell('code', '\n'.join('# ' + line if line else '#' for line in item['text'].splitlines()), {'role': 'annotation'})
        elif kind == 'example':
            compile(item['text'], post['id'] + ':example', 'exec')
            cell('code', item['text'], {'role': 'example'})
        elif kind == 'source':
            index = item['block']
            require(isinstance(index, int) and 0 <= index < len(post['blocks']) and index not in used, f'Invalid/repeated block: {index}')
            used.add(index)
            block = post['blocks'][index]
            code = block['code']
            presentation = item.get('presentation', 'code')
            require(presentation in {'code', 'excerpt'}, 'Source presentation must be code or excerpt')
            if presentation == 'code':
                require(block['language'].lower() in {'python', 'python3', 'py'}, 'Non-Python blocks must be excerpts')
                compile(code, post['id'] + ':source', 'exec')
            meta = {'leetcode_source': {'id': post['id'], 'block': index, 'sha256': sha256(code)}}
            language = 'python' if block['language'].lower() in {'python', 'python3', 'py'} else block['language'] or 'text'
            content = '```' + language + '\n' + code + '\n```' if presentation == 'excerpt' else code
            cid = cell('markdown' if presentation == 'excerpt' else 'code', content, meta)
            record = {'index': index, 'language': block['language'], 'sha256': sha256(code), 'cell_id': cid, 'presentation': presentation}
            if presentation == 'excerpt':
                record['fence_language'] = language
            retained.append(record)
        else:
            raise ValueError(f'Unknown curated cell type: {kind}')
    omitted = []
    for item in spec.get('omissions', []):
        index = item['block']
        require(isinstance(index, int) and 0 <= index < len(post['blocks']) and index not in used, f'Invalid/repeated omission: {index}')
        require(item.get('reason', '').strip(), 'Explain each omitted block')
        used.add(index)
        block = post['blocks'][index]
        omitted.append({'index': index, 'language': block['language'], 'sha256': sha256(block['code']), 'reason': item['reason']})
    require(used == set(range(len(post['blocks']))), f"Account for every source block in {post['id']}; missing {set(range(len(post['blocks']))) - used}")
    notebook = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                'language_info': {'name': 'python'}, 'leetcode': {'source_id': post['id'], 'url': post['url'], 'fetched_at': fetched_at[:10]}},
                'nbformat': 4, 'nbformat_minor': 5}
    entry = {'id': post['id'], 'kind': post['kind'], 'title': post['title'], 'note_title': spec['title'], 'summary': spec['summary'],
             'url': post['url'], 'notebook': spec['notebook'], 'source_slate_sha256': post['source_slate_sha256'],
             'source_content_sha256': post['source_content_sha256'], 'blocks': retained, 'omitted_blocks': omitted}
    return notebook, entry


def build(root, cache, curation_path):
    import nbformat
    config = load(root / 'leetcode/sync_config.json')
    snapshot = load(cache / 'snapshot.json')
    manifest = load(root / 'leetcode/sources.json') if (root / 'leetcode/sources.json').exists() else {'sources': []}
    require(snapshot['profile'] == config['profile'] and snapshot['user_slug'] == config['user_slug'], 'Snapshot belongs to another profile')
    plan = compare(snapshot, manifest)
    require(not plan['missing'], 'Previously recorded posts are missing; preserve their notebooks and investigate before building')
    required = {identity(item) for item in plan['new'] + plan['updated']}
    spec = load(curation_path)
    require(spec.get('status') == 'reviewed', 'Curation is still a draft: read and edit it, then set status=reviewed')
    require(spec.get('snapshot_fetched_at') == snapshot['fetched_at'], 'Curation refers to another fetch; review the current snapshot')
    entries = spec['entries']
    require(len({identity(item) for item in entries}) == len(entries), 'Duplicate curation entries')
    require({identity(item) for item in entries} == required, 'Curation must cover exactly the new and updated posts')
    if not required:
        print('No new or updated posts; tracked files remain unchanged')
        return
    posts = {identity(post): post for post in snapshot['posts']}
    previous = {identity(entry): entry for entry in manifest['sources']}
    owners = {entry['notebook']: identity(entry) for entry in manifest['sources']}
    outputs = []
    for item in entries:
        key = identity(item)
        path = repo_path(root, item['notebook'])
        require(path.suffix == '.ipynb', 'Notebook path must end in .ipynb')
        require(item['notebook'] not in owners or owners[item['notebook']] == key, 'Another source already owns this notebook')
        if key in previous:
            require(previous[key]['notebook'] == item['notebook'], 'Keep the existing notebook path; handle renaming as a separate edit')
        else:
            require(not path.exists(), f'Do not overwrite an unrelated file: {path}')
        require(all(out[0] != path for out in outputs), 'Two curated entries use the same path')
        book, entry = make_notebook(posts[key], item, snapshot['fetched_at'])
        nbformat.validate(nbformat.from_dict(book))
        outputs.append((path, book))
        previous[key] = entry
    updated = dict(manifest)
    updated.update(profile=config['profile'], fetched_at=snapshot['fetched_at'][:10],
                   coverage={'solutions': sum(p['kind'] == 'solution' for p in snapshot['posts']),
                             'discussions': sum(p['kind'] == 'discussion' for p in snapshot['posts']),
                             'solutions_has_next_page': False, 'discussions_next_token': None})
    updated['sources'] = list(previous.values())
    # Prepare and validate every output first; no partial changes on invalid curation.
    for path, book in outputs:
        write(path, book)
    write(root / 'leetcode/sources.json', updated)
    render_index(root, updated)
    print(f'Built {len(outputs)} notebooks; updated sources.json and leetcode/README.md')


def render_index(root, manifest=None):
    manifest = manifest or load(root / 'leetcode/sources.json')
    def escaped(text):
        return text.replace('|', '\\|').replace('\n', ' ')
    lines = ['# 力扣笔记', '', f"整理自 [公开主页]({manifest['profile']})，最近内容同步：**{manifest['fetched_at'][:10]}**。",
             '', '原代码逐字保留；简短说明与新增注释放在独立单元格。局部片段、错误版本和未完成占位会单独标明。', '']
    for kind, title in [('solution', '题解'), ('discussion', '讨论')]:
        selected = [e for e in manifest['sources'] if e['kind'] == kind]
        lines.extend(['## ' + title + f'（{len(selected)} 篇）', '', '| 笔记 | 来源 |', '| --- | --- |'])
        for entry in selected:
            path = Path(entry['notebook']).relative_to('leetcode').as_posix()
            title = escaped(entry.get('note_title') or entry['title'])
            lines.append(f"| [{title}]({path}) | [原文]({entry['url']}) |")
        lines.append('')
    lines.extend(['## 复用与校验', '', '[任务说明与复用流程](SYNC_TASK.md) · [来源清单](sources.json)', '',
                  '```bash', 'python leetcode/tools/sync_leetcode.py fetch',
                  'python leetcode/tools/verify_notebooks.py --online --execute', '```', '',
                  '仓库已有历史材料保留。4068 会议文章挂在 2916 题下，按实际内容命名；双周赛 193 第四题只有未完成占位。', ''])
    (root / 'leetcode/README.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--cache', type=Path, help='Override the local snapshot directory')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('fetch', help='Fetch every public post and write an incremental plan; no tracked files change')
    b = commands.add_parser('build', help='Build only new/updated notebooks from agent-reviewed curation')
    b.add_argument('--curation', type=Path)
    commands.add_parser('index', help='Regenerate leetcode/README.md from sources.json')
    args = parser.parse_args()
    root = args.repo.resolve()
    config = load(root / 'leetcode/sync_config.json')
    cache = args.cache.resolve() if args.cache else root / config['cache_dir']
    if args.command == 'fetch':
        fetch(root, cache)
    elif args.command == 'build':
        build(root, cache, args.curation or cache / 'curation.json')
    else:
        render_index(root)


if __name__ == '__main__':
    main()
