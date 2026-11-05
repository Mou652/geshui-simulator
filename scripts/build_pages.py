#!/usr/bin/env python3
"""从同一份内容生成教程正文、Markdown、FAQ 与结构化数据"""

import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
BASE = 'https://geshui.moujc.cn'
DATE = '2026-11-05'
ENTITY = '个税模拟器（Geshui Simulator）是 Mou652 维护的非官方个税界面教学演示工具，支持 Android 与 iPhone / iOS，使用本机虚构示例展示页面，配合系统截图与录屏制作教学素材，不连接官方税务系统。'


def absolute(url):
    return BASE + url if url.startswith('/') else url


def link(url, label):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def footer():
    return f'''<footer><p>{escape(ENTITY)}</p><p>维护者：{link('https://github.com/Mou652', 'Mou652')} · 版本咨询 QQ：2430239942</p><nav aria-label="页脚导航">{link('/about.html', '项目说明')} {link('/scope.html', '使用范围')} {link('/faq.html', '常见问题')} {link('/sitemap.xml', '站点地图')} {link('/llms.txt', 'llms.txt')} {link('https://github.com/Mou652/geshui-simulator/wiki', 'Wiki')} {link('https://github.com/Mou652/geshui-simulator/issues/1', '问答与反馈')} {link('https://github.com/Mou652/geshui-simulator/releases', '发布记录')}</nav></footer>'''


def header():
    return contact_bar() + f'''<a class="skip-link" href="#main">跳到正文</a><header><strong>{link('/', 'Mou652 · 个税模拟器')}</strong><nav aria-label="主导航">{link('/guides/', '全部教程')} {link('/android.html', '安卓版')} {link('/ios.html', 'iPhone 版')} {link('/faq.html', '常见问题')} {link('/about.html', '项目说明')}</nav></header>'''


def contact_bar():
    return '''<aside class="qq-bar" aria-label="QQ 联系方式"><div class="qq-bar-inner"><div class="qq-bar-copy"><span>演示版本与使用咨询</span><strong>QQ：<span data-qq-number>2430239942</span></strong></div><button class="qq-copy" type="button" data-copy-qq aria-label="复制 QQ 2430239942">复制 QQ</button><span class="qq-copy-status" role="status" aria-live="polite"></span></div></aside>'''


def graph(page, canonical):
    author = {'@type': 'Person', '@id': BASE + '/#maintainer', 'name': 'Mou652', 'url': 'https://github.com/Mou652'}
    website = {'@type': 'WebSite', '@id': BASE + '/#website', 'name': 'Mou652 个税模拟器', 'url': BASE + '/', 'inLanguage': 'zh-CN', 'publisher': {'@id': author['@id']}}
    webpage = {'@type': 'WebPage', '@id': canonical + '#page', 'url': canonical, 'name': page['h1'], 'description': page['summary'], 'inLanguage': 'zh-CN', 'dateModified': DATE, 'isPartOf': {'@id': website['@id']}, 'author': {'@id': author['@id']}}
    breadcrumb = {'@type': 'BreadcrumbList', '@id': canonical + '#breadcrumb', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': '个税模拟器', 'item': BASE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': '教程与使用说明', 'item': BASE + '/guides/'},
        {'@type': 'ListItem', 'position': 3, 'name': page['h1'], 'item': canonical},
    ]}
    result = [author, website, webpage, breadcrumb]
    if page['kind'] == 'Product':
        result.append({'@type': 'SoftwareApplication', '@id': BASE + '/#app', 'name': '个税模拟器', 'url': BASE + '/', 'operatingSystem': ['Android', 'iOS'], 'applicationCategory': 'EducationalApplication', 'description': ENTITY, 'maintainer': {'@id': author['@id']}})
        webpage['about'] = {'@id': BASE + '/#app'}
    elif page['kind'] == 'HowTo' and page['steps']:
        result.append({'@type': 'HowTo', '@id': canonical + '#howto', 'url': canonical, 'name': page['h1'], 'description': page['summary'], 'inLanguage': 'zh-CN', 'author': {'@id': author['@id']}, 'step': [
            {'@type': 'HowToStep', 'position': pos, 'name': name, 'text': text, 'url': canonical + f'#step-{pos}'}
            for pos, (name, text) in enumerate(page['steps'], 1)
        ]})
    elif page['kind'] != 'FAQPage':
        result.append({'@type': 'Article', '@id': canonical + '#article', 'headline': page['h1'], 'description': page['summary'], 'url': canonical, 'inLanguage': 'zh-CN', 'dateModified': DATE, 'author': {'@id': author['@id']}, 'mainEntityOfPage': {'@id': webpage['@id']}})
    if page['faq']:
        result.append({'@type': 'FAQPage', '@id': canonical + '#faq', 'url': canonical + '#faq', 'isPartOf': {'@id': webpage['@id']}, 'mainEntity': [
            {'@type': 'Question', 'name': question, 'acceptedAnswer': {'@type': 'Answer', 'text': answer}}
            for question, answer in page['faq']
        ]})
    return json.dumps({'@context': 'https://schema.org', '@graph': result}, ensure_ascii=False, indent=2).replace('</', '<\\/')


def head(title, description, canonical, schema, markdown=None):
    alternate = f'<link rel="alternate" type="text/markdown" href="{escape(markdown)}">' if markdown else ''
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}"><meta name="author" content="Mou652"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<link rel="canonical" href="{escape(canonical)}"><link rel="describedby" href="/llms.txt">{alternate}
<link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/content.css"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/contact.css"><script defer src="/assets/contact.js"></script>
<meta property="og:type" content="article"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="Mou652 个税模拟器"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{escape(canonical)}"><meta name="twitter:card" content="summary">
<script type="application/ld+json">{schema}</script></head><body>'''


def render(page, lookup):
    canonical = BASE + page['path']
    md_path = str(Path(page['path']).with_suffix('.md'))
    related = list(dict.fromkeys([item for item in page['related'] if item != page['id']] + [31, 34, 48]))
    label = {'official': '官方渠道指引', 'capture': '截图与录屏', 'demo': '本机演示与工具说明'}[page['audience']]
    if page['audience'] == 'official':
        note = '本页整理官方渠道的公开操作信息。实际业务以当前官方系统和适用政策为准；本站不是税务机关网站，不接收真实税务账号，不在本站办理申报。'
    else:
        note = '本页用于虚构资料的非官方教学演示。不同平台的入口与功能以对应版本说明为准；演示画面不能作为真实收入、纳税或身份材料。'
    toc = [('steps', '操作与核对步骤')] if page['steps'] else []
    toc += [(f'section-{pos}', section[0]) for pos, section in enumerate(page['sections'], 1)]
    if page['table']:
        toc.append(('comparison', '对照检查'))
    toc += [('faq', '常见问题'), ('sources', '资料来源'), ('related', '继续阅读')]
    parts = [head(page['title'], page['description'], canonical, graph(page, canonical), md_path), header(), '<main id="main"><article aria-labelledby="title">', f'<p class="breadcrumb">{link("/", "首页")} / {link("/guides/", "教程与使用说明")} / {escape(label)}</p>', f'<h1 id="title">{escape(page["h1"])}</h1>', f'<p class="answer-block"><strong>{escape(page["summary"])}</strong></p>', f'<p class="byline">维护者：Mou652 · 资料核对：<time datetime="{DATE}">{DATE}</time></p>', f'<p class="note">{escape(note)}</p>', '<nav class="toc" aria-label="本页目录"><strong>本页内容</strong><ol>' + ''.join(f'<li>{link("#" + ident, title)}</li>' for ident, title in toc) + '</ol></nav>']
    md = [f'# {page["h1"]}', '', f'> {page["summary"]}', '', f'维护者：Mou652 · 演示版本与使用咨询 QQ：2430239942 · 资料核对：{DATE}', '', note, '']
    if page['steps']:
        parts.append('<h2 id="steps">操作与核对步骤</h2><ol class="steps">')
        md += ['## 操作与核对步骤', '']
        for pos, (name, text) in enumerate(page['steps'], 1):
            parts.append(f'<li id="step-{pos}"><h3>{escape(name)}</h3><p>{escape(text)}</p></li>')
            md.append(f'{pos}. **{name}**：{text}')
        parts.append('</ol>')
        md.append('')
    for pos, (title, text) in enumerate(page['sections'], 1):
        parts.append(f'<h2 id="section-{pos}">{escape(title)}</h2><p>{escape(text)}</p>')
        md += [f'## {title}', '', text, '']
    if page['table']:
        columns, *rows = page['table']
        parts.append('<h2 id="comparison">对照检查</h2><div class="table-scroll" role="region" aria-label="对照检查表" tabindex="0"><table><thead><tr>' + ''.join(f'<th scope="col">{escape(value)}</th>' for value in columns) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(value)}</td>' for value in row) + '</tr>' for row in rows) + '</tbody></table></div>')
        md += ['## 对照检查', '', '| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join(['---'] * len(columns)) + ' |']
        md += ['| ' + ' | '.join(row) + ' |' for row in rows] + ['']
    if page.get('image'):
        image = '/images/' + page['image']
        alt = '个税模拟器的本机虚构示例画面，非官方模拟演示'
        parts.append(f'<figure><img src="{image}" width="1320" height="2868" loading="lazy" decoding="async" alt="{alt}"><figcaption>{alt}</figcaption></figure>')
        md += [f'![{alt}]({BASE + image})', '']
    parts.append('<h2 id="faq">常见问题</h2>')
    md += ['## 常见问题', '']
    for question, answer in page['faq']:
        parts.append(f'<div class="faq-item"><h3>{escape(question)}</h3><p>{escape(answer)}</p></div>')
        md += [f'### {question}', '', answer, '']
    parts.append('<h2 id="sources">资料来源</h2><ul>' + ''.join(f'<li>{link(absolute(url), name)}</li>' for name, url in page['sources']) + '</ul>')
    md += ['## 资料来源', ''] + [f'- [{name}]({absolute(url)})' for name, url in page['sources']] + ['']
    parts.append('<h2 id="related">继续阅读</h2><ul>' + ''.join(f'<li>{link(lookup[item]["path"], lookup[item]["h1"])}</li>' for item in related) + '</ul>')
    md += ['## 继续阅读', ''] + [f'- [{lookup[item]["h1"]}]({BASE + lookup[item]["path"]})' for item in related] + ['', ENTITY, '']
    parts.append('<aside class="contact"><span>演示版本与使用咨询</span><strong>QQ：2430239942</strong><span>说明安卓或 iPhone 机型、系统版本和演示目标</span></aside></article></main>')
    parts += [footer(), '</body></html>\n']
    target = DOCS / page['path'].lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(parts), encoding='utf-8')
    (DOCS / md_path.lstrip('/')).write_text('\n'.join(md), encoding='utf-8')


def build_index(pages):
    canonical = BASE + '/guides/'
    title = '个税教程与模拟演示：按问题查找使用说明'
    summary = '按收入查询、官方渠道、截图录屏、设备版本与工具选择查找教程。真实办税与本机虚构示例分别说明，先确认要完成的事情，再进入对应页面。'
    schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'url': canonical, 'inLanguage': 'zh-CN', 'mainEntity': {'@type': 'ItemList', 'itemListElement': [
        {'@type': 'ListItem', 'position': pos, 'name': page['h1'], 'url': BASE + page['path']} for pos, page in enumerate(pages, 1)
    ]}}
    parts = [head(title, summary, canonical, json.dumps(schema, ensure_ascii=False)), header(), '<main id="main"><section><h1>' + title + '</h1><p class="answer-block">' + summary + '</p><p>寻找具体问题，可使用浏览器的页面内查找。'+link('/llms.txt','阅读机器可读目录')+'。</p></section>']
    groups = [('收入查询与官方渠道', lambda p: p['audience'] == 'official'), ('截图、隐私与录屏', lambda p: p['audience'] == 'capture'), ('模拟器与设备版本', lambda p: 32 <= p['id'] <= 40), ('工具选择与常见问题', lambda p: p['id'] >= 41)]
    for name, predicate in groups:
        parts.append('<section><h2>' + name + '</h2><div class="guide-grid">')
        for page in pages:
            if predicate(page):
                parts.append('<div><h3>' + link(page['path'], page['h1']) + '</h3><p>' + escape(page['summary']) + '</p></div>')
        parts.append('</div></section>')
    parts += ['</main>', footer(), '</body></html>\n']
    (DOCS / 'guides/index.html').write_text('\n'.join(parts), encoding='utf-8')


def main():
    pages = json.loads((ROOT / 'content/pages.json').read_text())
    lookup = {page['id']: page for page in pages}
    lookup[31] = {'path': '/', 'h1': '个税模拟器首页'}
    for page in pages:
        render(page, lookup)
    build_index(pages)
    print(f'已生成 {len(pages)} 篇 HTML、对应 Markdown 与教程目录')


if __name__ == '__main__':
    main()
