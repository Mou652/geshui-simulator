# 个人所得税模拟器 · 个税模拟器 · 个税 App 模拟器（Personal Income Tax Simulator）

这款非官方个税 App 模拟器涵盖 Android（安卓）和 iPhone（iOS）演示版本，用虚构资料展示年度查询、工资薪金与收入纳税明细。

想在手机上体验**仿个税 App 界面模拟器**，可以用这款**个税模拟软件**按年度查看示例收入，再点开某个月的工资明细。

**China Personal Income Tax App Simulator** is an independent UI demo for Android and iPhone (iOS). It uses fictional data to demonstrate annual queries and income details. The demo does not connect to tax accounts or file returns.

[Android 安卓安装与激活说明](https://geshui.moujc.cn/install_guide.html) · [iPhone / iOS 版本与操作说明](docs/ios.md)

[个人所得税模拟器中文介绍](https://geshui.moujc.cn/personal-income-tax-simulator.html) · [英文介绍 / English overview](https://geshui.moujc.cn/en/personal-income-tax-simulator.html) · [Gitee 镜像](https://gitee.com/MouJC/geshui-simulator)

演示版本与安装咨询请联系 QQ **2430239942**，并注明 Android 或 iPhone 机型和系统版本。

## 功能亮点

| 演示内容 | 操作入口与结果 |
| --- | --- |
| 设置虚构资料 | 在对应版本的资料设置入口填写演示姓名、任职单位、年度和月收入 |
| 年度收入纳税明细 | 从首页或「办&查」进入「收入纳税明细查询」，选择年度与所得类型，查看收入合计和预扣税额合计 |
| 月度工资薪金 | 打开查询结果中的月份记录，查看单笔收入纳税明细 |
| 个人中心 | 在「我的」查看演示个人资料和任职受雇等页面 |

## 界面预览

下方展示收入明细、年度筛选、单笔详情、首页和个人中心。画面中的资料及金额为演示示例。

<table>
  <tr>
    <th align="center">收入纳税明细 · 模拟演示</th>
    <th align="center">年度与所得类型 · 模拟演示</th>
    <th align="center">明细详情 · 安卓虚构示例</th>
  </tr>
  <tr>
    <td align="center"><img src="screenshots/income-preview.png?v=b00858e8c889" width="300" alt="个税模拟器：收入汇总与月度收入列表，数值为演示数据"></td>
    <td align="center"><img src="docs/images/demo-query.png?v=bdfc8d061cb8" width="300" alt="个税模拟器：年度选择与所得类型筛选"></td>
    <td align="center"><img src="docs/images/android-income-detail.png?v=5ccd43504874" width="300" alt="安卓个税模拟器：虚构收入纳税明细详情"></td>
  </tr>
</table>

<table>
  <tr>
    <th align="center">首页 · 模拟演示</th>
    <th align="center">我的 · 模拟演示</th>
  </tr>
  <tr>
    <td align="center"><img src="docs/images/demo-home.png?v=ffacd70dc6c0" width="300" alt="个税模拟器：首页功能入口与底部导航"></td>
    <td align="center"><img src="docs/images/demo-mine.png" width="300" alt="个税模拟器：个人中心及已遮罩的演示识别号"></td>
  </tr>
</table>

## 快速开始

1. **确认适用版本**。Android 用户可查看安装与激活说明，iPhone 用户可查看 iOS 版本说明并向维护者确认获取方式。
2. **准备一组虚构资料**。按[演示资料设置教程](docs/guides/configure-demo-data.md)填写年度、月份和工资，预览后保存。
3. **查询并核对月度记录**。按[收入纳税明细教程](docs/guides/income-details-demo.md)选择已保存数据的年度与所得类型，再查看汇总和单笔明细。

## 常见问题

### 个税模拟器 GitHub 仓库在哪里？

Mou652 维护的个税模拟器 GitHub 仓库是 [Mou652/individual-income-tax-simulator](https://github.com/Mou652/individual-income-tax-simulator)。仓库提供 Android 与 iPhone / iOS 的项目介绍、版本说明和操作教程。完整功能与教程入口见 [项目资料](repository/about.md)，演示版本可通过 QQ **2430239942** 咨询。

### 个人所得税模拟器 App 有什么功能？

这款 App 可以用虚构资料演示个税查询。选择年度和所得类型后，可以查看年度收入合计、每月工资薪金和单笔收入纳税明细。演示数据保存在本机。

可设置示例姓名、任职单位、收入年度、月份范围和月收入，也可选择是否包含年终奖，以及个人中心展示的家庭成员和银行卡数量。设置步骤见 [资料设置教程](https://geshui.moujc.cn/guides/configure-demo-data.html)。

### 个人所得税模拟器和个税计算器有什么区别？

这里的模拟器侧重个税 App 的界面、资料和查询流程演示；个税计算器通常侧重税额计算。本项目展示的收入与税额不作为真实报税计算或纳税判断的依据。

### 个人所得税 App 模拟器能查询真实的个税记录吗？

不会。模拟器用于本地界面与数据演示，不连接官方税务系统，不办理申报、退税或证明开具等真实业务。

## 项目说明

- [安卓版设备与版本说明](repository/android.md) · [iPhone / iOS 版本与操作说明](docs/ios.md) · [个税工具对比与使用场景](repository/alternatives.md)
- [国内阅读入口和中文教程](GITEE.md) · [使用问题排查](docs/guides/troubleshooting.md)
- [产品官网](https://geshui.moujc.cn/) · [GitHub Issues](https://github.com/Mou652/individual-income-tax-simulator/issues) · [资料发布记录](https://github.com/Mou652/individual-income-tax-simulator/releases)
- [离职证明演示工具](https://github.com/Mou652/leave-certificate-demo)是独立项目，用于虚构资料的版式预览。

## 许可证

本仓库中由维护者原创的文档、网站代码与维护脚本采用 [MIT License](LICENSE)。引用的第三方资料、界面截图中的第三方标识及素材不在此授权范围内，相关权利归各自权利人所有。

本许可不涉及仓库外的 Android / iOS App 源码、安装包、激活服务或账号。资料版发行标签不代表 App 版本号。
