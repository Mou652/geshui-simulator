#!/usr/bin/env python3
"""同步个税官网与离职证明的导航和推荐入口"""

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def navigation(active):
    """生成可直接跳转的产品切换入口"""
    items = [('tax', '/', '个税模拟器'), ('leave', '/leave-certificate/', '离职证明')]
    links = []
    for key, href, label in items:
        current = ' aria-current="true"' if key == active else ''
        links.append(f'<a class="product-tab" href="{href}"{current}>{label}</a>')
    return '<nav class="product-tabs" aria-label="产品切换"><span class="product-tabs-label">演示工具</span>' + ''.join(links) + '</nav>'


def promotion(active):
    """展示另一款演示工具及其使用入口"""
    if active == 'tax':
        title, text, href, action = ('离职证明演示工具', '填写虚构资料、检查文档版式，授权后导出 PDF。', '/leave-certificate/', '查看离职证明')
    else:
        title, text, href, action = ('个人所得税模拟器', '了解安卓与 iPhone 演示版本，准备收入明细讲解、截图和录屏素材。', '/', '查看个税模拟器')
    return '<aside class="related-product" aria-label="相关演示工具"><div><span class="related-product-label">也可以了解</span><strong>' + title + '</strong><p>' + text + '</p></div><a class="related-product-action" href="' + href + '">' + action + ' <span aria-hidden="true">↗</span></a></aside>'


def unwrap(source, name, fallback=''):
    """移除上次生成的区块并保留原有联系方式"""
    pattern = re.compile(r'<!-- ' + name + r':start -->.*?<!-- ' + name + r':end -->', re.S)
    def replace(match):
        contact = re.search(r'<aside class="qq-bar".*?</aside>', match.group(), re.S)
        return contact.group() if contact else fallback
    return pattern.sub(replace, source)


def marked(name, html):
    """标记生成区块以支持重复同步"""
    return '<!-- ' + name + ':start -->' + html + '<!-- ' + name + ':end -->'


def update_page(source, path, surface='docs'):
    """为当前页面同步产品切换与可见推荐位"""
    active = 'leave' if surface != 'docs' or 'leave-certificate-' in path else 'tax'
    for name in ['product-navigation', 'product-promotion', 'product-footer']:
        source = unwrap(source, name)
    stylesheet = '<link rel="stylesheet" href="/assets/product-links.css">'
    if stylesheet not in source:
        source = source.replace('</head>', stylesheet + '\n</head>', 1)

    # 产品切换与原有联系方式共用吸顶区域
    contact = re.search(r'<aside class="qq-bar".*?</aside>', source, re.S)
    masthead = '<div class="product-navigation-shell">' + navigation(active)
    masthead += (contact.group() if contact else '') + '</div>'
    block = marked('product-navigation', masthead)
    if contact:
        source = source[:contact.start()] + block + source[contact.end():]
    elif surface == 'editor':
        source, count = re.subn(r'(<main class="app"[^>]*>)', lambda match: match.group() + block, source, count=1)
        assert count == 1, 'missing editor workspace'
    else:
        source = source.replace('<body>', '<body>' + block, 1)

    # 首页优先展示推荐，教程页在正文结束后继续引导
    block = marked('product-promotion', promotion(active))
    if surface == 'landing':
        anchor = '    <section class="showcase wide-container"'
        assert source.count(anchor) == 1
        source = source.replace(anchor, block + anchor, 1)
    elif surface == 'docs' and path == '/':
        source = source.replace('</h1>', '</h1>' + block, 1)
    elif surface == 'docs':
        source = source.replace('</main>', block + '</main>', 1)
    if surface != 'editor':
        footer = '<nav class="product-footer-links" aria-label="更多演示工具"><a href="/">个税模拟器官网</a><a href="/leave-certificate/">离职证明演示工具</a></nav>'
        source = source.replace('</footer>', marked('product-footer', footer) + '</footer>', 1)
    return source


def sync_docs():
    """同步所有静态说明页的产品入口"""
    files = sorted(DOCS.rglob('*.html'))
    for target in files:
        path = '/' + target.relative_to(DOCS).as_posix()
        if path.endswith('/index.html'):
            path = path.removesuffix('index.html')
        source = target.read_text(encoding='utf-8')
        updated = update_page(source, path)
        if source != updated:
            target.write_text(updated, encoding='utf-8')
    print('已同步', len(files), '个页面的双向产品入口')


def main():
    """同步官网，并按指定路径更新离职证明界面"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--leave-web', type=Path, help='离职证明项目的 web 目录')
    args = parser.parse_args()
    sync_docs()
    if args.leave_web:
        for filename, surface in [('index.html', 'landing'), ('editor.html', 'editor')]:
            target = args.leave_web / filename
            target.write_text(update_page(target.read_text(encoding='utf-8'), '/leave-certificate/' + filename, surface), encoding='utf-8')


if __name__ == '__main__':
    main()
