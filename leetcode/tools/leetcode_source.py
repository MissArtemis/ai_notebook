"""Read public LeetCode posts without browser state or login credentials."""

import hashlib
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def graphql(query, variables):
    request = Request('https://leetcode.cn/graphql/',
                      data=json.dumps({'query': query, 'variables': variables}).encode(),
                      headers={'Content-Type': 'application/json', 'User-Agent': 'ai-notebook-source-check/1.0'})
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')[:1000]
        raise RuntimeError(f'LeetCode HTTP {exc.code}: {detail}') from exc
    except URLError as exc:
        raise RuntimeError(f'LeetCode connection failed: {exc.reason}') from exc
    require(not result.get('errors'), f"GraphQL: {result.get('errors')}")
    require(result.get('data') is not None, 'LeetCode returned no data')
    return result['data']


def list_posts(user_slug):
    posts = []
    seen_ids = set()
    skip = 0
    while True:
        result = graphql('query($slug:String!,$skip:Int){solutionArticles(userSlug:$slug,skip:$skip,first:100){pageInfo{hasNextPage} edges{node{title slug createdAt status question{titleSlug translatedTitle questionFrontendId}}}}}',
                         {'slug': user_slug, 'skip': skip})['solutionArticles']
        page = [edge['node'] for edge in result['edges']]
        require(page or not result['pageInfo']['hasNextPage'], 'Solution pagination made no progress')
        for node in page:
            require(node['slug'] not in seen_ids, 'Solution pagination repeated a post')
            seen_ids.add(node['slug'])
            posts.append({'id': node['slug'], 'kind': 'solution', **node})
        skip += len(page)
        if not result['pageInfo']['hasNextPage']:
            break
    token = None
    seen_tokens = set()
    while True:
        result = graphql('query($slug:String!,$token:ID){columnsPublishedContents(userSlug:$slug,nextToken:$token){nodes{__typename ... on QAQuestionNode{uuid title createdAt status} ... on ColumnArticleNode{uuid title createdAt status}} nextToken}}',
                         {'slug': user_slug, 'token': token})['columnsPublishedContents']
        for node in result['nodes']:
            require(node.get('uuid'), f'Unknown discussion type: {node}')
            require(node['uuid'] not in seen_ids, 'Discussion pagination repeated a post')
            seen_ids.add(node['uuid'])
            posts.append({'id': node['uuid'], 'kind': 'discussion', **node})
        token = result['nextToken']
        if token is None:
            break
        require(token not in seen_tokens, 'Discussion pagination repeated a token')
        seen_tokens.add(token)
    return posts


def flatten(node):
    return node.get('text', '') + ''.join(flatten(child) for child in node.get('children', []))


def extract_blocks(article):
    if article.get('slateValue'):
        return [{'language': tab.get('language') or 'plainText', 'code': flatten(tab)}
                for node in json.loads(article['slateValue']) if node.get('type') == 'CodeBlock'
                for tab in node['children']]
    # Keep code exactly as written between Markdown fences, including trailing blank lines.
    text = article.get('content') or ''
    pattern = r'^(`{3,}|~{3,})([^\n]*)\n(.*?)\n\1[ \t]*(?=\n|$)'
    return [{'language': m.group(2).strip(), 'code': m.group(3)}
            for m in re.finditer(pattern, text, re.MULTILINE | re.DOTALL)]


def fetch_post(post, user_slug):
    if post['kind'] == 'solution':
        article = graphql('query($slug:String!){solutionArticle(slug:$slug){title slug content slateValue contentFormat author{username} question{titleSlug translatedTitle questionFrontendId}}}',
                          {'slug': post['id']})['solutionArticle']
        require(article is not None, f"Unavailable solution: {post['id']}")
        author = article['author']['username']
        url = f"https://leetcode.cn/problems/{article['question']['titleSlug']}/solution/{post['id']}/"
    else:
        require(post.get('__typename', 'QAQuestionNode') == 'QAQuestionNode',
                f"Unsupported discussion type {post.get('__typename')}; inspect its public page and adapt the reader before continuing")
        article = graphql('query($uuid:ID!){qaQuestion(uuid:$uuid){title content slateValue contentFormat contentAuthor{userSlug}}}',
                          {'uuid': post['id']})['qaQuestion']
        require(article is not None, f"Unavailable discussion: {post['id']}")
        author = article['contentAuthor']['userSlug']
        url = f"https://leetcode.cn/discuss/post/{post['id']}/"
    require(author == user_slug, f"Unexpected author for {post['id']}: {author}")
    body = article.get('slateValue') or article.get('content') or ''
    require(body.strip(), f"Empty/unreadable public content: {post['id']}")
    fingerprint = json.dumps({'title': article['title'], 'format': article.get('contentFormat'), 'body': body},
                             ensure_ascii=False, sort_keys=True)
    return {'id': post['id'], 'kind': post['kind'], 'title': article['title'], 'url': url,
            'author': author, 'listing': post, 'article': article,
            'source_content_sha256': sha256(fingerprint),
            'source_slate_sha256': sha256(article['slateValue']) if article.get('slateValue') else None,
            'blocks': extract_blocks(article)}


def reading_text(post):
    """Produce a local reading copy; original nodes remain in the JSON snapshot."""
    article = post['article']
    if not article.get('slateValue'):
        return article.get('content') or ''
    lines = []
    for node in json.loads(article['slateValue']):
        if node.get('type') == 'CodeBlock':
            for tab in node['children']:
                lines.append('```' + tab.get('language', '') + '\n' + flatten(tab) + '\n```')
        else:
            heading = '### ' if node.get('type', '').startswith('Heading') else ''
            lines.append(heading + flatten(node))
    return '\n\n'.join(lines)
