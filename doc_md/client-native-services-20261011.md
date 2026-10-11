# OMS 端内在线服务配套与发布（2026-10-11）

## 2026-10-12客户端页面纠正

当前客户端 6381e120aea1ff63dfdd34ff0e9fe38ac05f1528 已将既有功能接到lazer原新闻 / 帮助 / 排行 / 玩家 / 谱面容器和独立工具栏，删除统一面板。client-native-service-pages、client-native-community-owner、client-native-content-cache 以[新快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-client-native-pages-snapshot-20261012.md)及[共同合同](../../../oms-server/dev_bridge_md/doc_md/mainline/client-native-services.md)为当前采用。结构化内容与现有API足够，本轮未改Web / Backend代码、内容资源或生产部署；下方发布 / 运行 / 备份只属2026-10-11原版本。真实画面 / 账号 / 原包 / 整曲、P-C / 发行未签收，聊天 / 好友 / 在线状态后续。

## 2026-10-11服务配套来源（历史）

当时客户端统一面板源码 f2b495f41c0c20f8f81754339281b26e256e3d03（功能58454332）提供本文原接口消费者；其画面已被用户实测否定，现行页面只取顶部新来源。原[2026-10-11快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-client-native-services-snapshot-20261011.md)与软件保留原范围，不能签当前原生体验。

Web 运行源码为 `494932756b747edba791fd1499b83348ec49b963`，Backend 为 `824de121a6862d2f9b576f66a18715192fd0d57f`。本次没有 Windows 包；公开 20260626 客户端的发行范围不提升。真实窗口、IME / DPI、实际账号与下载入库、整曲 / 重启及固定宿主 P/C 继续由用户验收。

## 实现与请求预算

- `GET /client-content` 使用当前 `resources/oms/news.json`、`resources/oms/help.json`，新闻 / 帮助网页也读同一份内容。纯文本 v1、256 KiB、ETag 与 public max-age=300；损坏资源明确 503 / no-store。
- 客户端只有打开页面、切筛选、翻页或主动刷新才读取，不启动预抓或空闲轮询；内存内容有效期最多 300 秒，过期条件读取 / 304。服务器不保存第二份用户或密码库。
- 社区六个原 POST 复用统一鉴权，桌面 Bearer 与网页 cookie / Origin / Actor 各守原边界；作者、字段、限流、UUID 幂等和 schema3 不变。草稿归属、原正文重试与错误收据只取共同合同。
- BMS 按原 MD5 交既有 Ginger / 616 下载管理；mania 明确为 Sayobot 歌名候选。大包直达批准原站，OMS 不代理谱包；默认内部链接进入原生页面，明确网页访问和分享地址保持。

帮助及 IR 试运行文章同步固定 OMSIR 的直接登录说明，移除旧启用 / 填地址 / 保存连接步骤；未登录可主动读公开榜，成绩先保存、待交保留原账号，网页和桌面需分别登录。

## 本地软件证据

Backend 社区 / 鉴权 / 浏览器 Actor 聚焦 68/68，全套 367/367；原 Starlette httpx 提示保留。Web Laravel 实际 kernel 194 项、PHP8.5语法、原本地 HTTP 56 项与新增完整传输 32 项通过，覆盖 JSON 同源、gzip / ETag / HEAD / 304、稳定帮助锚点及合成桌面六项写入 / 幂等 / refresh / logout。仅本地合成账号，不写生产内容。

客户端准确命令、最终有效构建、各范围通过 / 原失败及独立基线结果只维护于上述来源快照，软件证据不代签真人。网站发布也不刷新原 1,800 秒运行 / 两空恢复日期。

## 生产发布与闭环

**已部署待真人验收**。最终切入 2026-10-11 16:34:47 CST，本轮完整收据核验 2026-10-11 16:37:19 CST；current为 `/opt/oms-ir/releases/824de121a686-494932756b74`，直接上一版 `cc37bdb8f3b4-f9a5afd99939`。包为 `oms-native-824de121a686-494932756b74.tar.gz`，73,701,928 B / 9,705运行输入，SHA256 `fe4e244dbee0775f23feb17803231d6fc3c48fa09fee473e3d43d82518f2c850`。Web与Backend完整来源见顶部；manifest中的client_commit仍绑定功能提交58454332，后续客户端f2b495f4仅5文件空白格式修正，并在最终格式源码重新双配置构建 / 跑301例，不冒称服务器包已重打或含客户端运行程序集。

### 准确发布、公开内容与同库往返

- 发布前后各13件配置 / manifest原件完整保存至受保护F目录，逐件SHA / mode / UID / GID核对；只更新IR、catalog、Web、cache四unit与OMS include五件绑定，新增精确 `/client-content` PHP位置。其余路由、两个站点、TLS / ACME及固定D1/22b备份unit完整保持；宝塔指定binary / config检查及init reload通过，实际响应验证安全头和单一public300缓存头。
- 安装、第一次切新、同库回旧、最终切新均保留真实有限资源窗。三次切换全部同步重启主IR、catalog、PHP，生成各目标独立正式缓存；同一DB dev64771 / inode265517、schema3与结构SHA保持，22表 / 18索引 / 8trigger，没有raw回灌。旧 / 新各10项公开scope哈希相同（来源全部 / 指定 / 空、分页、BMS / mania玩家榜及registry）。
- 41项公开HTTP通过：旧页面 / API、全部当前散列资源与公开对应源码、八插件字节、许可证 / 归属、无认证与私有目录边界及OMS / Homepage双站HTTPS；未下载1.6 GB公开历史投影。另8项内容HTTP通过：真实gzip / HEAD、strong / weak / list / star ETag与bodyless304，完整news / help正文等于包内共享JSON，8个帮助ID及安全头 / no-cookie身份保持。
- 90.0006秒实际两路匿名读同时运行，普通PHP45次、IR45次，另记录同MD5并发2读及后续温缓存。实际完整来源返回的first2 / 后续body相同，三个PID与Invocation稳定；内容有界缓存 / 304通过。有限90秒不签全站50人持续容量、外站实际出站次数、ASGI取消或长期流量。

### 资源与安全清理

| 实际窗口 | 观察秒数 / 采样 | 最低可用内存 B | 最低可用根盘 B | 共享CPU窗口均值 |
| --- | --- | --- | --- | --- |
| install | 36.03 / 180 | 718,299,136 | 4,423,434,240 | 28.12% |
| forward-1 | 13.36 / 67 | 764,846,080 | 4,424,704,000 | 25.10% |
| co-load | 96.73 / 482 | 785,633,280 | 4,415,959,040 | 4.04% |
| rollback | 14.01 / 70 | 791,289,856 | 4,415,324,160 | 21.86% |
| forward-2 | 14.15 / 71 | 806,244,352 | 4,415,164,416 | 22.47% |

上述各窗无swap / OOM / 非预期重启，始终高于4,402,384,384 B原恢复预留。分unit有限采样最高为IR 111,108,096 B、catalog 43,003,904 B、PHP 37,294,080 B、cache 49,958,912 B；它们是采样值，不冒称不可读oneshot终态MemoryPeak。安装前估计追加峰值125,526,016 B、沿实际空间重新核算；各窗口数据不宣称百分比性能提升。

发布前首次空间门差8,719,872 B而停止。完整386文件 / SHA / UID / GID / mode及2闲置FIFO元数据到F保全后，精确退役9个20261008 incoming取证目录；49个已退出 / 失败、无PID / 退出命令 / 触发器的旧瞬态取证unit定义也完整外取后清退。原业务库、所有当前 / 上一版 / 固定维护 / 旧设计 / B0 / FFF / 479运行目录和备份均保持。该步实测根盘增加 14,602,240 B（不是逻辑13,799,055 B）；收据 `production-private/idle-evidence-retirement.json`。

完成发布 / 两备份 / timer后核907个已加载unit定义和进程FD均无引用，F完整同SHA包仍在，只退役本轮incoming的73,701,928 B重复gzip，实测增加 73,707,520 B。两清理步骤观测增量之和 88,309,760 B（84.22 MiB），不将期间安装 / 缓存 / 日志变化混成净释放量。收尾根盘 4,488,687,616 B、原预留 4,402,384,384 B、余 86,303,232 B；增长触发重新预算。发布收尾时本机12个基线bin / obj删除被自动审批策略拒绝；随后用户清理、只读复核12/12不存在，保全与容量口径取[客户端清理补记](../../../oms/doc_md/subline/P3-IR/CHANGELOG.md#2026-10-11用户清理基线编译输出复核)，不并入上述服务器清理量或刷新生产日期。

### 新鲜固定helper备份与收尾

两次固定维护helper直接取当时真实current，准确成功Invocation分别 `8d6ba9cf856945ec9f6dd53b22b35d36` 与 `d1d60b33f17f4e3ea5077cbee50c741b`，核验时间 2026-10-11 15:40:37 CST / 2026-10-11 16:35:44 CST；来源分别旧 `cc37bdb8f3b4-f9a5afd99939` / 新 `824de121a686-494932756b74`。每对gzip9,063 B / raw241,664 B在受保护F目录完整核EOF / CRC、gzip与raw SHA、integrity / FK / schema3、22表 / 18索引 / 8trigger和来源；未输出个人行或凭据。终态MemoryPeak为 `[not set]`，如实不可用。

timer最终enabled / active / waiting，收尾实际下一次 `Mon 2026-10-12 04:17:32 CST`；不承诺以后固定秒数。未来同库回退必须重新备份 / 保全最新配置，再参照[当前维护](production-maintenance.md#当前原生服务维护与回退2026-10-11)同步恢复三服务；原2026-10-08的1,800秒和两空恢复未重复，旧证据日期不刷新。

### 原失败与证据边界

包编译首次默认WSL入口 `--cd` 不支持，旧编译收据不能匹配当前提交，均在安装前停止并留原日志；改为指定oms-web-dev与PHP8.5 / 锁定Node真实编译，214来源输入、484编译资源逐项绑定，3条原Webpack资源尺寸提示保留。本轮实际前端资源与旧部署hash相同，正文 / controller / PHP运行输入已换新来源，不能凭hash相同冒称未编译。

闲置目录外取前因2特殊FIFO、systemd无实例模板及已退出取证引用先停止，完整原件和修正r4收据保留；首次共载在约8秒的“全部200都应温缓存相同”断言失败。catalog合同允许部分来源失败返回200且不缓存；首次body未留，因此不确证该次是哪一源失败。验收helper改为先保存实际body / source状态，完整返回验证温缓存，部分失败验证下一次手动重读，新90秒窗口各来源完整成功且缓存不变。首次失败未重标成功、不宣称本轮证明了部分失败的实际生产分支；该边界软件检查另留原来源。

重复gzip第一次定点清退因systemctl将 `-.mount` 当参数停止在删除前，原日志保留；加参数终止符后重新核所有unit / FD / SHA，r2准确收据成功。旧公开源码 / 压力 / 恢复及此前网络清理不记成本轮新增；软件 / 有限实际HTTP不代签真实Windows窗口、账号 / 社区写入、IME / DPI、原包入库 / 整曲和P/C。


本轮证据根：`F:/zdamexy-workspace/websites/oms-web/artifacts/native-services-20261011/`。原配置 / 库备份留受保护 `production-private/`，不进 Git；源码、包和各有限窗口分别绑定真实身份。
