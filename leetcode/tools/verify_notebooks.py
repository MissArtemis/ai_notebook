"""Validate the curated notebooks; optionally compare public sources and execute cells."""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]


def sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def graphql(query, variables):
    request = Request('https://leetcode.cn/graphql/',
                      data=json.dumps({'query': query, 'variables': variables}).encode(),
                      headers={'Content-Type': 'application/json', 'User-Agent': 'ai-notebook-source-check/1.0'})
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    require(not result.get('errors'), f"GraphQL: {result.get('errors')}")
    return result['data']


def flatten(node):
    return node.get('text', '') + ''.join(flatten(child) for child in node.get('children', []))


def source_blocks(slate):
    return [{'language': tab.get('language'), 'code': flatten(tab)}
            for node in json.loads(slate) if node.get('type') == 'CodeBlock'
            for tab in node['children']]


def check_coverage(manifest):
    solutions = []
    while True:
        result = graphql('query($slug:String!,$skip:Int){solutionArticles(userSlug:$slug,skip:$skip,first:100){pageInfo{hasNextPage} edges{node{slug}}}}',
                         {'slug': '4bg5t', 'skip': len(solutions)})['solutionArticles']
        page = [edge['node']['slug'] for edge in result['edges']]
        require(page or not result['pageInfo']['hasNextPage'], 'Solution pagination made no progress')
        solutions.extend(page)
        if not result['pageInfo']['hasNextPage']:
            break
    discussions = []
    token = None
    seen = set()
    while True:
        result = graphql('query($slug:String!,$token:ID){columnsPublishedContents(userSlug:$slug,nextToken:$token){nodes{... on QAQuestionNode{uuid} ... on ColumnArticleNode{uuid}} nextToken}}',
                         {'slug': '4bg5t', 'token': token})['columnsPublishedContents']
        discussions.extend(node['uuid'] for node in result['nodes'])
        token = result['nextToken']
        if token is None:
            break
        require(token not in seen, 'Discussion pagination repeated a token')
        seen.add(token)
    for kind, actual in [('solution', solutions), ('discussion', discussions)]:
        expected = {item['id'] for item in manifest['sources'] if item['kind'] == kind}
        require(set(actual) == expected, f'{kind} coverage changed: online={set(actual)}, recorded={expected}')
        count_key = 'solutions' if kind == 'solution' else 'discussions'
        require(len(actual) == manifest['coverage'][count_key], f'{kind} count mismatch')
    print(f'Public coverage: {len(solutions)} solutions, {len(discussions)} discussions; pagination exhausted')


def fetch_slate(entry):
    if entry['kind'] == 'solution':
        data = graphql('query($slug:String!){solutionArticle(slug:$slug){slateValue author{username}}}',
                       {'slug': entry['id']})['solutionArticle']
        require(data['author']['username'] == '4bg5t', f"Unexpected author: {entry['id']}")
    else:
        data = graphql('query($uuid:ID!){qaQuestion(uuid:$uuid){slateValue contentAuthor{userSlug}}}',
                       {'uuid': entry['id']})['qaQuestion']
        require(data['contentAuthor']['userSlug'] == '4bg5t', f"Unexpected author: {entry['id']}")
    return data['slateValue']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--online', action='store_true', help='Check all profile pages and compare code with live public posts')
    parser.add_argument('--execute', action='store_true', help='Execute each notebook in a fresh Python kernel; do not save outputs')
    args = parser.parse_args()
    import nbformat

    manifest = json.loads((ROOT / 'leetcode/sources.json').read_text(encoding='utf-8'))
    if args.online:
        check_coverage(manifest)
    total = 0
    executed = 0
    for entry in manifest['sources']:
        path = ROOT / entry['notebook']
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        require(notebook.metadata.leetcode.source_id == entry['id'], f'{path}: source mismatch')
        cells = {cell.id: cell for cell in notebook.cells}
        require(len(cells) == len(notebook.cells), f'{path}: duplicate cell ids')
        online = source_blocks(fetch_slate(entry)) if args.online else None
        tracked_cells = set()
        for block in entry['blocks']:
            cell = cells[block['cell_id']]
            tracked_cells.add(cell.id)
            text = cell.source
            if block['presentation'] == 'excerpt':
                require(text.startswith('```python\n') and text.endswith('\n```'), f'{path}: malformed excerpt')
                text = text[len('```python\n'):-len('\n```')]
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
