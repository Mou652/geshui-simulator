"""从本地产品资料同步展示配置，不重建已修改的页面"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
config = json.loads((ROOT / 'content/promo-site.json').read_text(encoding='utf-8'))
target = ROOT / 'docs/assets/promo/config.js'
target.write_text('window.MOU_PROMO_CONFIG = ' + json.dumps(config, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'已同步 {len(config["promo_content"]["products"])} 个品类，不含安装包下载地址')
