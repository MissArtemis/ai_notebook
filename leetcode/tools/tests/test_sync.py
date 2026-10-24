"""Observable workflow invariants, using isolated data and no network."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import leetcode_source as source
import sync_leetcode as sync
import verify_notebooks as verifier


CODE = 'class Solution:\n    def answer(self):\n        # 原注释与空白必须保留\n        return 42\n'


def post(identifier='one', code=CODE):
    return {'id': identifier, 'kind': 'solution', 'title': '示例题解', 'url': 'https://leetcode.cn/example/',
            'source_content_sha256': source.sha256(code), 'source_slate_sha256': source.sha256(code),
            'blocks': [{'language': 'python', 'code': code}, {'language': 'plainText', 'code': '文字示意'}]}


def spec(identifier='one', path='leetcode/daily_challenge/no1.ipynb'):
    return {'id': identifier, 'kind': 'solution', 'notebook': path, 'title': '简短标题', 'summary': '独立总结。',
            'cells': [{'type': 'annotation', 'text': '补充解释。'}, {'type': 'source', 'block': 0},
                      {'type': 'example', 'text': 'assert Solution().answer() == 42'}],
            'omissions': [{'block': 1, 'reason': '文字示意已归纳进说明。'}]}


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.cache = self.root / '.cache/leetcode-sync'
        self.current = post()
        self.snapshot = {'profile': 'https://leetcode.cn/u/test/', 'user_slug': 'test',
                         'fetched_at': '2026-10-17T18:00:00+08:00', 'posts': [self.current]}
        sync.write(self.root / 'leetcode/sync_config.json', {'profile': self.snapshot['profile'], 'user_slug': 'test'})
        sync.write(self.root / 'leetcode/sources.json', {'profile': self.snapshot['profile'], 'sources': []})
        sync.write(self.cache / 'snapshot.json', self.snapshot)
        self.curation = self.cache / 'curation.json'
        sync.write(self.curation, {'status': 'reviewed', 'snapshot_fetched_at': self.snapshot['fetched_at'], 'entries': [spec()]})

    def build(self):
        sync.build(self.root, self.cache, self.curation)

    def tracked(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in (self.root / 'leetcode').rglob('*') if p.is_file()}

    def test_new_post_builds_exact_code_and_complete_inventory(self):
        self.build()
        notebook = sync.load(self.root / spec()['notebook'])
        original = next(c for c in notebook['cells'] if 'leetcode_source' in c['metadata'])
        self.assertEqual(''.join(original['source']), CODE)
        self.assertEqual(original['metadata']['leetcode_source']['sha256'], source.sha256(CODE))
        self.assertTrue(all(not c.get('outputs') for c in notebook['cells']))
        manifest = sync.load(self.root / 'leetcode/sources.json')
        self.assertEqual(manifest['coverage']['solutions'], 1)
        self.assertIn('no1.ipynb', (self.root / 'leetcode/README.md').read_text(encoding='utf-8'))

    def test_rerun_is_noop_and_does_not_change_notes(self):
        self.build()
        before = self.tracked()
        sync.write(self.curation, {'status': 'reviewed', 'snapshot_fetched_at': self.snapshot['fetched_at'], 'entries': []})
        self.build()
        self.assertEqual(before, self.tracked())

    def test_index_preserves_existing_local_contest_reviews(self):
        index = self.root / 'leetcode/README.md'
        local = '## 本地周赛复盘\n\n| 比赛 | 笔记 |\n| --- | --- |\n| 524 | [复盘](contests/local.md) |\n\n'
        index.write_text('# 力扣笔记\n\n' + local + '## 复用与校验\n旧说明\n', encoding='utf-8')
        self.build()
        result = index.read_text(encoding='utf-8')
        self.assertIn(local, result)
        self.assertEqual(result.count('## 本地周赛复盘'), 1)

    def test_new_updated_unchanged_missing_are_distinct(self):
        entries = []
        for identifier in ['same', 'changed', 'gone']:
            p = post(identifier)
            entries.append({**p, 'notebook': f'leetcode/{identifier}.ipynb'})
        snapshot = {'posts': [post('same'), post('changed', CODE + '\n'), post('new')]}
        plan = sync.compare(snapshot, {'sources': entries})
        self.assertEqual({key: [x['id'] for x in value] for key, value in plan.items()},
                         {'new': ['new'], 'updated': ['changed'], 'unchanged': ['same'], 'missing': ['gone']})

    def test_legacy_manifest_is_unchanged(self):
        old = {**post(), 'notebook': spec()['notebook']}
        del old['source_content_sha256']
        self.assertEqual(len(sync.compare(self.snapshot, {'sources': [old]})['unchanged']), 1)

    def test_updated_source_replaces_code_at_same_path(self):
        self.build()
        changed = post(code=CODE.replace('42', '43'))
        self.snapshot['posts'] = [changed]
        self.snapshot['fetched_at'] = '2026-10-18T18:00:00+08:00'
        sync.write(self.cache / 'snapshot.json', self.snapshot)
        edited = spec()
        edited['cells'][-1]['text'] = 'assert Solution().answer() == 43'
        sync.write(self.curation, {'status': 'reviewed', 'snapshot_fetched_at': self.snapshot['fetched_at'], 'entries': [edited]})
        self.build()
        notebook = sync.load(self.root / spec()['notebook'])
        original = next(c for c in notebook['cells'] if 'leetcode_source' in c['metadata'])
        self.assertEqual(''.join(original['source']), changed['blocks'][0]['code'])

    def test_draft_and_stale_snapshot_rejected_without_writes(self):
        for field, value in [('status', 'draft'), ('snapshot_fetched_at', 'old')]:
            curation = sync.load(self.curation)
            curation[field] = value
            sync.write(self.curation, curation)
            before = self.tracked()
            with self.assertRaises(ValueError):
                self.build()
            self.assertEqual(before, self.tracked())
            sync.write(self.curation, {'status': 'reviewed', 'snapshot_fetched_at': self.snapshot['fetched_at'], 'entries': [spec()]})

    def test_incomplete_duplicate_and_outside_paths_rejected(self):
        invalid = []
        one = spec()
        one['omissions'] = []
        invalid.append(one)
        two = spec()
        two['omissions'].append({'block': 0, 'reason': '重复'})
        invalid.append(two)
        invalid.extend([spec(path='../outside.ipynb'), spec(path='README.md'), spec(path='leetcode/a/../../outside.ipynb')])
        for item in invalid:
            sync.write(self.curation, {'status': 'reviewed', 'snapshot_fetched_at': self.snapshot['fetched_at'], 'entries': [item]})
            before = self.tracked()
            with self.assertRaises(ValueError):
                self.build()
            self.assertEqual(before, self.tracked())

    def test_missing_posts_do_not_delete_notebooks(self):
        self.build()
        self.snapshot['posts'] = []
        sync.write(self.cache / 'snapshot.json', self.snapshot)
        before = self.tracked()
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.build()
        self.assertEqual(before, self.tracked())

    def test_invalid_second_entry_does_not_write_first(self):
        self.snapshot['posts'].append(post('two'))
        sync.write(self.cache / 'snapshot.json', self.snapshot)
        broken = spec('two', 'leetcode/two.ipynb')
        broken['omissions'] = []
        sync.write(self.curation, {'status': 'reviewed', 'snapshot_fetched_at': self.snapshot['fetched_at'], 'entries': [spec(), broken]})
        before = self.tracked()
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(before, self.tracked())

    def test_markdown_and_slate_code_keep_whitespace(self):
        markdown = {'content': '说明\n\n```python\n' + CODE + '\n```\n'}
        self.assertEqual(source.extract_blocks(markdown)[0]['code'], CODE)
        slate = [{'type': 'CodeBlock', 'children': [{'language': 'python', 'children': [{'text': CODE[:10]}, {'text': CODE[10:]}]}]}]
        self.assertEqual(source.extract_blocks({'slateValue': json.dumps(slate)})[0]['code'], CODE)

    def test_public_listing_body_is_used_when_detail_is_unavailable(self):
        listed = {'id': 'one', 'kind': 'solution', 'slug': 'one', 'title': '示例',
                  'content': '```python\n' + CODE + '\n```', 'slateValue': None,
                  'contentFormat': 'MARKDOWN', 'author': {'username': 'test'},
                  'question': {'titleSlug': 'example'}}
        with patch.object(source, 'graphql', return_value={'solutionArticle': None}):
            current = source.fetch_post(listed, 'test')
            self.assertEqual(current['blocks'][0]['code'], CODE)
            self.assertEqual(current['author'], 'test')
            with self.assertRaisesRegex(ValueError, 'Unexpected author'):
                source.fetch_post(listed, 'another-user')
            with self.assertRaisesRegex(ValueError, 'identifier mismatch'):
                source.fetch_post({**listed, 'slug': 'another-post'}, 'test')
            with self.assertRaisesRegex(ValueError, 'Unavailable solution'):
                source.fetch_post({**listed, 'content': ''}, 'test')

    def test_submission_preserves_whitespace_and_detects_code_changes(self):
        import nbformat
        current = post()
        code = CODE + '\n    \n'
        current['contest'] = {'slug': 'weekly-contest-523', 'user_slug': 'test', 'submissions': [
            {'question': {'question_id': 42, 'title_slug': 'example', 'title': '示例'},
             'record': {'id': 123, 'status': 10, 'date': 1791686525},
             'detail': {'id': 456, 'lang': 'python3', 'code': code}}]}
        curated = spec()
        del curated['summary']
        curated['cells'].append({'type': 'submission', 'id': 456})
        notebook, entry = sync.make_notebook(current, curated, self.snapshot['fetched_at'])
        cells = {c.id: c for c in nbformat.reads(json.dumps(notebook), as_version=4).cells}
        cid = entry['submissions'][0]['cell_id']
        self.assertEqual(cells[cid].source, code)
        self.assertEqual(verifier.check_submissions(entry, cells, 'test'), {cid})
        with self.assertRaisesRegex(ValueError, 'owner mismatch'):
            verifier.check_submissions(entry, cells, 'someone-else')
        incomplete = copy.deepcopy(curated)
        incomplete['cells'].pop()
        with self.assertRaisesRegex(ValueError, 'Retain every accepted'):
            sync.make_notebook(current, incomplete, self.snapshot['fetched_at'])
        cells[cid].source = code.rstrip()
        with self.assertRaisesRegex(ValueError, 'Changed original'):
            verifier.check_submissions(entry, cells, 'test')

    def test_contest_submission_requires_matching_public_owner_and_identity(self):
        history = {'userContestRankingHistory': [{'attended': True, 'ranking': 149,
                    'contest': {'title': '第 523 场周赛'}}]}
        record = {'id': 123, 'submission_id': 456, 'status': 10, 'contest_id': 1421,
                  'data_region': 'CN', 'lang': 'python3'}
        ranking = {'total_rank': [{'user_slug': 'test', 'contest_id': 1421, 'data_region': 'CN'}],
                   'questions': [{'question_id': 42, 'title_slug': 'example', 'title': '示例'}],
                   'submissions': [{'42': record}]}
        detail = {'id': 456, 'code': CODE, 'lang': 'python3', 'contest_submission': 123}
        with patch.object(source, 'graphql', return_value=history), patch.object(source, 'public_json', side_effect=[ranking, detail]):
            contest = source.fetch_contest_submissions('weekly-contest-523', 'test')
            self.assertEqual(contest['submissions'][0]['detail']['code'], CODE)
        wrong_detail = {**detail, 'contest_submission': 999}
        with patch.object(source, 'graphql', return_value=history), patch.object(source, 'public_json', side_effect=[ranking, wrong_detail]):
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                source.fetch_contest_submissions('weekly-contest-523', 'test')
        ranking['total_rank'][0]['user_slug'] = 'someone-else'
        with patch.object(source, 'graphql', return_value=history), patch.object(source, 'public_json', return_value=ranking):
            with self.assertRaisesRegex(ValueError, 'User absent'):
                source.fetch_contest_submissions('weekly-contest-523', 'test')

    def test_all_solution_and_discussion_pages_are_read(self):
        solution = lambda slug: {'node': {'slug': slug, 'title': slug}}
        replies = [{'solutionArticles': {'edges': [solution('a')], 'pageInfo': {'hasNextPage': True}}},
                   {'solutionArticles': {'edges': [solution('b')], 'pageInfo': {'hasNextPage': False}}},
                   {'columnsPublishedContents': {'nodes': [{'uuid': 'c'}], 'nextToken': 'next'}},
                   {'columnsPublishedContents': {'nodes': [{'uuid': 'd'}], 'nextToken': None}}]
        with patch.object(source, 'graphql', side_effect=replies) as mocked:
            self.assertEqual([p['id'] for p in source.list_posts('test')], ['a', 'b', 'c', 'd'])
            self.assertEqual(mocked.call_args_list[1].args[1]['skip'], 1)
            self.assertEqual(mocked.call_args_list[3].args[1]['token'], 'next')

    def test_repeated_pagination_stops(self):
        page = {'solutionArticles': {'edges': [{'node': {'slug': 'a', 'title': 'a'}}], 'pageInfo': {'hasNextPage': True}}}
        with patch.object(source, 'graphql', side_effect=[page, copy.deepcopy(page)]):
            with self.assertRaisesRegex(ValueError, 'repeated'):
                source.list_posts('test')


if __name__ == '__main__':
    unittest.main()
