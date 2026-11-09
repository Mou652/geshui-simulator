# 网站内容维护

`page-matrix.csv` 保留原规划的 50 个编号与路径，首页沿用既有页面，其余 49 篇由 `pages.json` 维护。

执行 `python3 scripts/build_pages.py` 生成 HTML、Markdown 与教程目录。正文、FAQ、HowTo 步骤和 JSON-LD 使用同一份内容，避免分别修改后产生差异。

`field-tables.json` 按正式 URL 维护全站的“字段、含义、常见误解”三列表。每页至少四行，内容对应当前页面主题；构建时同步生成 HTML 与对应 Markdown。原有手写页面使用 `field-table` 注释标记更新区域，重复构建不会叠加表格。窄屏下可在表格区域横向滚动，也可用键盘聚焦该区域。

更新文章时检查资料来源，修改实际核对日期，并同步站点地图和 `llms.txt`。页面没有实际步骤时不标记为 HowTo；没有可用搜索服务时不声明 SearchAction；不为个人维护项目虚构公司实体。

原始规划中的网页版、竞品实测排名、固定费用及全机型兼容性没有足够依据，已改为当前能力、工具类别比较和版本核对说明。真实办税页面引用税务机关资料；页面和结构化数据不承诺收录、排名或 AI 引用效果。

## 离职证明内容

`leave-certificate-pages.json` 维护四篇独立教程。先运行原有 `build_pages.py`，再运行 `python3 scripts/build_leave_certificate_pages.py`，同步教程、Markdown、首页入口、站点地图与 `llms.txt`。最后运行 `python3 scripts/sync_text_sitemap.py` 和 `python3 scripts/verify_pages.py`。

`/leave-certificate/` 由已有服务反代，入口 HTML 与编辑器元信息单独部署；编辑器使用 `noindex,follow`，仅产品说明与教程进入站点地图。FAQ 标记与可见问答一致，不承诺富结果、收录或 AI 引用。
