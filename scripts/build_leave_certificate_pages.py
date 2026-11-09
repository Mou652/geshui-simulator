#!/usr/bin/env python3
"""生成离职证明教程、阅读目录与搜索入口"""

import json
import re
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

import build_pages as shared


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
BASE = 'https://geshui.moujc.cn'
DATE = '2026-11-09'
PREFIX = '/guides/leave-certificate-'


def main():
    """从同一份说明生成网页、Markdown 和入口链接"""
    pages = json.loads((ROOT / 'content/leave-certificate-pages.json').read_text())
    fields = json.loads((ROOT / 'content/field-tables.json').read_text())
    links = [(PREFIX + p['slug'] + '.html', p['title']) for p in pages]
    for page, (path, title) in zip(pages, links):
        fields[path] = {'caption': title.split('：')[0] + '字段说明', 'rows': page['rows']}
    field_path = ROOT / 'content/field-tables.json'
    original = field_path.read_text()
    existing = json.loads(original)
    missing = {key: value for key, value in fields.items() if key not in existing}
    if missing:
        field_path.write_text(original.rstrip().removesuffix('}').rstrip() + ',\n' + json.dumps(missing, ensure_ascii=False, indent=2)[2:])
    shared.FIELD_TABLES = fields

    # 网页与 Markdown 共用正文和问答
    for page, (path, title) in zip(pages, links):
        canonical = BASE + path
        md_path = str(Path(path).with_suffix('.md'))
        graph = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'WebPage', '@id': canonical + '#page', 'url': canonical,
             'name': title, 'description': page['description'], 'inLanguage': 'zh-CN',
             'dateModified': DATE, 'about': {'@id': BASE + '/leave-certificate/#app'},
             'author': {'@type': 'Person', 'name': 'Mou652'}},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': '首页', 'item': BASE + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': '离职证明演示工具', 'item': BASE + '/leave-certificate/'},
                {'@type': 'ListItem', 'position': 3, 'name': title, 'item': canonical}]},
            {'@type': 'FAQPage', '@id': canonical + '#faq', 'mainEntity': [
                {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                for q, a in page['faq']]}
        ]}
        html = [shared.head(title, page['description'], canonical, json.dumps(graph, ensure_ascii=False), md_path),
                shared.header(), '<main id="main"><article>',
                '<p class="breadcrumb"><a href="/">首页</a> / <a href="/leave-certificate/">离职证明演示工具</a></p>',
                '<h1>' + escape(title) + '</h1>', '<p class="answer-block">' + escape(page['summary']) + '</p>',
                '<p class="byline">维护者：Mou652 · 资料核对：<time datetime="' + DATE + '">' + DATE + '</time></p>',
                '<p><a href="/leave-certificate/editor.html">打开在线演示工具</a> · <a href="/leave-certificate/">产品介绍与预览</a></p>']
        md = ['# ' + title, '', '> ' + page['summary'], '', '维护者：Mou652 · 核对：' + DATE,
              '', '[打开演示工具](' + BASE + '/leave-certificate/editor.html)', '']
        for heading, text in page['sections']:
            html += ['<h2>' + escape(heading) + '</h2><p>' + escape(text) + '</p>']
            md += ['## ' + heading, '', text, '']
        table_html, table_md = shared.field_table(path)
        html += [table_html, '<h2 id="faq">常见问题</h2>']
        md += [table_md, '', '## 常见问题', '']
        for q, a in page['faq']:
            html += ['<div class="faq-item"><h3>' + escape(q) + '</h3><p>' + escape(a) + '</p></div>']
            md += ['### ' + q, '', a, '']
        html += ['<h2>继续阅读</h2><ul>' + ''.join('<li>' + shared.link(p, t) + '</li>' for p, t in links if p != path) + '</ul>',
                 '<p>激活与使用咨询：<strong>QQ 2430239942</strong>。仅供虚构资料、版式研究与技术交流，演示文件不作为真实人事证明。</p>',
                 '</article></main>', shared.footer(), '</body></html>\n']
        md += ['## 继续阅读', ''] + ['- [' + t + '](' + BASE + p + ')' for p, t in links if p != path]
        md += ['', '激活与使用咨询：QQ 2430239942。仅供虚构资料和技术交流，演示文件不作为真实人事证明。', '']
        (DOCS / path.lstrip('/')).write_text('\n'.join(html))
        (DOCS / md_path.lstrip('/')).write_text('\n'.join(md))

    # 保留现有个税目录，追加独立的离职证明资料区
    block = '<!-- leave-certificate-guides:start -->\n<section aria-labelledby="leave-guides"><h2 id="leave-guides">离职证明演示工具教程</h2><ul>'
    block += ''.join('<li>' + shared.link(p, t) + '</li>' for p, t in links)
    block += '</ul></section>\n<!-- leave-certificate-guides:end -->'
    for filename in ['index.html', 'guides/index.html']:
        target = DOCS / filename
        source = target.read_text()
        source = re.sub(r'<!-- leave-certificate-guides:start -->.*?<!-- leave-certificate-guides:end -->\n?', '', source, flags=re.S)
        target.write_text(source.replace('</main>', block + '\n</main>'))

    # 站点地图只收录规范的公开说明页
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    tree = ET.parse(DOCS / 'sitemap.xml')
    root = tree.getroot()
    additions = {BASE + '/leave-certificate/'} | {BASE + p for p, _ in links}
    for node in root.findall('{*}url'):
        if node.find('{*}loc').text in additions | {BASE + '/', BASE + '/guides/'}:
            root.remove(node)
    for url in sorted(additions | {BASE + '/', BASE + '/guides/'}):
        node = ET.SubElement(root, '{' + namespace + '}url')
        ET.SubElement(node, '{' + namespace + '}loc').text = url
        ET.SubElement(node, '{' + namespace + '}lastmod').text = DATE
    ET.indent(tree, space='  ')
    tree.write(DOCS / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    urls = [node.text for node in root.findall('.//{*}loc')]
    (DOCS / 'sitemap.txt').write_text('\n'.join(urls) + '\n')
    (DOCS / 'leave-certificate-sitemap.xml').write_text('<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="' + namespace + '">\n' + ''.join('<url><loc>' + u + '</loc><lastmod>' + DATE + '</lastmod></url>\n' for u in sorted(additions)) + '</urlset>\n')

    llms = DOCS / 'llms.txt'
    source = re.sub(r'<!-- leave-certificate:start -->.*?<!-- leave-certificate:end -->\n?', '', llms.read_text(), flags=re.S)
    intro = '<!-- leave-certificate:start -->\n## 离职证明演示工具\n\n'
    intro += '离职证明是同一维护者提供的独立网页工具。用于虚构资料和版式演示，演示文件不作为真实人事证明。预览带提示水印，服务端授权 PDF 不叠加产品水印；一码一份，首次成功生成后24小时最多3个版本，同版重下不扣次数。授权与个税模拟器独立。获取条件咨询 QQ 2430239942。\n\n'
    intro += '- [产品介绍与预览](' + BASE + '/leave-certificate/): 在线演示工具、使用步骤与联系方式\n'
    intro += ''.join('- [' + t + '](' + BASE + str(Path(p).with_suffix('.md')) + '): 对应 HTML 教程的纯文本阅读版\n' for p, t in links)
    intro += '\n<!-- leave-certificate:end -->\n\n'
    llms.write_text(source.replace('## 项目资料', intro + '## 项目资料', 1))
    robots = DOCS / 'robots.txt'
    source = robots.read_text()
    sitemap_line = 'Sitemap: ' + BASE + '/leave-certificate-sitemap.xml'
    if sitemap_line not in source:
        robots.write_text(source.rstrip() + '\n' + sitemap_line + '\n')
    print('Generated', len(pages), 'guides, Markdown, 5 product sitemap URLs and AI directory')


if __name__ == '__main__':
    main()
