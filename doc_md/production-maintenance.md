# OMS 原版 osu-web 试运行维护

2026-10-22 [全工作区安全修复](architecture-security-review-20261022.md#全量修复实施)已将OMS/helper切换至Python3.12.15/OpenSSL3.5.9，独立PHP切换至`php85-0069de279481`的修复组合，宝塔为13.1.0/Python3.13.16；生产Node22.23.4、uv0.13.4及原证书补丁保持。原OMS HTTP应用不变，Homepage安全依赖另循其部署hook发布；当前恢复计划和独立备份工具已同步新root/目录分类。历史应用lock和manifest不改标签，回退不得重新引入旧运行时、CA或curl；具体版本、备份及未完成门取该记录。

2026-10-22 已实施[PHP 与共享主机安全维护](php-security-maintenance-20261022.md)：生产 PHP8.5.12、旧 PHP8.2 停用、状态页访问修复、BT Nginx1.30.6 / 系统 OpenSSL3、启动依赖及内核更新，真实重启后双站与业务服务通过。应用 release 仍为 `824de121a686-494932756b74`，原应用 manifest 保留历史；当前 PHP 取实际 RootDirectory / 进程与独立安全收据。应用回退保留这些安全修复，不能重新启用旧 PHP。

2026-10-17 本人网盘的数据库日备份与[OMS / Homepage 全量恢复材料备份](../../../oms-server/oms-backend/doc_md/other/full-backup-20261017.md)均已启用，覆盖历史投影、发布 / 依赖、两站、运行配置 / 证书及重建清单。当前工具、分层目录、旧引用、新备份验证及清理收尾只取[分层归档记录](../../../oms-server/oms-backend/doc_md/other/netdisk-layout-20261017.md)。原HTTP发布与固定helper保持，恢复私钥离线；[CDT已升级](../../homepage-website/doc_md/other/aliyun-backup-cost-20261017.md)，实际抵扣和新Linux整机启动恢复尚待。

当前2026-10-11 16:34:47 CST已发布端内服务配套，Web / Backend真实来源、原生内容缓存、90秒共载、三服务同库往返、公开41＋内容8项与两新鲜固定helper备份只取[本轮记录](client-native-services-20261011.md#生产发布与闭环)。日备份恢复，产品保持**已部署待真人验收**；当次服务 manifest 的客户端字段绑定功能源码 58454332，f2b495f4 属旧统一面板软件；现行客户端取[页面纠正来源](client-native-services-20261011.md#2026-10-12客户端页面纠正)，用户 VS Code 非调试验收，未生成 Windows 包。

2026-10-12客户端谱面列表沿[当前接续](client-native-services-20261011.md#2026-10-12客户端页面纠正)先选模式，再显示所属来源：BMS 仅 Ginger Rush / 616，osu!mania 仅 Sayobot，切回 BMS 恢复上次来源；等待中关闭 / 改选阻止旧页面弹出。原生真实字段、普通 / 大卡、阅读恢复及原MD5详情 / 榜保持；仅客户端与文档，没有服务重验或部署，生产来源 / 备份日期和真人门保持。

## 当前来源与运行位置

下表的HTTP源码绑定2026-10-11 16:34:47 CST实际发布记录；10月22日[安全维护](architecture-security-review-20261022.md#全量修复实施)另更新运行时并复核同一应用来源，PHP路径以该轮实际进程为准。10月16～17日清理与备份记录保留原时点。操作前仍按下方运行核对取得当时真实状态，文档HEAD不代表运行提交。

| 对象 | 最近发布记录的实际身份 |
| --- | --- |
| HTTP / 网页运行包 | `/opt/oms-ir/current` → `/opt/oms-ir/releases/824de121a686-494932756b74`，2026-10-11 16:34:47 CST最终切入 |
| 服务源码 | Backend `824de121a6862d2f9b576f66a18715192fd0d57f`；账号、成绩、社区仍为 FastAPI / SQLite 唯一权威 |
| 原版页面源码 | Web `494932756b747edba791fd1499b83348ec49b963`；Laravel / Blade / React / Less / Turbo、AGPL / 归属及对应源码下载保持 |
| 固定维护代码 | `/opt/oms-ir/releases/d1f052b93a81-22b4ee54f237`；日备份 unit 直接指向此包，不能随 HTTP 回退覆盖或当闲置目录清理 |
| 源码 / 旧设计回退目标 | `/opt/oms-ir/releases/d1f052b93a81-e6fdf914cb04`；原设计完整外存备份在 F 盘，服务器没有另打旧设计备份包 |
| 实际业务库 | `/var/lib/oms-ir/ir.db` / schema3 / 22表；该次发布保留同一 dev / inode，无生产 raw 恢复或样本数据迁入 |
| 全量公开历史 | `/opt/oms-ir/archives/lr2ir-v3-public-1-e8f5702701bb5382b93ec572815e07306b9017b124fee505152e47723ac0acdd.db`；只读25,562,325存储摘要 / 334,117谱面，其中25,560,957合格摘要，隔离行不参与榜 |
| PHP 环境 | `/opt/oms-web/runtime/php85-0069de279481`；独立 oms-web 用户，只读 `/app`，当前库版本与实际进程校验取本页顶部晚间安全记录；BT旧PHP8.2仍masked |
| 当前可写缓存 / 日志 | `/var/cache/oms-web/824de121a686-494932756b74/production-r1`；bootstrap / storage私有、PHP日志沿原位置 |
| 实际 OMS 路由 | 宝塔 `39.105.55.78.conf` 与 `extension/39.105.55.78/oms-ir.conf` 配对；共享 Nginx、个人站、证书、ACME规则保留 |

上述 Web / Backend 是运行提交，文档HEAD、历史取证和外置检查工具各自记录。客户端现行原生服务完整来源取[2026-10-11配套](client-native-services-20261011.md#2026-10-12客户端页面纠正)，直接登录与待交仍沿原来源；下方2026-10-10接线为原提交历史。旧ppy API为空 / 总开关false，用户从F工作区VS Code非调试验收，未生成Windows发行、publish或安装副本。

插件沿原八个批准文件的完整字节 / 版本清单：beatoraja 0.8.8、LR2oraja build11611350155、ED v0.4.0、OpenLR2 v260915 x86 / x64。网页能下载插件不代表这些真实宿主已完成交分、原生读榜及玩法矩阵验收。

## 当前原生服务维护与回退（2026-10-11）

2026-10-22 起，以下历史应用回退步骤须保留受修复 PHP RootDirectory、cache 启动依赖和 BT Nginx / 状态页安全配置；不得直接覆盖旧五件原件而恢复漏洞版本。新版运行时拦截、准确原件和当前恢复材料范围取[安全维护](php-security-maintenance-20261022.md#发布与回退约束)。

直接上一版 `cc37bdb8f3b4-f9a5afd99939 / production-r1`；2026-10-11 新→该版→新已实际三服务同库通过，其当次五件配置原件只作历史底稿。未来操作先取新鲜固定helper备份 / F完整核验，另保全操作前完整安全配置、unit与timer状态；暂停timer并等待运行任务结束，再停止Web / cache、主IR / catalog。基于当前受修复配置调整旧应用所需路径、缓存参数与配对路由，保留当前Python/OpenSSL、PHP RootDirectory、cache启动依赖及Nginx安全限制，禁止整份覆盖10月11日旧unit / include。候选配置经检查后原子切current、daemon-reload、BT指定binary / config检查，启动IR / catalog核双health、生成该应用正式缓存、init Nginx reload并启动FPM，核旧页面 / 资源 / 双站及实际进程身份。保留同一业务库 / schema3，不回灌raw；受修复运行时上的新候选回退须重新验收，10月11日结果不代签。

新原生客户端内容端点在直接旧版不存在，回退需明确该能力会显示读取失败；网页 / IR旧服务仍沿已验证范围。当前、直接上一版、固定D1/22b维护、D1/e6旧设计及其他必要保留包的八件准确清单取[存储清理记录](storage-cleanup-20261016.md#退役与保留范围)，其余旧测试/准备失败目录已完整F保全后退役。共享gzip沿此前网络配置，原2026-10-08旧设计恢复日期不刷新。日期化网络与成绩页回退只说明原发布范围，当前步骤只取本节；后续配置 / 数据变化先重新核门，不能盲盖旧原件。

历次发布日期、旧运行包 / 配置、失败与当次回退范围只从[日期化实施与发布证据](README.md#日期化实施与发布证据)读取。2026-10-09 各轮网页目标和 10 月 11 日网络轮步骤已退出当前维护页；独有历史步骤归回原日期记录，现行回退只按上节及操作前新核对的配置执行。

## 客户端与网站接线（2026-10-10）

2026-10-10采用`client-omsir-direct-login`，直接登录来源见[账号快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-ir-account-login-snapshot-20261010.md)，当时只更新客户端、删除旧地址 / 开关 / 保存与通用奖杯 / 目录搜索。现行独立原生页 / 统一谱面列表接续见顶部来源，固定OMSIR、匿名公开榜与原origin凭据 / 待交隔离仍适用；浏览器与桌面分别登录，真实窗口 / 账号 / 下载仍待。

采用`client-web-wiring`的[客户端提交快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-client-web-wiring-snapshot-20261010.md)，实际路径 / 参数只取[共同接线合同](../../../oms-server/dev_bridge_md/doc_md/subline/oms-player-site/constraints.md#客户端与网页入口)。客户端恢复选歌 / 结算谱面、规范个人页和玩家排行；原谱MD5 / OMS ID、当前玩法 / 键型、来源含空 / 条件 / mania组和页码保留；可切换地址仅为该旧提交的交互，现行origin取上方新来源。浏览器分别登录，不传桌面token。

2026-10-11已发布共享news / help JSON，网页与原生客户端同源，固定OMSIR直接登录说明同步；此前启用 / 填地址 / 保存缺口关闭。[本轮配套](client-native-services-20261011.md)签源码 / 生产读取，仍不代签真实账号或公开20260626发行。

2026-10-10较早接线只更新客户端及文档，当时a85 / b173生产来源不变；65例 / 双配置和匿名页面仅证明该提交软件。当前新增原生页面与配套发布不由旧65代签，来源沿顶部。原账号 / 待交、两端同范围、实际原包下载及P/C按[真人验收](#真人验收)，无Windows发行物。

## 新闻与内容维护

内容维护每次改共享JSON后检查原生v1 / 256KiB预算、实际kernel、网页摘要 / 完整正文 / 帮助锚点、ETag / gzip / HEAD / 304及普通刷新；随准确不可变包发布，不直接改运行目录。账号 / 用户内容继续由唯一Backend管理。

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
| oms-netdisk-backup.service | 独立数据库云备份，128 MiB / CPU50% / swap0；每日04:45 CST起加至多5分钟随机延迟 |
| oms-full-backup.service | 独立完整恢复材料备份，192 MiB / CPU50% / swap0；每日05:30 CST起加至多5分钟随机延迟，新对象上传 / 下载各限1 MiB/s |

读取实际状态时先保存时间和 current，再检查原单元；不把一次空闲读数当作完整资源门：

```bash
readlink -f /opt/oms-ir/current
systemctl show oms-ir.service oms-ir-catalog.service oms-web.service -p Id -p LoadState -p MainPID -p MemoryCurrent -p MemoryPeak -p NRestarts -p Result
systemctl show oms-ir-backup.timer oms-netdisk-backup.timer oms-full-backup.timer -p Id -p UnitFileState -p ActiveState -p SubState -p NextElapseUSecRealtime
systemctl show oms-ir-backup.service -p ExecMainPID -p MainPID -p ControlPID -p InvocationID -p ExecMainCode -p ExecMainStatus -p Result
df -B1 /
free -b
journalctl --namespace=oms-ir -u oms-ir.service -u oms-ir-catalog.service -u oms-ir-backup.service --no-pager -n 80
journalctl -u oms-web.service --no-pager -n 40
```

HTTP / PHP通过真实请求触发；不新增后台扫描、聊天、presence、多人或持续连接。HTML要求重新验证缓存，带散列资源一年 immutable；原插件 no-store。页面更新需检查普通浏览器刷新，不能只让玩家用 Ctrl+F5。

2026-10-08完整运行 / 两空恢复门与原空间底线保持[原日期生产证据](production-deployment-20261007.md)。2026-10-11安装 / 有限读取 / 收尾盘账取[原生服务配套](client-native-services-20261011.md#资源与安全清理)，清理后的最近盘账取下节；历史运行包F保全沿各发布来源，不以90秒刷新旧1,800秒，也不把十万合成数据当千万级历史证明。数据增长 / 新版本 / 实际故障触发重新预算，不自行购买或扩盘。

## 日备份与 F 盘外取

最近盘账取[2026-10-17备份清理收尾](../../../oms-server/oms-backend/doc_md/other/netdisk-layout-20261017.md#清理收尾)：当次根盘可用约7.74 GiB，原4.10 GiB恢复预留保持；这不是实时磁盘读数。应用发布及旧持续 / 恢复证据日期不刷新。

固定本地timer定义为每日04:15 CST、随机延迟至多300秒、Persistent=true；最新终态取分层归档记录。实际下一次触发时间随当时systemd状态读取，不承诺固定秒数。

2026-10-17两个云timer启用及最新真实成功收据取分层归档记录；timer启用不等于某次上传成功，失败记录必须核对。云端不自动裁剪历史；恢复旧平铺总目录时沿[分层定位规则](../../../oms-server/oms-backend/doc_md/other/netdisk-layout-20261017.md#路径与恢复引用)，实际操作和新Linux重建步骤取[全备说明](../../../oms-server/oms-backend/doc_md/other/full-backup-20261017.md#操作与恢复顺序)。本地每日快照的七天清理与云端保留分别执行。

日备份仍在 `/var/backups/oms-ir/daily-<UTC时间>.db.gz`，同名 `.json` 最后发布。固定 helper 只取一次真实 current，sidecar绑定当时运行 manifest及维护来源；旧 sidecar不改标签。只有完整核验的日备份对可按原 keep-days7清理，预算按八对计算；孤立件、失败件、手工恢复与发布前快照不当成合格 daily 自动删除。

1. 每次发布前 / 后、每周外取及故障时，从本次实际成功 InvocationID 的完成行识别准确对；核实已关闭 MainPID / ControlPID、真实退出状态、固定 helper、当前来源及峰值。oneshot终态峰如 `[not set]` 如实记null，不能填0或用末次采样冒充。
2. 完整 gzip / sidecar 直接传至 F 盘受保护新目录，逐件核字节 / SHA、完整 gzip EOF / CRC、raw size / SHA、integrity / FK、22表 / sequence / 索引 / trigger及来源绑定。目录只允许当前用户、SYSTEM、Administrators；个人原始行和凭据不输出、不进Git。
3. 真正恢复先在新空目录进行，冻结包 / 依赖与 fresh缓存独立还原，公开投影只读引用；签收正常读写、撤销 / 隐藏、全量榜 / 非空原生 / 分页及实际资源和F全件交接后，才准确退役自己的恢复数据。2026-10-08两轮已有完整证据，未变时不重复制造恢复副本。
4. SQLite一致备份仅包含业务库；全量公开投影、对应源码 / 依赖包和当前配置各有独立完整F来源，不拿241,664 B的真实业务raw冒充1.6 GB历史投影已保全，也不以只读投影代替账号 / 会话备份。

2026-10-08首次发布前后正式对、失败observer及旧恢复保全沿[原日期生产记录](production-deployment-20261007.md)。2026-10-11发布前后两次固定helper备份的准确来源 / Invocation、完整F核验与timer取[原生服务配套](client-native-services-20261011.md#新鲜固定helper备份与收尾)；后续备份与调度取本节分层归档记录，不把发布前后旧备份称为当前最新备份。后端[deploy](../../../oms-server/oms-backend/deploy/README.md)的旧静态命令和b520仅属历史；当前三服务同库回退取本页现行原生维护节，旧设计仍按下节2026-10-08原范围。

## 保留当前库的设计与源码回退

2026-10-08新→旧D1/e6→新已实际通过。恢复旧设计时保留同一业务库、当前UUID / 账号 / 会话 / 密钥 / 隐藏 / 社区及真实限流变化，不回灌旧raw。以下属于该次schema3兼容范围，后续变更先核当前实际状态和新兼容证据。

1. 完整保全当前实际配置、manifest、unit / timer状态和故障证据至F。暂停timer前记录其活动 / 启用状态，等待原worker关闭，以固定helper取得新一致备份并完整F核验。恢复串行，不能复用2026-10-08冻结绑定去执行未来发布。
2. 停当前主IR和新PHP后再核同一DB身份 / schema。旧全部定义保留；本次仅允许已采用的 `scores_directory` 与 `score_groups_public_directory` 两条普通目录索引，不因它们拒绝已证明兼容的旧源码，也不为过门删除索引或任何数据。出现其他结构差异时保全实际停点并向前修复。
3. F `production-before-switch-r4/08-39.105.55.78.conf` 与 `09-oms-ir.conf` 是当次旧设计路由底稿。未来执行时将旧设计必要路由合入操作前当前安全配置，保留状态页访问限制、当前BT Nginx绑定及受修复运行时；不能整份恢复这两份旧文件。候选配置检查后按正确mode原子替换，再切 current至D1/e6、启动旧主IR并核schema3健康。10月8日当次catalog源码未变且未停止；未来须按实际应用依赖同步处置，固定备份unit / helper保持。个人站、TLS / ACME不替换，合并后的新回退另行验证。
4. 用真实宝塔 `/www/server/nginx/sbin/nginx -t -c /www/server/nginx/conf/nginx.conf` 检查，再用 `/etc/init.d/nginx reload`。reload返回0不代表新规则已接收请求；有界检查实际HTTPS、旧主页完整manifest字节、IR / 社区 / 八插件和个人站，保留每次真实尝试。
5. 旧设计稳定后新PHP保持停止 / disabled；仅恢复事先保存的timer活动状态，核当前真实下一次触发时间。任一步失败保留实际服务 / 路由停点，不能宣称自动回退成功或用旧数据库消掉新记录。

本次第一forward曾在reload之后立即读到旧worker而误判，继而因未允许已批准两索引使自动恢复停在服务关闭；已独立恢复并修订，完整失败原件保留。正式R4同库往返及后续最终发布证明本节具体范围，不表示任意旧源码均兼容。

旧设计完整Git / 工作区差异 / 原发布 / 字体与两恢复只在 F:\zdamexy-workspace\oms\artifacts\oms-web-migration-20261007\legacy-r3；原D1/e6运行包在 F:\zdamexy-workspace\oms\artifacts\oms-deai-20261007。新包、两实际恢复、正式对、原旧配置和最终新配置均在 F:\zdamexy-workspace\oms\artifacts\oms-web-production-20261007；服务器只保留所需不可变运行 / 维护 / 回退目录，不另增旧设计备份。

## 真人验收

1. 普通浏览器打开首页并正常刷新，核新闻、菜单、桌面 / 窄屏，再到 `/download` 与 `/help` 按步骤进入游戏。公开发行仍为页面明确标注的20260626，开发工作区IR不冒充已发行能力。
2. `/beatmapsets?ruleset=bms` 搜索并查看详情，确认Ginger / 616自动推荐与人工换源，实际下载原包并在OMS入库打开；mania选对应玩法及Sayobot实际包，核原生mania / 混合包边界。
3. `/account` 使用原OMS账号，检查我的记录、真实公开个人页、密钥一次展示 / 归属 / 撤销。不要提交密码或token作反馈；旧LR2IR同名账号不认领为OMS。
4. `/ir` 先选难度表和表内难度，按字母 / 表内搜索找到曲目，再进入该单曲MD5榜；段位组合或缺失MD5只跳原表。按谱面选一个 / 多个 / 全部 / 空来源，比较分数、独立灯、人数、全局名次及跨页；参考混榜后主动收窄到真实存在的同条件。OMS原账号入口、个人页及选歌 / 本人记录中的实际谱面入口与网页同谱同范围对照。
5. 用户在VS Code非调试启动F:\zdamexy-workspace\oms，按上方固定 OMSIR 来源在原窗口直接注册 / 登录，手动完整保存新局；匿名可主动查具体谱面公开榜，退出停止新局归属捕捉。断网、重启、原账号重登及旧官方origin待交补交核UUID不重造、归属不变，其他origin凭据 / 待交不转移。旧osu! API地址空 / 在线false保持。先导P先验OMS＋全量公开历史＋ED7K，再继续指定beatoraja / LR2oraja / ED / OpenLR2版本与完整玩法 / 架构矩阵，实际交分和宿主原生读榜逐格留证。
6. 在同一开发工作区从独立新闻、帮助、玩家排行、个人页与谱面入口操作，按[当前原生合同](../../../oms-server/dev_bridge_md/doc_md/mainline/client-native-services.md#页面与导航)核真正原生页面 / 选中状态、排行→个人→原MD5谱面→榜或下载→返回。单一谱面列表先选 BMS / osu!mania；BMS 仅 Ginger Rush / 616，osu!mania 仅 Sayobot，切回 BMS 恢复上次来源；首次模式加载中关闭后旧页不再弹出，OMS 不作为客户端目录来源；只显示来源支持的搜索 / 筛选，在用户正常OMS窗口对照lazer，检查普通 / 大卡的实际排布、固定字号、长名 / 展开可读性和实际键型，跨顶部页、关闭重开及慢读取中切走后恢复各来源条件 / 阅读位置。Web 与桌面分别登录，网页分享和未知字段保持原边界。
7. 使用自己的真实社区内容，分别核网页与端内发帖 / 回复、本人编辑 / 删除及他人权限。端内检查长正文、换行、IME / 剪贴板 / 焦点与 DPI；失败或丢响应后重试原正文 / UUID，切账号或关闭页面仍保留原作者草稿。只有明确建立新提交才换正文或归属，核同一帖 / 回复没有重复创建；具体合同取[社区草稿](../../../oms-server/dev_bridge_md/doc_md/mainline/client-native-services.md#社区桌面认证与草稿)。
8. 对照网页新闻摘要 / 完整正文与端内文章、帮助段落 / 站内锚点，检查实际同源链接进入原生页，外部链接由主动操作打开。内容变更后的普通刷新与缓存读取沿[新闻维护](#新闻与内容维护)，软件 ETag / 304 结果不代签真实点击、阅读或输入体验。反馈注明所用开发源码或公开发行及操作时间；本节验收不生成 Windows 发行包。

生产普通浏览器与真人验收仍未签收；本地桌面 / 手机、刷新证据和用户此前的本地视觉认可保留原范围。2026-10-08～09 的公开 HTTP 数量、线上浏览器超时及无效视口尝试分别取 [首次发布](production-deployment-20261007.md#正式发布与收尾)、[文案审改](deai-review-20261009.md)、[难度表](bms-difficulty-tables-20261009.md)、[等级筛选](bms-level-filter-20261009.md)与[排行榜记录](rankings-layout-review-20261009.md)，本页不累计旧轮次结果。

遇到问题记录入口、操作、发生时间及页面提示，按反馈修复后只重验受影响范围。PP / 地力、聊天、presence、多人与官网谱包托管不在本次交付。
