# OMS 原版 osu-web 试运行维护

2026-10-08 原版网站已部署，状态 **已部署待验收**。玩家可从[首页](https://oms.zdamexy.work/)进入新闻、独立下载与帮助、谱面浏览、跨来源榜、账号、个人页、玩家榜和社区。真人下载入库、账号 / 密钥、OMS 对照及固定播放器 P/C 尚未签收。具体运行、恢复、失败与发布证据只取[生产记录](production-deployment-20261007.md#正式发布与收尾)。

## 当前来源与运行位置

| 对象 | 当前实际身份 |
| --- | --- |
| HTTP / 网页运行包 | `/opt/oms-ir/current` → `/opt/oms-ir/releases/b879e4233818-b0feceae22e4`，2026-10-08 20:35:11 CST 最终切入 |
| 服务源码 | Backend `b879e42338183bed3a5b7de057817152a23de46c`；账号、成绩、社区仍为 FastAPI / SQLite 唯一权威 |
| 原版页面源码 | Web `b0feceae22e4af55dc9c974f39e4b5f40a02bfd1`；保留原 Laravel / Blade / React / Less / Turbo，AGPL / 归属及对应源码下载公开 |
| 固定维护代码 | `/opt/oms-ir/releases/d1f052b93a81-22b4ee54f237`；日备份 unit 直接指向此包，不能随 HTTP 回退覆盖或当闲置目录清理 |
| 源码 / 旧设计回退目标 | `/opt/oms-ir/releases/d1f052b93a81-e6fdf914cb04`；原设计完整外存备份在 F 盘，服务器没有另打旧设计备份包 |
| 实际业务库 | `/var/lib/oms-ir/ir.db` / schema3 / 22表；本次保留同一 dev / inode，无生产 raw 恢复或样本数据迁入 |
| 全量公开历史 | `/opt/oms-ir/archives/lr2ir-v3-public-1-e8f5702701bb5382b93ec572815e07306b9017b124fee505152e47723ac0acdd.db`；只读25,562,325存储摘要 / 334,117谱面，其中25,560,957合格摘要，隔离行不参与榜 |
| PHP 环境 | `/opt/oms-web/runtime/php85-ed3f014e02a9`，Alpine / PHP8.5；独立 oms-web 用户，只读 `/app`，不升级宝塔共享 PHP |
| 本次可写缓存 / 日志 | `/var/cache/oms-web/b879e4233818-b0feceae22e4/production-r1`；`bootstrap`、`storage` 私有，PHP日志在 `storage/logs/fpm.log` / `php.log` |
| 实际 OMS 路由 | 宝塔 `39.105.55.78.conf` 与 `extension/39.105.55.78/oms-ir.conf` 配对；共享 Nginx、个人站、证书、ACME规则保留 |

上述 Web / Backend 是运行提交，文档 HEAD、历史取证提交及外置检查工具各自记录，不重标生产。客户端账号 UI 软件来源仍为 `6168791`，默认 endpoint 空、旧在线总开关 false；用户通过 VS Code 非调试启动 F:\oms 验收，不生成 Windows 发行包、publish 或安装副本。

插件沿原八个批准文件的完整字节 / 版本清单：beatoraja 0.8.8、LR2oraja build11611350155、ED v0.4.0、OpenLR2 v260915 x86 / x64。网页能下载插件不代表这些真实宿主已完成交分、原生读榜及玩法矩阵验收。

## 运行与资源核对

| 单元 | 固定预算和行为 |
| --- | --- |
| oms-ir.service | 500 MiB / CPU150% / swap0；loopback8081，按需 API |
| oms-ir-catalog.service | 96 MiB / CPU25% / swap0；loopback8082，仅批准源元数据；本次保留原 PID1862556，三源码文件已与新包核对一致 |
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

本次完整运行门最低可用内存560.957 MiB，swap / OOM零；两空恢复所有窗口、最大 main + WAL、源码 / 依赖 / 缓存、八对与额外2 GiB均已实测。最后恢复最低磁盘仅高于原底线6,162,952 B，原数保留。增长、新版本或真实故障触发重新预算；不自行购买或扩盘。最终实际空闲和瞬时负载取生产记录，不把十万条合成数据当千万级历史证明。

## 日备份与 F 盘外取

原 timer 保持每日04:15 CST、随机延迟至多300秒、Persistent=true；当前 enabled / active / waiting。2026-10-08实际恢复后下一次为2026-10-09 04:16:57 CST，这是当次 systemd 结果，不承诺以后固定秒数。

日备份仍在 `/var/backups/oms-ir/daily-<UTC时间>.db.gz`，同名 `.json` 最后发布。固定 helper 只取一次真实 current，sidecar绑定当时运行 manifest及维护来源；旧 sidecar不改标签。只有完整核验的日备份对可按原 keep-days7清理，预算按八对计算；孤立件、失败件、手工恢复与发布前快照不当成合格 daily 自动删除。

1. 每次发布前 / 后、每周外取及故障时，从本次实际成功 InvocationID 的完成行识别准确对；核实已关闭 MainPID / ControlPID、真实退出状态、固定 helper、当前来源及峰值。oneshot终态峰如 `[not set]` 如实记null，不能填0或用末次采样冒充。
2. 完整 gzip / sidecar 直接传至 F 盘受保护新目录，逐件核字节 / SHA、完整 gzip EOF / CRC、raw size / SHA、integrity / FK、22表 / sequence / 索引 / trigger及来源绑定。目录只允许当前用户、SYSTEM、Administrators；个人原始行和凭据不输出、不进Git。
3. 真正恢复先在新空目录进行，冻结包 / 依赖与 fresh缓存独立还原，公开投影只读引用；签收正常读写、撤销 / 隐藏、全量榜 / 非空原生 / 分页及实际资源和F全件交接后，才准确退役自己的恢复数据。本次两轮已有完整证据，未变时不重复制造恢复副本。
4. SQLite一致备份仅包含业务库；全量公开投影、对应源码 / 依赖包和当前配置各有独立完整F来源，不拿241,664 B的真实业务raw冒充1.6 GB历史投影已保全，也不以只读投影代替账号 / 会话备份。

本次发布前正式对和发布后正式对分别在 F:\oms\artifacts\oms-web-production-20261007\fixed-production-backup-pre-switch-f3f004b6adaa 与 `fixed-production-backup-post-switch-7be5768366c7`。两者完整核验且同实例运行观察通过。旧R6 observer false及其另行完整对保全仍保持，不能重标成功。后端原备份命令与权限说明见[运行维护](../../../oms-server/oms-backend/deploy/README.md)；其中旧b520回退段仅属原时点，本次回退按下节。

## 保留当前库的设计与源码回退

本次新→旧D1/e6→新已实际通过。恢复旧设计时保留同一业务库、当前UUID / 账号 / 会话 / 密钥 / 隐藏 / 社区及真实限流变化，不回灌旧raw。以下属于本次schema3兼容范围，后续变更先核当前实际状态和新兼容证据。

1. 完整保全当前实际配置、manifest、unit / timer状态和故障证据至F。暂停timer前记录其活动 / 启用状态，等待原worker关闭，以固定helper取得新一致备份并完整F核验。恢复串行，不能复用2026-10-08冻结绑定去执行未来发布。
2. 停当前主IR和新PHP后再核同一DB身份 / schema。旧全部定义保留；本次仅允许已采用的 `scores_directory` 与 `score_groups_public_directory` 两条普通目录索引，不因它们拒绝已证明兼容的旧源码，也不为过门删除索引或任何数据。出现其他结构差异时保全实际停点并向前修复。
3. 从 F `production-before-switch-r4/08-39.105.55.78.conf` 与 `09-oms-ir.conf` 原件恢复配对OMS路由，按原mode原子替换；原子切 current至D1/e6、启动旧主IR并核schema3健康。本次catalog源码未变且未停止，固定备份unit / helper保持。共享Nginx、个人站、TLS / ACME不替换。
4. 用真实宝塔 `/www/server/nginx/sbin/nginx -t -c /www/server/nginx/conf/nginx.conf` 检查，再用 `/etc/init.d/nginx reload`。reload返回0不代表新规则已接收请求；有界检查实际HTTPS、旧主页完整manifest字节、IR / 社区 / 八插件和个人站，保留每次真实尝试。
5. 旧设计稳定后新PHP保持停止 / disabled；仅恢复事先保存的timer活动状态，核当前真实下一次触发时间。任一步失败保留实际服务 / 路由停点，不能宣称自动回退成功或用旧数据库消掉新记录。

本次第一forward曾在reload之后立即读到旧worker而误判，继而因未允许已批准两索引使自动恢复停在服务关闭；已独立恢复并修订，完整失败原件保留。正式R4同库往返及后续最终发布证明本节具体范围，不表示任意旧源码均兼容。

旧设计完整Git / 工作区差异 / 原发布 / 字体与两恢复只在 F:\oms\artifacts\oms-web-migration-20261007\legacy-r3；原D1/e6运行包在 F:\oms\artifacts\oms-deai-20261007。新包、两实际恢复、正式对、原旧配置和最终新配置均在 F:\oms\artifacts\oms-web-production-20261007；服务器只保留所需不可变运行 / 维护 / 回退目录，不另增旧设计备份。

系统日志的46原件已完整保存并核验到F后，才按用户授权清理。默认namespace480 MiB加原OMS32 MiB，合计512 MiB；完整原件及失败传输保留F，不重复清理其他日志或其他私有目录。

共享主机变更分别在[Homepage记录](../../homepage-website/doc_md/other/shared-journal-budget-20261008.md)和[旧OMS Website记录](../../oms-website/doc_md/other/shared-journal-budget-20261008.md)留链接；原件与当前事实仍只由本次生产记录维护。

## 真人验收

1. 普通浏览器打开首页并正常刷新，核新闻、菜单、桌面 / 窄屏，再到 `/download` 与 `/help` 按步骤进入游戏。公开发行仍为页面明确标注的20260626，开发工作区IR不冒充已发行能力。
2. `/beatmapsets?ruleset=bms` 搜索并查看详情，确认Ginger / 616自动推荐与人工换源，实际下载原包并在OMS入库打开；mania选对应玩法及Sayobot实际包，核原生mania / 混合包边界。
3. `/account` 使用原OMS账号，检查我的记录、真实公开个人页、密钥一次展示 / 归属 / 撤销。不要提交密码或token作反馈；旧LR2IR同名账号不认领为OMS。
4. `/ir` 按谱面选一个 / 多个 / 全部 / 空来源，比较分数、独立灯、人数、全局名次及跨页；参考混榜后主动收窄到真实存在的同条件。OMS原用户按钮 / 登录页 / 个人页、选谱奖杯与网页同谱同范围对照。
5. 用户在VS Code非调试启动F:\oms，手动完整保存新局；断网、重启、原账号重登及旧待交补交核UUID不重造、归属不变。先导P先验OMS＋全量公开历史＋ED7K，再继续指定beatoraja / LR2oraja / ED / OpenLR2版本与完整玩法 / 架构矩阵，实际交分和宿主原生读榜逐格留证。

本次公网HTTP通过，浏览器工具读取线上页仍30秒超时，未取得线上DOM / 截图或普通点击 / 登录验收。用户已认可本地原版视觉；该认可和本地浏览器证据不提升为本次线上真人通过。遇到问题记录入口、操作、发生时间及页面提示，按反馈修复后只重验受影响范围。PP / 地力、聊天、presence、多人与官网谱包托管不在本次交付。
