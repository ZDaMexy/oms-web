# 2026-10-09 成绩来源与排行榜阅读审改

用户提供 OMS 与 osu! 谱面 / 排行榜截图，要求改善成绩来源和排行榜观感，并检查其他成绩页面。本轮延续原 Laravel / Blade / React / Less / Turbo 页面，整理信息层级、列宽、密度与展开方式。运行源码为 Web `fffddaac1ce468b6c250fb1016039834fcc772a5`；2026-10-09 17:24:30 CST 已切入生产，产品仍为 **已部署待验收**。准确当前绑定与真人门取[维护说明](production-maintenance.md)。

## 页面变化

- 成绩来源分为播放器与 LR2IR 历史两组，按钮显示短名称和选中状态；完整注册版本仍在按钮 title / aria-label 及“版本与来源说明”中。全选、空选、真实来源范围和单来源 / 同条件限制沿原 API。
- 谱面榜整理为标题 / 人数、真实榜首与本人卡、紧凑对齐表格。EX 加千分位，满分次要显示且不拆行；玩家名称、原始通关灯、来源、游玩时间各占独立列。未知时间用“—”，详情解释“来源未提供”。
- 每行详情展开占整张表宽度，显示真实 namespace / ID、来源及记录类型、游玩 / 接收时间、原始选项、缺失字段和独立最佳灯。原始 JSON 保留在第二层展开中，避免挤进最后一个窄单元格。
- 无封面 / 无已知统计的谱面收紧头部，不再显示四项全“未知”统计和大片空白；已有真实封面与已知数值继续显示。谱面收录和标识放在可展开信息中。
- 玩家榜同步暗色筛选控件、范围说明、真实榜首 / 本人卡、对齐数字与可滚动表格；个人页公开最佳 / 最近记录与本人历史同步条件展开、原始灯和突出统计数字。公开个人页的来源按钮使用完整行宽。
- 窄屏来源按钮自然换行，榜首卡收窄；成绩表在自身区域横向滚动。aria-pressed、详情展开状态、焦点样式与原生 details 保留。

通关灯颜色只帮助阅读，原始 label / family / value / rule 没有归一化成另一播放器的灯；未知灯保持原文字。本轮不增加头像、国家、PP、等级、判定计数、游玩日期或假用户。完整名次、并列、分页、本人名次与独立最佳灯仍由服务计算；累计 mania 分数在 JS 用 BigInt、在 PHP 用十进制字符串格式化。既有 Zris 56 张难度表与表内等级筛选保留。没有 Backend、接口契约、客户端或生产成绩写入。

## 软件、本地 HTTP 与真实浏览器

证据位于 `F:\zdamexy-workspace\websites\oms-web\artifacts\rankings-ux-20261009`，原件和含本地账号的检查输出不进入 Git。

| 证据 | 本轮结果与适用范围 |
| --- | --- |
| TypeScript | 实际 tsc 检查通过；最后 JS 修改后的 `typecheck-profile.log` 通过，最终提交只继续改同条件标签 CSS |
| 生产构建 | `compiled-inputs.json` 核 213 项精确提交输入与 474 件实际资源；webpack 成功，保留上游 3 项体积性能警告 |
| 成绩本地 HTTP | `scores-local.json` 58 项通过：真实归档 653 人 / 首两页 / 全局并列、全选空选及两个来源、BMS / mania、真实同条件选择、本地现有 owner 的 me 与本人历史、匿名拒绝 |
| 原页面与资源 | 最终版本 `http-regression-local.json` 31 项通过，包含页面、散列资源、插件和源码下载 |
| 表目录回归 | `http-local.json` 56 张表 / 309 项通过；后续只有展示样式和个人页调整，没有改变表目录 / 等级筛选逻辑 |
| 本地真实浏览器 | 653 人谱面、来源清空 / 两来源、第二页全局并列、档案无同条件提示、现有本地样本的同条件正向路径、玩家榜、BMS / mania 个人记录和条件展开通过 |
| 本轮窄屏 | 先前已取得真实 375×811 内容截图 `mobile-initial.jpg` / `mobile-board-final.jpg`，来源换行、局部表格及页面不横向溢出；未签横向手势。收尾再次设置 390×844 未生效，仍为 1280×720；该次截图已单列为无效视口尝试 |

最终桌面截图为 `final-header.jpg`、`final-desktop.jpg`、`final-details.jpg`、`players-final-desktop.jpg`；个人页为 `profile-desktop.jpg`。所有这些都是 **本地** 实际页面。653 人来源于公开 LR2IR 归档，榜首 REMILIA / LR2IR#55914 / EX3356 / 满分3372 / FULLCOMBO；本地 owner、mania900000及同条件样本是之前存在的隔离测试记录，不能代签生产账号或玩家验收。没有创建新账号、成绩或将测试库迁入生产。

实现过程中修正了 React17 不支持 useId、通关灯使用不存在的 Less 色变量、原生筛选白底、个人页按钮受父级半宽限制，以及同条件标签拆行；每次依实际截图 / 检查修正并重新构建。检查工具曾误把新版断言用于更新前页面，以及使用错误的本人历史地址，按实际路由修正后才通过；原失败日志保留。最终取景一次用错成绩详情的可访问名称，读取新 DOM 后改用真实按钮。

## 生产包与切换

完整包 `oms-native-b879e4233818-fffddaac1ce4.tar.gz` 为 73,449,942 B，SHA256 `d4516559c90ee08000e38d7ebc0ed422168994a4f91bc3541f9582841dc58273`。准确构建输入与完整 AGPL 对应源码包均已公开核对。包相对上一生产版本只替换 manifest、对应源码 tar 和玩家榜 Blade，另加入 12 件散列资产；Backend / vendor / 八件批准插件 / PHP 环境逐件保持原字节，旧散列资产保留。

安装成功后切 `/opt/oms-ir/current` 至 `/opt/oms-ir/releases/b879e4233818-fffddaac1ce4`，缓存为 `/var/cache/oms-web/b879e4233818-fffddaac1ce4/production-r1`。两 Web unit 与 OMS include 只将旧 6fb 绑定改为 fff；前后 12 件完整配置 / manifest 均保存受保护 F 目录。配对 OMS 根站点、Homepage、固定维护、TLS / ACME 等未受影响配置保持原字节。

实际库 dev64771 / inode265517、schema3 / 22表保持；主 IR PID2936181 与 catalog PID1862556 未重启。主 IR 仍引用 B0 的运行代码，必须保留 B0 目录。FPM PID3400292，正式缓存与真实命名空间启动、宝塔 Nginx 配置检查通过；预算保持 Web200 MiB / high160 / CPU50% / swap0，cache128 MiB / CPU50%。静态 systemd-analyze 对原 / 新单元均返回1，诊断相同，原因含宿主视角下不存在 RootDirectory 内 PHP 路径及既有 cloudmonitor 警告；这不是静态校验返回0，实际命名空间启动另有成功证据。

首个新 CSS 请求即为200 / 匹配；首次下载页读到启动502，有界等待后200，原始尝试保留。发布前公开成绩检查24项，发布后29项与另33项完整页面 / 资源 / 插件 / 源码 / 双站 HTTPS 检查通过。更新前后相同范围的成绩响应除快照读取时间外逐字段一致，653 人、全球名次、原始灯、条件及来源保持。线上浏览器创建页20秒超时，未取得本轮生产 DOM / 截图；HTTPS 成功不能提升为线上浏览器或真人通过。

## 两次完整备份、空间与有限资源门

固定 helper 仍直接取 `/opt/oms-ir/releases/d1f052b93a81-22b4ee54f237/backend/deploy/backup.sh`。发布前 `daily-20261009T091025Z.db.gz` 9,054 B / InvocationID `f65676fda8fd4b689e4119ef8301062e`，发布后 `daily-20261009T092649Z.db.gz` 9,063 B / InvocationID `20ac1ab0055d425599fa57fb399d43ce`，绑定分别为6fb与fff。两对完整 gzip / sidecar / release / private raw / invocation 日志均已外取至受保护 F 目录；raw 各241,664 B，完整 EOF / CRC / SHA、integrity / FK、schema3 / 22表 / 18索引 / 8trigger全部核验。终态 cache / backup 峰不可读记null。首个 SSH readlink 超时发生在启动备份之前；修正跨平台调用后取得上述新鲜成功对，没有拿失败调用当成功备份。timer 恢复 enabled / active / waiting，收尾实际下一触发2026-10-10 04:17:45 CST。

安装前空间只高于原预留约80 MB。先完整外取两个已不引用的历史网页运行包2b与747，逐件核全部内容、SHA与 mode / uid / gid / mtime / 链接；检查活动进程、FD / maps / cwd、配置、cron均未引用， fresh备份后再次核对，才退役服务器这两个确切目录。受保护 F 归档分别为：

- `b879e4233818-2b240a44fd5c.tar.gz` 62,779,084 B，SHA256 `d4252dfb1724d824ee2943396c10be216d0f212e3def1898850195fb9edbc599`，11,464项。
- `b879e4233818-7473587da7e1.tar.gz` 77,420,980 B，SHA256 `0c6954b080d37016f6abcf8acc8e582144d08693538b284af48b3772e027ac28`，11,528项。

二者现在只能从本轮 `production-private/obsolete-runtimes/` 的已核验 F 全件归档恢复，旧发布记录的服务器目录属于旧时点。当前6fb网页回退、主 IR B0、固定 D1/22维护、旧 D1/e6设计与日备份保留。新包安装完且远端 / F 字节与 SHA 再次匹配后，只退役本轮 incoming 的73,449,942 B重复gzip。收尾根盘空闲4,605,456,384 B；沿2026-10-08最大main＋WAL 1,422,161,928 B、八对与额外2 GiB合计2,980,222,456 B，保守所需4,402,384,384 B，余203,072,000 B。本轮没有清其他日志 / 缓存或私有目录，也没有扩大磁盘。

两并发读取者共12个真实网页 / 首两页榜请求，0.541秒窗口内最低 MemAvailable832,684,032 B、最高 PHP采样35,004,416 B，实际 cgroup峰59,924,480 B，swap / OOM / max / 重启零、限制保持。它只证明这次有限新页面读取，没有重做2026-10-08的1,800秒压力、空恢复或旧设计往返。

## 同库回退与未完成门

直接网页回退为上一版 `/opt/oms-ir/releases/b879e4233818-6fbf7fd157d2` / `production-r1`。未来回退前先用固定 helper 取得新的完整备份与配置；按本轮 `before/` 原件恢复两个 Web unit 与 OMS include、检查宝塔 Nginx、切 current、重载、生成旧正式缓存 / 重启FPM，有界等待后核双站 / 实际资源。保留当前库，主 IR / catalog / 固定维护不换源；本轮未执行实际往返。旧设计 D1/e6仍只取2026-10-08的已验证兼容范围。

本轮只更新 Web 与两站共享设施镜像，其他项目原有未提交修改由基线 / 精确差异保全验收；文档提交不重标运行 fff。共享事实投影见[Homepage镜像](../../homepage-website/doc_md/other/oms-ranking-layout-20261009.md)与[旧Website镜像](../../oms-website/doc_md/other/oms-ranking-layout-20261009.md)。真人正常刷新、登录 / 密钥 / 下载入库、OMS对照、固定宿主 P→C继续待验收，客户端不构建发行包。
