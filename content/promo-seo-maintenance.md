# 产品搜索入口维护

主站以个税模拟器与个人所得税界面演示为核心，收入纳税明细、资料设置、安卓安装、截图和个税录屏分别链接现有说明页。离职证明与图片处理服务使用独立详情页。

产品配置位于 `promo-site.json`。每个产品的 `seo_path`、`seo_title`、`seo_h1`、`seo_description` 分别维护规范路径、站点标题、正文标题和摘要；内容必须对应当前可用功能与可见正文。

修改配置或详情模板后执行：

```sh
python3 scripts/build_promo_seo.py
python3 scripts/sync_text_sitemap.py
python3 scripts/verify_pages.py
```

其他页面有实际重要更新时，通过 `--changed` 同步其修改日期，例如：

```sh
python3 scripts/build_promo_seo.py --changed / --changed install_guide.html
```

生成器会同步静态产品正文、运行时配置和站点地图。未变化的产品页不会刷新修改日期。首页使用 WebSite、Person 和页面目录结构，不虚构公司、评价或搜索服务。

`pay.html` 与旧参数详情模板 `promo-detail.html` 使用 `noindex,follow`，不进入站点地图。旧详情参数仍可使用；产品链接指向各自静态页面，保留各产品独立正文。

主站产品页和安装指南覆盖 Android 安卓与 iPhone（iOS）。区分安卓 APK 和 iPhone 描述文件，并注明两端都需要激活码。图片处理中的个税、社保场景仅描述虚构演示素材的清晰度、裁剪、排版与隐私打码等需求。

发布通过现有 main 分支与官网同步服务完成。IndexNow 工作流返回 200 或 202 仅代表通知接收，Google、百度等后台的提交回执也不代表已收录或排名提升。

首页保留“灵活就业指导”品牌展示，浏览器标题和摘要说明个税模拟器、安卓与 iPhone 安装及教学用途。产品详情页的 `seo_title` 继续按各自配置维护。中英文个税专题互设 `hreflang`，各自使用本页规范网址。
