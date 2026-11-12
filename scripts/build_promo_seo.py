#!/usr/bin/env python3
"""从现有产品资料生成可直接抓取的详情页并同步站点地图"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
BASE = 'https://geshui.moujc.cn/'


def article_html(node):
    """将产品文档转换为首屏可读取的介绍与图片"""
    kind = node.get('type')
    attrs = node.get('attrs', {})
    if kind == 'text':
        return escape(node.get('text', ''))
    children = ''.join(article_html(child) for child in node.get('content', []))
    if kind == 'heading':
        level = min(3, max(2, int(attrs.get('level', 2))))
        return f'<h{level}>{children}</h{level}>'
    if kind == 'paragraph':
        return '<p>' + children + '</p>'
    if kind == 'image':
        return ('<figure><img loading="lazy" src="' + escape(attrs['src'], quote=True)
                + '" alt="' + escape(attrs.get('alt', ''), quote=True) + '"><figcaption>'
                + escape(attrs.get('caption', '')) + '</figcaption></figure>')
    return children


def set_text(source, element_id, text):
    """替换详情模板中指定业务字段的初始正文"""
    pattern = r'(<[a-z0-9]+\b[^>]*\bid="' + element_id + r'"[^>]*>).*?(</[a-z0-9]+>)'
    result, count = re.subn(pattern, lambda match: match[1] + escape(text) + match[2], source, count=1, flags=re.S)
    if count != 1:
        raise ValueError('详情模板缺少字段：' + element_id)
    return result


def main():
    """生成产品规范页面并保留未修改教程的更新时间"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--changed', action='append', default=[], help='本次实际修改的其他页面路径')
    args = parser.parse_args()
    updated = {BASE + path.lstrip('/') for path in args.changed}
    config = json.loads((ROOT / 'content/promo-site.json').read_text(encoding='utf-8'))
    products = config['promo_content']['products']
    template = (DOCS / 'promo-detail.html').read_text(encoding='utf-8')
    for product in products:
        canonical = BASE + product['seo_path']
        source = re.sub(r'<title>.*?</title>', '<title>' + escape(product['seo_title']) + '</title>', template)
        source = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="' + escape(product['seo_description'], quote=True) + '">', source)
        source = re.sub(r'\s*<meta name="robots"[^>]*>', '', source)
        source = re.sub(r'<link rel="canonical"[^>]*>', '<link rel="canonical" href="' + canonical + '">', source)
        source = source.replace('<body class="detail-page">', '<body class="detail-page" data-product-id="' + product['id'] + '">')
        source = source.replace('id="detailContent" hidden', 'id="detailContent"').replace('id="detailState" class=', 'id="detailState" hidden class=')
        for field, value in [('detailTitle', product['seo_h1']), ('crumbProduct', product['title']), ('detailDescription', product['seo_description']), ('detailPrice', f"¥ {product['price_cny']} 元"), ('detailCategory', product['category'] + ' · ' + product['platform_label'])]:
            source = set_text(source, field, value)
        source = source.replace('<article id="detailArticle" class="rich-article"></article>', '<article id="detailArticle" class="rich-article">' + article_html(product['details_doc']) + '</article>')
        source = source.replace('请开启 JavaScript 查看产品介绍，或', '产品介绍可直接阅读；开启 JavaScript 可使用图片预览及咨询按钮，也可')
        entity = {'@type': 'SoftwareApplication' if product['id'] == 'tax' else 'Service', '@id': canonical + '#product', 'name': product['seo_h1'], 'description': product['seo_description'], 'url': canonical, 'image': BASE + product['image_url'], 'offers': {'@type': 'Offer', 'price': product['price_cny'], 'priceCurrency': 'CNY', 'url': canonical}}
        if product['id'] == 'tax':
            entity.update(operatingSystem='Android', applicationCategory='EducationalApplication')
        graph = {'@context': 'https://schema.org', '@graph': [entity, {'@type': 'WebPage', '@id': canonical + '#page', 'name': product['seo_title'], 'url': canonical, 'description': product['seo_description'], 'mainEntity': {'@id': entity['@id']}, 'isPartOf': {'@id': BASE + '#website'}}, {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': '灵活就业指导', 'item': BASE}, {'@type': 'ListItem', 'position': 2, 'name': product['seo_h1'], 'item': canonical}]}]}
        social = '<meta property="og:type" content="website"><meta property="og:title" content="' + escape(product['seo_title'], quote=True) + '"><meta property="og:description" content="' + escape(product['seo_description'], quote=True) + '"><meta property="og:url" content="' + canonical + '"><meta property="og:image" content="' + BASE + product['image_url'] + '">'
        source = source.replace('</head>', social + '\n<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False).replace('</', '<\\/') + '</script>\n</head>')
        target = DOCS / product['seo_path']
        if not target.exists() or target.read_text(encoding='utf-8') != source:
            target.write_text(source, encoding='utf-8')
            updated.add(canonical)

    # 保持运行时产品资料与静态正文一致
    (DOCS / 'assets/promo/config.js').write_text('window.MOU_PROMO_CONFIG = ' + json.dumps(config, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    sitemap = ET.parse(DOCS / 'sitemap.xml')
    root = sitemap.getroot()
    for entry in list(root):
        if entry.findtext('{*}loc') in {BASE + 'pay.html', BASE + 'promo-detail.html'}:
            root.remove(entry)
    known = {entry.findtext('{*}loc'): entry for entry in root}
    for url in sorted(updated):
        entry = known.get(url)
        if entry is None:
            entry = ET.SubElement(root, '{' + namespace + '}url')
            ET.SubElement(entry, '{' + namespace + '}loc').text = url
        modified = entry.find('{*}lastmod')
        if modified is None:
            modified = ET.SubElement(entry, '{' + namespace + '}lastmod')
        modified.text = datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    ET.indent(sitemap, space='  ')
    sitemap.write(DOCS / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    print('已生成 4 个静态产品详情页并同步站点地图')


if __name__ == '__main__':
    main()
