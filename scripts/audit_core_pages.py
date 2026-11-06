#!/usr/bin/env python3
"""核对核心页面的搜索入口与规范网址，支持读取部署后的正式站"""

import argparse
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser


ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://geshui.moujc.cn'
AGENTS = ['Baiduspider', 'bingbot', 'Googlebot']


class Page(HTMLParser):
    """提取页面标题、搜索摘要和规范网址"""

    def __init__(self, source):
        super().__init__()
        self.title = ''
        self.h1 = []
        self.description = []
        self.canonical = []
        self.robots = []
        self.active = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.active = 'title'
        elif tag == 'h1':
            self.active = 'h1'
            self.h1.append('')
        elif tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs.get('href', ''))
        elif tag == 'meta' and attrs.get('name') == 'description':
            self.description.append(attrs.get('content', ''))
        elif tag == 'meta' and attrs.get('name', '').lower() in ['robots', 'baiduspider', 'bingbot', 'googlebot']:
            self.robots.append(attrs.get('content', ''))

    def handle_endtag(self, tag):
        if tag in ['title', 'h1']:
            self.active = None

    def handle_data(self, text):
        if self.active == 'title':
            self.title += text
        elif self.active == 'h1':
            self.h1[-1] += text


def read_resource(path, live):
    """读取正式站响应或本地发布文件"""
    address = BASE + path
    if live:
        request = Request(address, headers={'User-Agent': 'Mou652-Core-SEO-Audit/1.0'})
        with urlopen(request, timeout=20) as response:
            return response.read().decode('utf-8'), response.status, response.url, dict(response.headers)
    target = ROOT / 'docs' / path.lstrip('/')
    if path.endswith('/'):
        target /= 'index.html'
    return target.read_text(encoding='utf-8'), 200, address, {}


def audit_page(page, live, robots, sitemap_urls):
    """核对一个核心页面的标题、收录限制与关键词职责"""
    address = BASE + page['path']
    try:
        source, status, final_url, headers = read_resource(page['path'], live)
        parsed = Page(source)
        directives = ','.join(parsed.robots + [value for key, value in headers.items() if key.lower() == 'x-robots-tag']).lower()
        checks = {
            'http_200': status == 200,
            'no_redirect': final_url == address,
            'title': parsed.title == page['title'],
            'single_h1': parsed.h1 == [page['h1']],
            'description': parsed.description == [page['description']],
            'canonical': parsed.canonical == [address],
            'index_allowed': 'noindex' not in directives and 'none' not in directives,
            'follow_allowed': 'nofollow' not in directives and 'none' not in directives,
            'primary_keyword': page['keyword'] in parsed.title and page['keyword'] in parsed.h1[0],
            'sitemap': address in sitemap_urls,
            'html_content_type': not live or 'text/html' in next((value for key, value in headers.items() if key.lower() == 'content-type'), ''),
        }
        checks.update({agent + '_allowed': robots.can_fetch(agent, address) for agent in AGENTS})
        return {'url': address, 'keyword': page['keyword'], 'intent': page['intent'], 'checks': checks, 'passed': all(checks.values())}
    except Exception as exc:
        return {'url': address, 'error': str(exc), 'passed': False}


def main():
    """汇总核心页面与两种站点地图的检查结果"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='检查正式站而非本地文件')
    parser.add_argument('--output', type=Path, help='保存完整JSON核查结果')
    args = parser.parse_args()
    config = json.loads((ROOT / 'content/core-pages.json').read_text(encoding='utf-8'))
    robots_text, _, _, _ = read_resource('/robots.txt', args.live)
    robots = RobotFileParser()
    robots.parse(robots_text.splitlines())
    xml, _, _, _ = read_resource('/sitemap.xml', args.live)
    sitemap_urls = [node.text for node in ET.fromstring(xml).findall('.//{*}loc')]
    plain, _, _, _ = read_resource('/sitemap.txt', args.live)
    map_checks = {
        'xml_txt_same_urls': sitemap_urls == plain.splitlines(),
        'unique_urls': len(sitemap_urls) == len(set(sitemap_urls)),
        'robots_declares_both': set(robots.site_maps() or []) == {BASE + '/sitemap.xml', BASE + '/sitemap.txt'},
    }
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda page: audit_page(page, args.live, robots, sitemap_urls), config['pages']))
    passed = all(map_checks.values()) and all(item['passed'] for item in results)
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'mode': 'live' if args.live else 'local', 'sitemap_checks': map_checks, 'sitemap_urls': len(sitemap_urls), 'pages': results, 'result': 'passed' if passed else 'failed'}
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
