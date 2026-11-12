"""为二级页面同步统一的返回入口与样式"""
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def back_link(href='index.html', label='返回首页'):
    """生成可直接导航的返回链接"""
    return f'<a class="page-back" href="{href}" data-page-back><span class="page-back-icon" aria-hidden="true"><svg viewBox="0 0 20 20" fill="none"><path d="M15.5 10H4.5m0 0 5-5m-5 5 5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span>{label}</span></a>'


def sync_docs():
    """补齐非首页页面的返回入口，保留手工安排的位置"""
    changed = 0
    for target in sorted(DOCS.rglob('*.html')):
        if target == DOCS / 'index.html':
            continue
        source = target.read_text(encoding='utf-8')
        updated = source
        stylesheet = os.path.relpath(DOCS / 'assets/page-navigation.css', target.parent)
        if not re.search(r'<link\b[^>]*href=[\"\'][^\"\']*page-navigation\.css[\"\']', updated):
            updated = updated.replace('</head>', f'<link rel="stylesheet" href="{stylesheet}">\n</head>', 1)
        if 'data-page-back' not in updated:
            home = os.path.relpath(DOCS / 'index.html', target.parent)
            markup = '<!-- page-return:start --><div class="page-return">' + back_link(home) + '</div><!-- page-return:end -->'
            updated, count = re.subn(r'(<main\b[^>]*>)', lambda match: match[1] + markup, updated, count=1)
            if count != 1:
                raise ValueError(f'未找到页面主体：{target}')
        if updated != source:
            target.write_text(updated, encoding='utf-8')
            changed += 1
    return changed


if __name__ == '__main__':
    print(f'已同步 {sync_docs()} 个二级页面的返回入口')
