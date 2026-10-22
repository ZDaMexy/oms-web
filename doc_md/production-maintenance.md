# OMS 原版 osu-web 试运行维护

2026-10-22 [全工作区安全修复](architecture-security-review-20261022.md#全量修复实施)已将OMS/helper切换至Python3.12.15/OpenSSL3.5.9，独立PHP切换至`php85-0069de279481`的修复组合，宝塔为13.1.0/Python3.13.16；生产Node22.23.4、uv0.13.4及原证书补丁保持。原OMS HTTP应用不变，Homepage安全依赖另循其部署hook发布；当前恢复计划和独立备份工具已同步新root/目录分类。历史应用lock和manifest不改标签，回退不得重新引入旧运行时、CA或curl；具体版本、备份及未完成门取该记录。

2026-10-22 已实施[PHP 与共享主机安全维护](php-security-maintenance-20261022.md)：生产 PHP8.5.12、旧 PHP8.2 停用、状态页访问修复、BT Nginx1.30.6 / 系统 OpenSSL3、启动依赖及内核更新，真实重启后双站与业务服务通过。应用 release 仍为 `824de121a686-494932756b74`，原应用 manifest 保留历史；当前 PHP 取实际 RootDirectory / 进程与独立安全收据。应用回退保留这些安全修复，不能重新启用旧 PHP。

2026-10-12客户端谱面列表沿[当前接续](client-native-services-20261011.md#2026-10-12客户端页面纠正)先选模式，再显示所属来源：BMS 仅 Ginger Rush / 616，osu!mania 仅 Sayobot，切回 BMS 恢复上次来源；等待中关闭 / 改选阻止旧页面弹出。原生真实字段、普通 / 大卡、阅读恢复及原MD5详情 / 榜保持；仅客户端与文档，没有服务重验或部署，生产来源 / 备份日期和真人门保持。玩家验收以正常OMS窗口对照lazer的排布、字号、长名 / 展开和真实键型为准；隔离420内容宽度检查只作边界，不代签实际窗口 / DPI。

内容维护每次改共享JSON后检查原生v1 / 256KiB预算、实际kernel、网页摘要 / 完整正文 / 帮助锚点、ETag / gzip / HEAD / 304及普通刷新；随准确不可变包发布，不直接改运行目录。账号 / 用户内容继续由唯一Backend管理。

## 当前原生服务维护与回退（2026-10-11）

2026-10-22 起，以下历史应用回退步骤须保留受修复 PHP RootDirectory、cache 启动依赖和 BT Nginx / 状态页安全配置；不得直接覆盖旧五件原件而恢复漏洞版本。新版运行时拦截、准确原件和当前恢复材料范围取[安全维护](php-security-maintenance-20261022.md#发布与回退约束)。

直接上一版 `cc37bdb8f3b4-f9a5afd99939 / production-r1`；本轮新→该版→新已实际三服务同库通过。未来操作先取新鲜固定helper备份 / F完整核验与最新13件配置保全，保存timer后暂停；停止Web / cache、主IR / catalog，按本轮 `native-services-20261011/production-private/before/` 五件原件恢复四unit与OMS include，原子切current、daemon-reload、BT指定binary / config检查，启动IR / catalog核双health、生成旧正式缓存、init Nginx reload并启动FPM，核真实旧页面 / 资源 / 双站及三个PID。保留同一业务库 / schema3，不回灌raw；不能仅切current或只换网页。

新原生客户端内容端点在直接旧版不存在，回退需明确该能力会显示读取失败；网页 / IR旧服务仍沿已验证范围。固定D1/22b维护、D1/e6旧设计和全部当前 / 上一版 / 更早保留运行包不清理。共享gzip沿此前网络配置，原2026-10-08旧设计恢复日期不刷新。下方网络与成绩页回退属于原发布，当前步骤只取本节；后续配置 / 数据变化先重新核门，不能盲盖旧原件。


当前2026-10-11 16:34:47 CST已发布端内服务配套，Web / Backend真实来源、原生内容缓存、90秒共载、三服务同库往返、公开41＋内容8项与两新鲜固定helper备份只取[本轮记录](client-native-services-20261011.md#生产发布与闭环)。日备份恢复，产品保持**已部署待真人验收**；当次服务 manifest 的客户端字段绑定功能源码 58454332，f2b495f4 属旧统一面板软件；现行客户端取[页面纠正来源](client-native-services-20261011.md#2026-10-12客户端页面纠正)，用户 VS Code 非调试验收，未生成 Windows 包。

此前2026-10-11 12:24:11 CST网络优化发布与清理、往返及备份保持[该轮原证据](network-service-review-20261011.md#清理后实际发布已部署待验收)；现行来源及原生服务发布取本页顶部。

此前2026-10-09 22:17:27 CST已发布OMSIR成绩页：实际客户端并列、旧库低调标记、EX / ACC / 六类判定 / 连击 / Mod与原详情；接入事实、原失败、模板路由补齐及全部新增证据取[本轮记录](omsir-score-page-20261009.md)。本轮重启主IR以加载附加展示字段，catalog不重启；产品真人门保持待验收。

2026-10-08 原版网站已部署，状态 **已部署待验收**。玩家可从[首页](https://oms.zdamexy.work/)进入新闻、独立下载与帮助、谱面浏览、跨来源榜、账号、个人页、玩家榜和社区。真人下载入库、账号 / 密钥、OMS 对照及固定播放器 P/C 尚未签收。具体运行、恢复、失败与发布证据只取[生产记录](production-deployment-20261007.md#正式发布与收尾)。

2026-10-09 文案与阅读体验审改已发布，软件 / 公网检查和发布前后完整备份通过；具体范围、失败尝试与新增证据取[本轮审改记录](deai-review-20261009.md)。下文2026-10-08的完整压力 / 恢复 / 旧设计往返证据保留原日期，不因这次网页更新重标。产品真人门继续待验收。

同日14:07:57 CST 谱面榜难度表浏览已发布：先选Zris目录的56张表，再按完整曲名首字母排序、过滤和分页；当前来源、发布前后备份、公网核对、启动502与新增读取 / 磁盘预算取[本轮记录](bms-difficulty-tables-20261009.md)。该快照按发布更新；不自动每日抓表。旧文案发布和更早恢复分别保持原证据日期。

同日15:03:58 CST 已发布表内等级选择，实际软件 / 本地桌面 / 公网检查、视口未生效与线上浏览器超时、备份和更新后预算取[本轮等级筛选记录](bms-level-filter-20261009.md)。前述14:07难度表来源和更早证据保持原日期；本次未重新抓表。

同日17:24:30 CST 已发布成绩来源与排行榜审改，覆盖谱面头部、来源筛选、谱面 / 玩家榜和个人成绩。完整本地浏览器、公开成绩一致性、两次备份、有限资源门、历史运行包 F 归档及线上取景超时取[本轮排行榜记录](rankings-layout-review-20261009.md)。前述筛选与旧证据保持各自日期；真人门继续待验收。

同日20:12:43 CST 已按用户澄清合并 LR2IR 为普通来源，默认页为「排行榜」；原数据 / 名次 / 身份保持。当前发布、完整选择与原客户端详情的实际验证取[本轮记录](lr2ir-source-presentation-20261009.md)。

## 当前来源与运行位置

| 对象 | 当前实际身份 |
| --- | --- |
| HTTP / 网页运行包 | `/opt/oms-ir/current` → `/opt/oms-ir/releases/824de121a686-494932756b74`，2026-10-11 16:34:47 CST最终切入 |
| 服务源码 | Backend `824de121a6862d2f9b576f66a18715192fd0d57f`；账号、成绩、社区仍为 FastAPI / SQLite 唯一权威 |
| 原版页面源码 | Web `494932756b747edba791fd1499b83348ec49b963`；Laravel / Blade / React / Less / Turbo、AGPL / 归属及对应源码下载保持 |
| 固定维护代码 | `/opt/oms-ir/releases/d1f052b93a81-22b4ee54f237`；日备份 unit 直接指向此包，不能随 HTTP 回退覆盖或当闲置目录清理 |
| 源码 / 旧设计回退目标 | `/opt/oms-ir/releases/d1f052b93a81-e6fdf914cb04`；原设计完整外存备份在 F 盘，服务器没有另打旧设计备份包 |
| 实际业务库 | `/var/lib/oms-ir/ir.db` / schema3 / 22表；本次保留同一 dev / inode，无生产 raw 恢复或样本数据迁入 |
| 全量公开历史 | `/opt/oms-ir/archives/lr2ir-v3-public-1-e8f5702701bb5382b93ec572815e07306b9017b124fee505152e47723ac0acdd.db`；只读25,562,325存储摘要 / 334,117谱面，其中25,560,957合格摘要，隔离行不参与榜 |
| PHP 环境 | `/opt/oms-web/runtime/php85-922304e595f8`，Alpine / PHP8.5；独立 oms-web 用户，只读 `/app`，PHP8.5.12；BT旧PHP8.2已停用，取本页顶部安全维护 |
| 当前可写缓存 / 日志 | `/var/cache/oms-web/824de121a686-494932756b74/production-r1`；bootstrap / storage私有、PHP日志沿原位置 |
| 实际 OMS 路由 | 宝塔 `39.105.55.78.conf` 与 `extension/39.105.55.78/oms-ir.conf` 配对；共享 Nginx、个人站、证书、ACME规则保留 |

上述 Web / Backend 是运行提交，文档HEAD、历史取证和外置检查工具各自记录。客户端现行原生服务完整来源取[2026-10-11配套](client-native-services-20261011.md#2026-10-12客户端页面纠正)，直接登录与待交仍沿原来源；下方2026-10-10接线为原提交历史。旧ppy API为空 / 总开关false，用户从F工作区VS Code非调试验收，未生成Windows发行、publish或安装副本。

插件沿原八个批准文件的完整字节 / 版本清单：beatoraja 0.8.8、LR2oraja build11611350155、ED v0.4.0、OpenLR2 v260915 x86 / x64。网页能下载插件不代表这些真实宿主已完成交分、原生读榜及玩法矩阵验收。

## 客户端与网站接线（2026-10-10）

2026-10-11已发布共享news / help JSON，网页与原生客户端同源，固定OMSIR直接登录说明同步；此前启用 / 填地址 / 保存缺口关闭。[本轮配套](client-native-services-20261011.md)签源码 / 生产读取，仍不代签真实账号或公开20260626发行。

2026-10-10采用`client-omsir-direct-login`，直接登录来源见[账号快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-ir-account-login-snapshot-20261010.md)，当时只更新客户端、删除旧地址 / 开关 / 保存与通用奖杯 / 目录搜索。现行独立原生页 / 统一谱面列表接续见顶部来源，固定OMSIR、匿名公开榜与原origin凭据 / 待交隔离仍适用；浏览器与桌面分别登录，真实窗口 / 账号 / 下载仍待。

采用`client-web-wiring`的[客户端提交快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-client-web-wiring-snapshot-20261010.md)，实际路径 / 参数只取[共同接线合同](../../../oms-server/dev_bridge_md/doc_md/subline/oms-player-site/constraints.md#客户端与网页入口)。客户端恢复选歌 / 结算谱面、规范个人页和玩家排行；原谱MD5 / OMS ID、当前玩法 / 键型、来源含空 / 条件 / mania组和页码保留；可切换地址仅为该旧提交的交互，现行origin取上方新来源。浏览器分别登录，不传桌面token。

2026-10-10较早接线只更新客户端及文档，当时a85 / b173生产来源不变；65例 / 双配置和匿名页面仅证明该提交软件。当前新增原生页面与配套发布不由旧65代签，来源沿顶部。原账号 / 待交、两端同范围、实际原包下载及P/C按[真人验收](#真人验收)，无Windows发行物。

## 2026-10-11 网络优化回退历史

直接上一版为 `a85aee3e3c45-b17354d27c6b / production-r1`；本轮真实三服务新→该版→新、同库 / schema保持已通过，原2026-10-08旧设计恢复保留原日期。未来回退先新鲜固定helper备份 / F完整核验和最新配置保全，停止Web / cache与IR / catalog后，再按本轮 `network-deploy-20261011/production-private/before/` 五件原件恢复IR、catalog、Web、cache unit与OMS include，切current、daemon-reload、宝塔Nginx检查，启动IR / catalog、核双health、生成旧正式缓存、Nginx reload、启动FPM并核页面 / 资源 / 双站及三个实际PID。所有HTTP / catalog / PHP必须同步加载目标，不能仅切current；共享图片gzip维持本轮值，旧raw不覆盖现库。

所有当前 / 直接上一版 / 固定D1维护与旧设计、B0 / FFF / 479 release仍保留；当前准确前后配置、两次备份、timer与空间仅取本轮记录。下一次操作前复核新流量 / 数据增长和最新配置，不能复用过时原件盲盖。

## 2026-10-09 成绩页维护与回退历史

运行源码、正式缓存、精确IR路径、四件配置变化（含JSON模板exact路由）、前后12件原件、两对完整备份与F核验取[本轮发布记录](omsir-score-page-20261009.md)。主IR已加载a85 / 新PID3509802，catalog原PID保持；与过去纯Web更新的主IR未重启不同，不能套用旧三配置回退步骤。

当次直接同库回退479：先新备份和配置保全，恢复本轮before的IR / 两Web unit与OMS include，切current、daemon-reload、BT检查 / 重载、生成旧正式缓存，再重启IR / FPM并核公开范围、两站、资源。保持现库，禁止旧raw覆盖新内容；实际新→旧→新往返仍只取原2026-10-08证据。固定D1/22b维护 / D1/e6旧设计、B0、FFF和479均保留。

证据根为 `F:/zdamexy-workspace/websites/oms-web/artifacts/score-page-normalization-20261009`。timer恢复enabled / active / waiting；同库dev / inode保持。收尾空闲4,545,056,768 B，保守预留4,402,384,384 B，余142,672,384 B。新有限12次读取不刷新旧持续 / 压力 / 恢复；未做母库清洗、schema迁移、真实客户端或Windows发行。

## 2026-10-09 普通来源发布历史（20:12）

本轮将 LR2IR 成绩作为普通来源并列展示，源码 / 资源 / 对应源码包已切479，Backend / vendor / 八插件 / PHP环境保持。两个Web unit与OMS include仅更新版本 / 独立缓存绑定，数据库身份及主IR / catalog进程保持。实际缓存 / FPM / 宝塔Nginx、公开36项成绩一致性及33项页面 / 全件资源 / 双站检查取[本轮记录](lr2ir-source-presentation-20261009.md)。线上浏览器取景超时，本地截图不代签生产真人视觉。

前后12件完整配置、固定helper新鲜两对备份和实际有限资源窗在 `F:\zdamexy-workspace\websites\oms-web\artifacts\lr2ir-source-presentation-20261009\production-private`。timer恢复enabled / active / waiting；收尾下一触发的原值在 `transfer-retirement.json`，备份 / 缓存不可读终态峰保持null。

当次直接同库网页回退为 `b879e4233818-fffddaac1ce4 / production-r1`；先新备份和配置保全，再恢复本轮before的两Web unit与OMS include、核宝塔Nginx、切current / 重载并生成旧正式缓存 / 重启FPM，核有界就绪 / 双站 / 资源。当次主IR仍从B0加载，主IR / catalog / 固定维护不换源，不回灌raw；本轮未做实际往返。已无活动引用的6fb运行目录在全部字节 / 元数据核对、新鲜备份与再次核引用后退役，现从本轮受保护F全件归档恢复；B0、D1固定维护 / 旧设计和日备份保留。

完整F副本与远端SHA核对后只退役本任务incoming重复gzip；收尾空闲4,591,403,008 B，保守预留4,402,384,384 B，余189,018,624 B。旧压力 / 恢复仍保留原日期，增长触发重新预算。共享落点同步[Homepage镜像](../../homepage-website/doc_md/other/oms-lr2ir-source-20261009.md)与[旧Website镜像](../../oms-website/doc_md/other/oms-lr2ir-source-20261009.md)。

## 2026-10-09 排行榜展示发布记录（17:24）

本轮整理成绩展示，Backend / vendor / 八插件 / PHP环境保持原字节，schema3 / 同一库与主 IR / catalog PID保持。两 Web unit 与 OMS include只换fff版本 / 独立缓存绑定。完整实际启动、首个启动502与有界就绪、公开成绩29项 / 页面资源33项、源码下载及双站检查取[排行榜发布记录](rankings-layout-review-20261009.md)。主 IR仍从B0加载，不能清理B0。

前后12件配置与固定helper两对完整备份在 `F:\zdamexy-workspace\websites\oms-web\artifacts\rankings-ux-20261009\production-private` 的 `before / after / backup-pre / backup-post`。终态不可读峰保持null，timer恢复enabled / active / waiting，收尾当次下一触发2026-10-10 04:17:45 CST。

当前直接网页回退为 `b879e4233818-6fbf7fd157d2 / production-r1`，保留当前库；先新备份 / 配置保全，再按本轮before原件恢复两个Web unit与OMS include、检查宝塔Nginx、切current / 重载并生成旧正式缓存 / 重启FPM，核有界就绪、双站与资源。主IR / catalog / 固定维护不换源，不回灌raw；本轮没有实际往返。

历史2b / 747运行目录已全件F归档并核所有字节 / 元数据及无活动引用，再于新鲜备份后退役服务器确切目录，现需从 `production-private/obsolete-runtimes/` 的核验归档恢复。当前6fb回退、B0 / D1维护 / 旧设计和日备份保留。仅在完整F副本与远端SHA重绑后退役本任务incoming重复gzip。收尾空闲4,605,456,384 B，沿2026-10-08最大raw / 八对 / 额外2 GiB保守所需4,402,384,384 B，余203,072,000 B；这次有限资源窗不刷新旧压力 / 恢复证据。共享投影取[Homepage镜像](../../homepage-website/doc_md/other/oms-ranking-layout-20261009.md)与[旧Website镜像](../../oms-website/doc_md/other/oms-ranking-layout-20261009.md)。

## 2026-10-09 表内等级发布记录（15:03）

本轮更新表内等级选项、等级 / 字母 / 搜索组合、分页与单曲返回等级，Backend / vendor / 插件 / PHP环境和schema3保持原字节，同一业务库和主IR / catalog PID保持。两Web unit与OMS include只换当前版本 / 独立缓存；正式缓存、FPM实际启动、BT Nginx检查和双站HTTPS通过。完整事实、首个CSS404 / 启动502与有界就绪、测试范围和预算只在[本轮记录](bms-level-filter-20261009.md)登记。

发布前后12件配置与准确helper备份对在`F:\zdamexy-workspace\websites\oms-web\artifacts\bms-levels-20261009\production-private`的`before / after / backup-pre / backup-post`；不可读终态备份 / 缓存峰保持null。timer恢复enabled / active / waiting，收尾当次下一触发2026-10-10 04:18:11 CST。

当次直接网页回退目标`b879e4233818-7473587da7e1 / production-r2`，保留当前库；先取得新备份和完整配置，再恢复本轮`before/`的两个Web unit与OMS include，检查BT Nginx、切current、重载并生成旧正式缓存 / 重启FPM，核就绪 / 双站 / 资源。主IR / catalog / 固定维护不换源、不回灌raw。本轮未做实际往返；旧D1/e6只取下方原日期范围。

新增两路等级过滤读取在原FPM限制内通过；当前空闲4,493,045,760 B，按2026-10-08最大main＋WAL与八对 / 额外2 GiB合计4,402,384,384 B保守计算，余量90,661,376 B。仅在完整F包和远端SHA重绑后退役本任务73,083,160 B incoming重复gzip；运行 / 维护 / 747回退目录、日备份与F包保留。共享落点同步[Homepage镜像](../../homepage-website/doc_md/other/oms-table-levels-20261009.md)及[旧Website镜像](../../oms-website/doc_md/other/oms-table-levels-20261009.md)。

## 2026-10-09 难度表浏览发布记录（14:07）

本轮更新难度表浏览、离线导航元数据、散列资源与对应源码下载；Backend、vendor、八个批准插件、PHP运行环境和schema3保持完整字节。实际库dev / inode保持，主IR / catalog未重启。两个Web unit与OMS include只修改新版本 / 独立缓存目录绑定，正式缓存和FPM实际启动通过；配对OMS根站点、Homepage、固定维护和TLS / ACME规则保留原字节。

447项线上表目录 / 来源 / 排序 / 过滤 / 分页及资源核对、另33项原页面 / 插件 / 全件源码 / 双站核对均通过；新增两路大表读取的有限资源门通过。准确发布 / 失败 / 瞬时预算和更新后盘账只在[本轮难度表记录](bms-difficulty-tables-20261009.md)完整登记；本轮没有重做2026-10-08的1,800秒和两次空恢复。

发布前后12件配置原件与准确固定helper备份对在`F:\zdamexy-workspace\websites\oms-web\artifacts\bms-tables-20261009\production-private`的`before / after / backup-pre / backup-post`；终态不可读的备份 / 缓存峰保持null。timer恢复enabled / active / waiting，收尾当次下一触发为2026-10-10 04:18:37 CST。

当次直接网页回退目标为`b879e4233818-2b240a44fd5c`，保留当前业务库。未来操作先取得新的准确备份与配置保全，再按本轮`before/`原件原子恢复两个Web单元和OMS include，核BT Nginx、切回current、重载路由并生成旧版缓存 / 重启FPM；启动检查有界等待就绪，再核双站和资源。主IR / catalog / 固定维护不换源、不回灌raw。本轮首个502实际退回2b，随后最终切入747；这只证明该具体网页绑定回退，旧静态D1/e6兼容仍取下方历史。

仅在完整F副本与远端SHA重绑后退役4件incoming重复传输gzip，以恢复八对 / 最大raw / 额外2 GiB的原空间预留；当次空闲与保守所需的差为249,528,832 B。原始F副本、所有运行 / 维护 / 回退目录和日备份保留。共享设施落点同步[Homepage镜像](../../homepage-website/doc_md/other/oms-bms-tables-20261009.md)与[旧Website镜像](../../oms-website/doc_md/other/oms-bms-tables-20261009.md)。

## 2026-10-09 文案发布记录（03:56）

本次仅更新网页源码 / 散列资源及其对应源码包，Backend、vendor、插件、PHP运行环境和schema3保持原完整字节；主 IR / catalog未重启，实际库 dev / inode保持。两个网页unit与OMS Nginx include只改版本绑定，正式新缓存已实际生成，FPM已清旧OPcache。当前8个资源与8个批准插件文件的HTTP字节已核对；HTML仍重新验证，资源immutable，插件no-store。

发布前后配置与准确日备份对在 `F:\zdamexy-workspace\websites\oms-web\artifacts\deai-20261009\production-private`；`before/` 与 `after/` 保留完整配对站点配置、unit / timer和manifest原件，`backup-pre/` 与 `backup-post/` 保留完整gzip / sidecar、private raw及核验结果。本次终态备份 / 缓存峰不可用，记null；timer恢复enabled / active / waiting，收尾当次下一触发为2026-10-09 04:15:11 CST，不承诺以后秒数。

直接回到上一网页版本时，目标为 `b879e4233818-b0feceae22e4`，并保留当前业务库。未来操作先取得新的准确一致备份与配置保全，再按本轮F盘 `before/` 的已核对原件原子恢复OMS include和两个Web单元，检查BT Nginx、切回current、重载路由并重新生成上一版缓存 / 重启FPM，核双站和实际资源。Backend / catalog / 固定维护不换源、不回灌旧raw。此目标是本次发布前实际运行版，本轮没有重做往返；旧静态设计D1/e6的2026-10-08兼容与回退范围仍取下方历史步骤。

共享配置变化在[Homepage镜像](../../homepage-website/doc_md/other/oms-web-copy-review-20261009.md)与[旧Website镜像](../../oms-website/doc_md/other/oms-web-copy-review-20261009.md)同步，完整事实与证据取本轮审改记录。

## 新闻与内容维护

新闻只维护[news.json](../resources/oms/news.json)，帮助只维护[help.json](../resources/oms/help.json)。HomeController同一读源提供首页 / 新闻 / 完整正文、/help和匿名结构化/client-content；实际稳定slug / help ID沿共享JSON，旧静态src/oms/news.ts只属旧设计来源。

保持实际 JSON 结构：文章包含 `slug`、`published_at`、`title`、`image`、`excerpt` 和 `body`；正文段落使用 `text`，可选 `heading` 与 `links`，链接使用 `label` / `href`。公开固定地址由 `slug` 决定，现有地址和真实发布日期保留。发布或试运行范围写在真实标题、摘要和正文中，不增加假新闻、玩家活动或已完成的真人验收；公开 20260626 与开发版 IR 的边界继续保留。

新闻随源码提交和不可变发布包上线，网页没有新闻编辑入口。更新后检查首页摘要、新闻列表、固定文章的日期 / 正文 / 链接以及普通刷新；维护者不能直接修改已发布只读包，也不能把只改本地文件记成已上线。对应运行来源、源码下载和实际发布结果仍按本文件及[生产记录](production-deployment-20261007.md)分别登记。

## 运行与资源核对

现行资源取[原生服务发布](client-native-services-20261011.md#资源与安全清理)：安装 / 三次切换 / 90秒两路共载的实际窗、原恢复预留与收尾空间分别记录。前一网络轮已发布网页身份复用、一次下载解析与同键合并 / 图片gzip，证据保留原日期，不混计本轮收益。客户端内容无启动预取 / 空闲轮询，按页请求、取消迟到结果、300秒有界缓存；谱包不经OMS代理。有限请求不签全站CPU / 长期流量提升，增长重新预算。

| 单元 | 固定预算和行为 |
| --- | --- |
| oms-ir.service | 500 MiB / CPU150% / swap0；loopback8081，按需 API |
| oms-ir-catalog.service | 96 MiB / CPU25% / swap0；loopback8082、批准源元数据；与IR / PHP每次同库切换同步重启，具体PID沿本轮收据 |
| oms-web.service | 200 MiB / CPU50% / swap0，high160 MiB；loopback FPM9070，两子进程按需启动，enabled / running |
| oms-web-cache.service | 128 MiB / CPU50% / swap0；正式 `/app` 与 URL 下生成配置 / 视图，完成后 exited，当前版本发布时重启 FPM清旧 OPcache |
| oms-ir-backup.service | 固定维护包，128 MiB / CPU50% / swap0；oneshot，不与另一备份 / 恢复并行 |

读取实际状态时先保存时间和 current，再检查原单元；不把一次空闲读数当作完整资源门：

```bash
readlink -f /opt/oms-ir/current
systemctl show oms-ir.service oms-ir-catalog.service oms-web.service -p Id -p LoadState -p MainPID -p MemoryCurrent -p MemoryPeak -p NRestarts -p Result
systemctl show oms-ir-backup.timer -p UnitFileState -p ActiveState -p SubState -p NextElapseUSecRealtime
systemctl show oms-ir-backup.service -p ExecMainPID -p MainPID -p ControlPID -p InvocationID -p ExecMainCode -p ExecMainStatus -p Result
df -B1 /
free -b
journalctl --namespace=oms-ir -u oms-ir.service -u oms-ir-catalog.service -u oms-ir-backup.service --no-pager -n 80
journalctl -u oms-web.service --no-pager -n 40
```

HTTP / PHP通过真实请求触发；不新增后台扫描、聊天、presence、多人或持续连接。HTML要求重新验证缓存，带散列资源一年 immutable；原插件 no-store。页面更新需检查普通浏览器刷新，不能只让玩家用 Ctrl+F5。

2026-10-08完整运行 / 两空恢复门与原空间底线保持[原日期生产证据](production-deployment-20261007.md)。最新安装 / 有限读取 / 收尾盘账取[原生服务配套](client-native-services-20261011.md#资源与安全清理)，历史运行包F保全沿各发布来源；不以新90秒刷新旧1,800秒，也不把十万合成数据当千万级历史证明。数据增长 / 新版本 / 实际故障触发重新预算，不自行购买或扩盘。

## 日备份与 F 盘外取

原 timer 保持每日04:15 CST、随机延迟至多300秒、Persistent=true；当前 enabled / active / waiting。2026-10-08实际恢复后下一次为2026-10-09 04:16:57 CST，这是当次 systemd 结果，不承诺以后固定秒数。

日备份仍在 `/var/backups/oms-ir/daily-<UTC时间>.db.gz`，同名 `.json` 最后发布。固定 helper 只取一次真实 current，sidecar绑定当时运行 manifest及维护来源；旧 sidecar不改标签。只有完整核验的日备份对可按原 keep-days7清理，预算按八对计算；孤立件、失败件、手工恢复与发布前快照不当成合格 daily 自动删除。

1. 每次发布前 / 后、每周外取及故障时，从本次实际成功 InvocationID 的完成行识别准确对；核实已关闭 MainPID / ControlPID、真实退出状态、固定 helper、当前来源及峰值。oneshot终态峰如 `[not set]` 如实记null，不能填0或用末次采样冒充。
2. 完整 gzip / sidecar 直接传至 F 盘受保护新目录，逐件核字节 / SHA、完整 gzip EOF / CRC、raw size / SHA、integrity / FK、22表 / sequence / 索引 / trigger及来源绑定。目录只允许当前用户、SYSTEM、Administrators；个人原始行和凭据不输出、不进Git。
3. 真正恢复先在新空目录进行，冻结包 / 依赖与 fresh缓存独立还原，公开投影只读引用；签收正常读写、撤销 / 隐藏、全量榜 / 非空原生 / 分页及实际资源和F全件交接后，才准确退役自己的恢复数据。本次两轮已有完整证据，未变时不重复制造恢复副本。
4. SQLite一致备份仅包含业务库；全量公开投影、对应源码 / 依赖包和当前配置各有独立完整F来源，不拿241,664 B的真实业务raw冒充1.6 GB历史投影已保全，也不以只读投影代替账号 / 会话备份。

2026-10-08首次发布前后正式对、失败observer及旧恢复保全沿[原日期生产记录](production-deployment-20261007.md)。最新两个固定helper准确来源 / Invocation、完整F核验与timer取[原生服务配套](client-native-services-20261011.md#新鲜固定helper备份与收尾)。后端[deploy](../../../oms-server/oms-backend/deploy/README.md)的旧静态命令和b520仅属历史；当前三服务同库回退取本页现行原生维护节，旧设计仍按下节2026-10-08原范围。

## 保留当前库的设计与源码回退

2026-10-08新→旧D1/e6→新已实际通过。恢复旧设计时保留同一业务库、当前UUID / 账号 / 会话 / 密钥 / 隐藏 / 社区及真实限流变化，不回灌旧raw。以下属于该次schema3兼容范围，后续变更先核当前实际状态和新兼容证据。

1. 完整保全当前实际配置、manifest、unit / timer状态和故障证据至F。暂停timer前记录其活动 / 启用状态，等待原worker关闭，以固定helper取得新一致备份并完整F核验。恢复串行，不能复用2026-10-08冻结绑定去执行未来发布。
2. 停当前主IR和新PHP后再核同一DB身份 / schema。旧全部定义保留；本次仅允许已采用的 `scores_directory` 与 `score_groups_public_directory` 两条普通目录索引，不因它们拒绝已证明兼容的旧源码，也不为过门删除索引或任何数据。出现其他结构差异时保全实际停点并向前修复。
3. 从 F `production-before-switch-r4/08-39.105.55.78.conf` 与 `09-oms-ir.conf` 原件恢复配对OMS路由，按原mode原子替换；原子切 current至D1/e6、启动旧主IR并核schema3健康。本次catalog源码未变且未停止，固定备份unit / helper保持。共享Nginx、个人站、TLS / ACME不替换。
4. 用真实宝塔 `/www/server/nginx/sbin/nginx -t -c /www/server/nginx/conf/nginx.conf` 检查，再用 `/etc/init.d/nginx reload`。reload返回0不代表新规则已接收请求；有界检查实际HTTPS、旧主页完整manifest字节、IR / 社区 / 八插件和个人站，保留每次真实尝试。
5. 旧设计稳定后新PHP保持停止 / disabled；仅恢复事先保存的timer活动状态，核当前真实下一次触发时间。任一步失败保留实际服务 / 路由停点，不能宣称自动回退成功或用旧数据库消掉新记录。

本次第一forward曾在reload之后立即读到旧worker而误判，继而因未允许已批准两索引使自动恢复停在服务关闭；已独立恢复并修订，完整失败原件保留。正式R4同库往返及后续最终发布证明本节具体范围，不表示任意旧源码均兼容。

旧设计完整Git / 工作区差异 / 原发布 / 字体与两恢复只在 F:\zdamexy-workspace\oms\artifacts\oms-web-migration-20261007\legacy-r3；原D1/e6运行包在 F:\zdamexy-workspace\oms\artifacts\oms-deai-20261007。新包、两实际恢复、正式对、原旧配置和最终新配置均在 F:\zdamexy-workspace\oms\artifacts\oms-web-production-20261007；服务器只保留所需不可变运行 / 维护 / 回退目录，不另增旧设计备份。

系统日志的46原件已完整保存并核验到F后，才按用户授权清理。默认namespace480 MiB加原OMS32 MiB，合计512 MiB；完整原件及失败传输保留F，不重复清理其他日志或其他私有目录。

共享主机变更分别在[Homepage记录](../../homepage-website/doc_md/other/shared-journal-budget-20261008.md)和[旧OMS Website记录](../../oms-website/doc_md/other/shared-journal-budget-20261008.md)留链接；原件与当前事实仍只由本次生产记录维护。

2026-10-08用户已手动完成此前被自动审批拦截的本地pytest临时目录与npm缓存清理，F盘剩余约4.95 GiB；三处目录已只读复核不存在，该清理待办关闭。具体路径、执行者与复核证据见[本地清理补记](production-deployment-20261007.md#2026-10-08-本地缓存清理补记)。后续开发入口及依赖安装会重新生成相应缓存。

## 真人验收

1. 普通浏览器打开首页并正常刷新，核新闻、菜单、桌面 / 窄屏，再到 `/download` 与 `/help` 按步骤进入游戏。公开发行仍为页面明确标注的20260626，开发工作区IR不冒充已发行能力。
2. `/beatmapsets?ruleset=bms` 搜索并查看详情，确认Ginger / 616自动推荐与人工换源，实际下载原包并在OMS入库打开；mania选对应玩法及Sayobot实际包，核原生mania / 混合包边界。
3. `/account` 使用原OMS账号，检查我的记录、真实公开个人页、密钥一次展示 / 归属 / 撤销。不要提交密码或token作反馈；旧LR2IR同名账号不认领为OMS。
4. `/ir` 先选难度表和表内难度，按字母 / 表内搜索找到曲目，再进入该单曲MD5榜；段位组合或缺失MD5只跳原表。按谱面选一个 / 多个 / 全部 / 空来源，比较分数、独立灯、人数、全局名次及跨页；参考混榜后主动收窄到真实存在的同条件。OMS原用户按钮 / 登录页 / 个人页、选谱奖杯与网页同谱同范围对照。
5. 用户在VS Code非调试启动F:\zdamexy-workspace\oms，手动完整保存新局；断网、重启、原账号重登及旧待交补交核UUID不重造、归属不变。先导P先验OMS＋全量公开历史＋ED7K，再继续指定beatoraja / LR2oraja / ED / OpenLR2版本与完整玩法 / 架构矩阵，实际交分和宿主原生读榜逐格留证。

2026-10-08公网HTTP通过，但线上浏览器工具30秒超时。2026-10-09文案轮新增33项公网HTTP核对通过，生产下载页浏览器导航 / 读取35秒及截图15秒仍超时。同日难度表轮447项与另33项公网核对通过，线上建页40秒仍超时；未取得线上DOM / 截图或真人点击 / 登录验收。两轮桌面 / 手机与普通刷新证据均属于本地，用户先前认可的原版视觉也不提升为线上真人通过。遇到问题记录入口、操作、发生时间及页面提示，按反馈修复后只重验受影响范围。PP / 地力、聊天、presence、多人与官网谱包托管不在本次交付。

同日15:03等级筛选轮各309项本地 / 公网与另33项公网回归通过，本地桌面真实选表 / 换级 / 字母 / 分页与刷新通过；390×844视口设置未生效、实际仍1280×720，未签本轮窄屏。线上现有tab绑定40秒超时，没有取得本轮生产DOM / 截图。完整证据取[等级筛选记录](bms-level-filter-20261009.md)，真人门继续待验收。

同日17:24排行榜审改轮58项本地成绩、31项最终本地资源 / 页面、29项公开成绩与33项公开回归通过，更新前后同范围原始成绩一致。本地桌面及此前真实窄屏截图已取得，收尾追加视口仍未生效；线上建页20秒超时，没有生产DOM / 截图。截图不代签真人门，详细适用范围取[排行榜记录](rankings-layout-review-20261009.md)。
