#!/usr/bin/env python3
"""按现有 XML 站点地图同步纯文本入口，更新 XML 后运行本脚本"""

import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit


def main():
    """校验主站规范网址并导出 UTF-8 纯文本地图"""
    docs = Path(__file__).resolve().parents[1] / 'docs'
    urls = [node.text for node in ET.parse(docs / 'sitemap.xml').findall('.//{*}loc')]
    if not urls or len(urls) != len(set(urls)):
        raise ValueError('站点地图为空或存在重复网址')
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc != 'geshui.moujc.cn':
            raise ValueError('站点地图包含主站以外的网址')
        if parsed.query or parsed.fragment or any(ch.isspace() for ch in url):
            raise ValueError('站点地图包含非规范网址')
        target = docs / parsed.path.lstrip('/')
        if not parsed.path or parsed.path.endswith('/'):
            target /= 'index.html'
        if target.suffix != '.html' or not target.is_file():
            raise ValueError('站点地图网址没有对应的 HTML 页面')
    output = docs / 'sitemap.txt'
    output.write_text('\n'.join(urls) + '\n', encoding='utf-8')
    print(f'已同步 {len(urls)} 个主站网址到 {output.name}')


if __name__ == '__main__':
    main()
