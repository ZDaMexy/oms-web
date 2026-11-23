# 2026-11-24 OMS 网页排版与文案

本轮从桌面浏览器对照 osu! 官网首页、下载、谱面列表、排行榜、新闻与论坛。首页先给下载和查谱，再放新闻。筛选紧邻结果，技术说明留在对应入口。OMS 首页用七键轨道表现游戏玩法。[osu! 首页](https://osu.ppy.sh/) · [下载页](https://osu.ppy.sh/home/download) · [谱面列表](https://osu.ppy.sh/beatmapsets) · [排行榜](https://osu.ppy.sh/rankings/osu/global/performance) · [论坛](https://osu.ppy.sh/community/forums)

| 页面 | 玩家可见变化 |
| --- | --- |
| 首页与下载 | 下载和查谱进入首屏。按钮直接打开 `oms_20260626` 发行页。下载说明按解压、添加谱面、设置键位排列，开发版 IR 和各播放器插件有就近入口。 |
| 新闻与帮助 | 新闻列表按实际发布日期分年，首页和列表共用可点击的新闻行。帮助目录在手机上分两栏，长说明按段落呈现，校验和许可可展开。共享新闻、帮助的地址和 ID 保留。 |
| 查谱与查榜 | mania 的 1–18K 改为下拉，谱面榜、玩家榜和找玩家在同一组导航。覆盖率榜只显示一列有成绩的谱面数，其他指标仍显示谱面数供对照。个人页先显示玩家名，再显示成绩筛选。 |
| 社区与账号 | 发帖按钮与帖子筛选分开，空列表说明当前状态。账号页可直接打开登录弹窗。 |

## 本地验证

- Web `2a9db1bb8cd1` 通过 TypeScript、生产资源构建与隔离运行入口的 10 个 HTTP 检查。Webpack 仍报告应用资源和入口大小提示。`check-score-options.cjs` 通过 15 项，`verify-browser-api.cjs` 的模拟请求回归通过。
- Chrome 在 1440px、390px、320px 完成 47 项检查。走通下载、窄屏菜单、登录弹窗、帮助锚点和插件附件、难度与单谱榜、清空和恢复成绩来源、个人页、mania 键型、找玩家、社区搜索与发帖入口。浏览器检查读取隔离数据，未提交帖子或成绩。桌面实测发现玩家榜表头被压窄，调整表头与覆盖率列后重新复验。
- 共享新闻与帮助的 v1 JSON、稳定 ID 和 `ETag` 的 304 在实际 HTTP 路径通过。现有 PHP 检查改为比对帮助锚点下的可见段落，194 项通过。Client Bridge 仅同步采纳位置，来源、适用范围与待复核状态沿原记录。
- 对照图、最终桌面与手机截图及浏览器报告位于本机 `artifacts/site-design-20261124/`。

## 生产发布

- 03:21:15 CST 核验现行包 `909f8ff7d4de-2a9db1bb8cd1`，直接回退包为 `909f8ff7d4de-c26b894f9f53`。发布包 74,214,316 B，SHA-256 `a71f11e775799a999b8d147dbf530998ee2900f8d652b42f71beb609ea4462f1`。准备阶段的离线缓存缺 `pydantic-core` wheel，改用当前服务的同锁定虚拟环境，核验 41 个后端文件、634 个环境文件与 9,740 个运行文件。环境差异只涉及新路径的启动脚本。
- 公网浏览器重复通过 47 项检查。OMS 首页、两项后端健康检查与个人站 HTTPS 正常。公网获取的 9 个静态资源及对应源码压缩包的 SHA-256 与正式包一致，包含上一版带指纹的 CSS。网页现行 CSS 是 `/assets/css/app.49ffeff7.css`，SHA-256 `50dd8a43f41e30a0ecd692d8c79c078e9ee5710b55aec61011ac6d94cf16eae3`。
- 发布前后快照为 `daily-20261123T191948Z.db.gz` 与 `daily-20261123T192137Z.db.gz`，固定 helper Invocation 分别为 `6b1ed10f7d7545cf845c68a784b81520` 和 `a2e62878ac304fa4a06e41ade0820cbe`。两对带 sidecar 的完整快照已外取到 F 盘，核对 gzip、SHA-256、SQLite 完整性、外键及 schema 3 的 22 张表。主库 dev `64771`、inode `265517`。三个备份 timer 均为 `enabled / active / waiting`。
- 配置原件和切换收据位于 F 盘受限目录 `artifacts/site-design-20261124/production-private/` 与服务器 `/var/backups/oms-maintenance/oms-web-site-design-20261124/`。发布临时目录已清理，根盘剩余 29,262,610,432 B。后续取[现行维护和回退](production-maintenance.md#当前应用维护与回退)。真实下载入库、账号和客户端交分验收取[真人路径](production-maintenance.md#真人验收)。
