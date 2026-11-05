#!/usr/bin/env python3
"""核对成品页面的链接、正文、结构化数据与发布目录"""

import csv
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
BASE = 'https://geshui.moujc.cn'


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def text(self):
        return ''.join(child.text() if isinstance(child, Node) else child for child in self.children)

    def find(self, tag=None, **attrs):
        found = []
        if (tag is None or self.tag == tag) and all(self.attrs.get(key) == value for key, value in attrs.items()):
            found.append(self)
        for child in self.children:
            if isinstance(child, Node):
                found.extend(child.find(tag, **attrs))
        return found


class Parser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append(node)

    def handle_endtag(self, tag):
        for pos in range(len(self.stack) - 1, 0, -1):
            if self.stack[pos].tag == tag:
                self.stack = self.stack[:pos]
                break

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def site_path(file):
    path = '/' + str(file.relative_to(DOCS))
    return path[:-10] if path.endswith('index.html') else path


def resolve(url):
    parsed = urlsplit(url)
    target = DOCS / unquote(parsed.path).lstrip('/')
    return target / 'index.html' if target.is_dir() else target


def main():
    pages = json.loads((ROOT / 'content/pages.json').read_text())
    files = sorted(DOCS.rglob('*.html'))
    trees = {file: Parser(file.read_text()).root for file in files}
    expected_urls = {BASE + site_path(file) for file in files}
    titles = []
    links = 0
    for file, tree in trees.items():
        prefix = str(file.relative_to(ROOT))
        title = tree.find('title')
        assert len(title) == 1 and title[0].text().strip(), prefix + ': title'
        titles.append(title[0].text())
        assert len(tree.find('h1')) == 1, prefix + ': h1'
        assert tree.find('meta', name='description'), prefix + ': description'
        canonical = tree.find('link', rel='canonical')
        assert len(canonical) == 1 and canonical[0].attrs['href'] == BASE + site_path(file), prefix + ': canonical'
        for node in tree.find():
            for attr in ['href', 'src']:
                if not node.attrs.get(attr):
                    continue
                url = urljoin(BASE + site_path(file), node.attrs[attr])
                parsed = urlsplit(url)
                if parsed.netloc != 'geshui.moujc.cn':
                    continue
                target = resolve(url)
                assert target.is_file(), f'{prefix}: missing {url}'
                if parsed.fragment and target.suffix == '.html':
                    assert trees[target].find(id=unquote(parsed.fragment)), f'{prefix}: missing anchor {url}'
                links += 1
        for script in tree.find('script', type='application/ld+json'):
            json.loads(script.text())
    assert len(titles) == len(set(titles)), 'Duplicate page titles'
    faq_count = 0
    howto_count = 0
    for page in pages:
        file = DOCS / page['path'].lstrip('/')
        tree = trees[file]
        data = json.loads(tree.find('script', type='application/ld+json')[0].text())['@graph']
        faq = next(node for node in data if node['@type'] == 'FAQPage')
        visible = tree.find('div', **{'class': 'faq-item'})
        actual_faq = [(item.find('h3')[0].text(), item.find('p')[0].text()) for item in visible]
        structured_faq = [(item['name'], item['acceptedAnswer']['text']) for item in faq['mainEntity']]
        assert actual_faq == structured_faq, page['path'] + ': FAQ differs'
        faq_count += len(actual_faq)
        howto = [node for node in data if node['@type'] == 'HowTo']
        if howto:
            for pos, step in enumerate(howto[0]['step'], 1):
                visible_step = tree.find('li', id=f'step-{pos}')[0]
                assert visible_step.find('h3')[0].text() == step['name']
                assert visible_step.find('p')[0].text() == step['text']
                howto_count += 1
        assert not any(node.get('@type') in ('Organization', 'SearchAction') for node in data)
        assert file.with_suffix('.md').is_file()
    with (ROOT / 'content/page-matrix.csv').open() as handle:
        matrix = list(csv.DictReader(handle))
    assert len(matrix) == 50 and len({row['URL路径'] for row in matrix}) == 50
    assert all(resolve(BASE + row['URL路径']).is_file() for row in matrix)
    sitemap = ET.parse(DOCS / 'sitemap.xml')
    urls = [node.text for node in sitemap.findall('.//{*}loc')]
    assert len(urls) == len(set(urls))
    assert set(urls) == expected_urls, ('Sitemap mismatch', expected_urls.symmetric_difference(urls))
    for url in re.findall(r'\]\((https://geshui\.moujc\.cn/[^)]*)\)', (DOCS / 'llms.txt').read_text()):
        assert resolve(url).is_file(), 'llms: ' + url
    robots = RobotFileParser()
    robots.parse((DOCS / 'robots.txt').read_text().splitlines())
    agents = ['Bytespider','Baiduspider','GPTBot','OAI-SearchBot','ChatGPT-User','ClaudeBot','Claude-SearchBot','Claude-User','PerplexityBot','Perplexity-User','Googlebot','bingbot']
    for agent in agents:
        for path in ['/', '/llms.txt', '/guides/income-detail-lookup.html', '/guides/income-detail-lookup.md']:
            assert robots.can_fetch(agent, BASE + path), (agent, path)
    print(json.dumps({'html_pages':len(files),'matrix_entries':len(matrix),'new_articles':len(pages),'local_links':links,'matching_faq_answers':faq_count,'matching_howto_steps':howto_count,'sitemap_urls':len(urls),'crawler_agents_verified':len(agents),'result':'passed'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
