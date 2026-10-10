# OMS 网络服务审查与优化（2026-10-11）

本轮按用户要求同时审查现 OMS Web、Backend 和 Windows 客户端的在线服务，目标是减少玩家等待、重复请求及共享主机的运行 / 流量负担。源码从客户端 `7d4d8fa9`、Web `a9bc3f1c`、Backend `69d9889c` 接续，实现分别提交为客户端 `f3b8a439f0354c2f9b20e8fc2a0ccd467db3dea0`、Web `f9a5afd99939e8a60e861debce4a5fb315eb21ad`、Backend `cc37bdb8f3b4e3cb60c2cf563f9054e389fbee24`；开工已有文档 / 构建脚本改动完整保全，本轮只归属新增代码和文档增量。共享Nginx只调整已压缩图片的gzip类型表，具体实施取下方；业务库、账户、TLS / 域名、服务限额或谱包托管边界保持。

## 已实施

- 网页 Turbo 换页复用当前标签页已确认的身份（含匿名），首次恢复、窗口重新获得焦点、跨标签页登录 / 退出与真正401仍重新核对。本人历史、密钥、本人名次与写入保持账号 revision、原 cookie Path 和 `X-OMS-Actor`；公开来源 / 谱面元数据 / 离线难度表独立于账号刷新。
- BMS 自动获取改为一次 `resolve=1` JSON 解析后直接导航到批准的 HTTPS 原包地址。旧307入口保留，原连通性探测、额度、错误及 no-store 保持；浏览器取消后不导航，不让 OMS 代理大包。形状与边界取[共同谱面合同](../../../oms-server/dev_bridge_md/doc_md/subline/oms-player-site/catalog-api.md)。
- 外源公开元数据同时冷读相同键时共享一次操作；各读取者独立 JSON，单人取消不影响其他人，最后取消回收共享任务，失败不缓存。两解析槽 / 两外源并发 / 20秒总期限、8MiB / 128项 / 120秒缓存不扩大。此取消证据属于提供器任务，未证明浏览器断开已自动传播至 ASGI。
- 客户端临时交分故障对原账号待交统一等待，避免逐条请求撞同一个服务故障；服务器 Retry-After 截止写入原待交文件，新局、同账号退出重登及重启不能提前发送。运行中的普通连接恢复仍可手动重试；恢复文件没有退避类型，未来截止保守保留。409 / 422只暂停相应记录，原 UUID / body / owner不改；JSON传输启用gzip / deflate，解压后读取预算继续受限。准确来源、软件结果和真人缺口沿[客户端状态](../../../oms/doc_md/subline/P3-IR/DEVELOPMENT_STATUS.md)与 Client Bridge 登记。

客户端采用 `client-ir-shared-retry` / `client-ir-json-compression`，来源先由[Client Bridge提交快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-ir-network-snapshot-20261011.md)确认，再进入[Dev Bridge共同IR约束](../../../oms-server/dev_bridge_md/doc_md/subline/oms-ir/constraints.md#范围与来源)，本仓与Backend只消费这些已确认边界。旧账号入口 / 其他事实、11待复核、阶段、真人与发行门不刷新。

## 可比较的请求量

| 场景与取证范围 | 修改前 | 修改后 | 含义 |
| --- | --- | --- | --- |
| 匿名首次进入后共浏览6个Turbo页面；旧代码路径计算 / 新Node VM模拟fetch回归 | 12次身份请求（每页me→refresh） | 2次首次身份请求 | 后续换页无需重复确认匿名身份；焦点 / 通知 / 401另算，不是实际浏览器水瀑 |
| 一次正常BMS自动获取；旧代码路径 / 同一模拟回归 | 2次下载解析，另先强制身份刷新 | 1次下载解析，无前置身份刷新 | 只统计OMS解析，不包含原主机下载和真正401恢复 |
| 同MD5两名冷读取者；旧提交与新工作区的MockTransport比较 | 4次外源请求 | 2次外源请求 | 实际两解析槽范围内减少50%，仍查两批准来源 |
| 同MD5二十名提供器并发读压力例 | 40次外源请求 | 2次外源请求 | 提供器合并证据；生产入口仍只有两槽，不宣称支持20个解析并发 |
| 现生产公开sources JSON；匿名真实HTTPS identity / gzip | 1847 B响应实体 | 496 B压缩实体 | 解压内容完全相等，该样本减少73.1%；不等于全站节省率 |

元数据比较仅报告实际请求次数；Windows计时粒度不足以支持本轮延迟提升结论。客户端压缩能力与网页 / 后端本地改动未部署，不把此表当作上线后总流量、CPU或延迟实测。原件在 `F:/zdamexy-workspace/oms/artifacts/network-review-20261011/metadata-before-after.json`、`production-readonly.json`，网页回归见下方日志。

## 本轮验证

Backend focused **52项**、完整pytest **353项**通过，原有Starlette TestClient弃用提示1条；覆盖旧307 / 新JSON / 地址拒绝 / 超额 / 失败、同键合并 / 独立对象 / 取消 / 失败后新读。原件为客户端审查证据目录的 `backend-focused.txt` 和 `backend-full.txt`。

Web `node scripts/verify-browser-api.cjs` 的10组Node VM / 模拟fetch回归、`npm run typecheck`、`npm run prod`通过。回归覆盖焦点、跨标签页、旧账号写入、401恢复、公开读取、SSR路径、解析失败 / 取消与有无浏览器锁；不是普通浏览器实际账号 / 水瀑签收。生产构建有3条既有资源体积提示，未因本轮扩大依赖。每个新shell先加载开发存储，Node / PHP 在现F盘WSL工作区，日志为 `artifacts/network-browser-api-20261011.log`、`network-typecheck-20261011.log`、`network-build-20261011.log`。

新资源已重启隔离本地Nginx / FPM / Backend / catalog，地址 `http://127.0.0.1:8090`，没有启动真实用户数据客户端。实际匿名HTTP首页和7件声明资源通过，收到压缩资源实体318,792 B；不含字体选择、CSS后代、JS API或真实浏览器绘制时序，首次328ms / 紧邻313ms仅属本机当次。记录为 `artifacts/assets-network-20261011.json`。

实际本地匿名HTTP5项通过：v2 sources200、me401、真实公开BMS详情200、新JSON下载解析200与旧307，均no-store且返回批准原主机，不做archive GET / 账号 / 写入；结果为客户端证据 `local-http.json`。真实后台浏览器查看首页 / 新闻 / 下载 / 有来源结果的BMS目录 / 真实谱面非空公开榜共5页，无console警告或错误。顶部链接等待曾超时，实际页内下载链接随后成功；帮助点击未导航，未签帮助浏览器。`browser-observation.json`保留工具限制，未验账号跨标签页、实际水瀑、窄屏、原包入库或生产DOM，创建的标签页已关闭。

客户端最终r7重新编译的七fixture **89/89**、普通Desktop Release / Debug均0警告0错误，默认owned handler / 实际JSON reader的loopback5例通过。真实账号切换回归曾暴露Release存储异常filter复用持锁标记导致锁未释放；改明确类型catch后同一2例及完整回归通过，所有中止、栈、IL / 工具链与指纹保留。原件、格式的既有Queue常量提示与新增格式修复、探针6条CA2007 / 自动审批清理拒绝、未签真人只在[客户端日志](../../../oms/doc_md/subline/P3-IR/CHANGELOG.md#2026-10-11网络服务审查与负载优化)完整登记。

工作区协作文档检查通过164件文档 / 1611条链接，客户端检查通过201件Markdown / 2144条相对链接 / 390个锚点 / 123条记忆引用。Client Bridge登记为15来源 / 30事实 / 79消费者，11待复核保持；原14来源与28事实对象逐项比较未改写。检查与保全原件为客户端证据目录的 `workspace-final-r1.log`、`client-docs-final-r1.log`、`registry-preservation.json`，检查对象为保留开工已有改动的当前工作区。

## 生产只读观察与未完成范围

2026-10-11 02:22 CST 实际 current为 `a85aee3e3c45-b17354d27c6b`，三服务active / running、NRestarts均0。主IR / catalog / Web瞬时内存分别63,307,776 / 43,397,120 / 54,112,256 B；共享可用795,975,680 B，swap使用0。两个公开主页实际HTTPS均200，现Nginx已开gzip、JSON在类型表、keepalive60秒。这次只读状态不代签1,800秒资源门或长期CPU / 带宽；随后图片gzip调整另见下节。

根可用磁盘4,495,077,376 B；扣除2026-10-08已核恢复预留4,402,384,384 B后，只余92,692,992 B（约88.4MiB）。新包、安装展开与回退保全须重新预算；不能以当前空闲内存或旧恢复门跳过空间检查，也不删除所需回退包或自行扩盘。首次SSH连接超时、远端缺rg的失败保留，随后只读重试成功。

本轮产品源码已提交、软件与本地HTTP / 匿名浏览器通过，应用尚未部署；生产继续使用上方旧运行包，共享gzip调整已生效。真实客户端完整游玩、原账号 / 旧待交 / 断网重启、网页跨标签页实际账号、原包下载入库和两端同谱同范围仍由[真人路径](production-maintenance.md#真人验收)签收；没有生成Windows发行物。Backend schema与备份格式不变，旧公开最佳、独立灯及原资格不变。

## 实际候选包与发布空间门（未通过）

已按原native发布器制作完整包 `cc37bdb8f3b4-f9a5afd99939`，绑定本轮三个实际源码提交，旧五插件 / 许可 / PHP环境 / schema3 / 只读公开投影保持。原编译器 / 发布器文件没有修改；本机wrapper只改变checkout / 收据输出目录，并以 `publisher-binding.json` 绑定原四脚本SHA。新编译绑定214输入 / 484资源，候选包73,675,695 B、SHA `d2b3a91d6c4173e1151ee2d8fddb08fb5d35322e7da4c72ff366fd48940390be`，准确包及收据在 `artifacts/network-production-20261011/package/`。首次空间脚本在生成包尚未结束时遇缺收据而退出，随后等待完整包成功后重跑，失败日志不改判。

03:08:58 CST只读复核现current、9696项旧不可变文件mode / 设备 / size、依赖和缓存分配、PHP原输入包SHA与实际4KiB文件系统。根可用4,525,359,104 B，恢复预留4,402,384,384 B后余122,974,720 B；保守额外峰值125,362,176 B，余量 **−2,387,456 B（约−2.28MiB）**。这属于具体包的安装估算门未通过，不是实际安装失败或声称精确缺盘量；目录、wheel / pyc、helper和缓存有保守额度，实际安装峰尚未测。

| 额外峰值组成 | 分配字节 / 取证身份 |
| --- | --- |
| 上传包 | 73,678,848 B，实际文件按4KiB圆整 |
| 变化regular文件（含对应源码 / 根manifest / 新资源） | 28,680,192 B，逐tar member按4KiB圆整 |
| 独立release目录 | 6,078,464 B，1072目录 / 每entry256 B保守估算 |
| ready / projection链接 | 8,192 B额度 |
| 独立venv | 14,114,816 B，旧同依赖实际分配参考 |
| 正式fresh PHP缓存 | 704,512 B，旧实际352,256 B的两倍额度 |
| 新Backend wheel / pyc | 1,048,576 B额度 |
| helper / 安装元数据 | 1,048,576 B额度 |

100,818,262 B相同逻辑文件具备硬链接的mode / 同设备 / size与旧manifest条件，但最终installer仍须逐文件重核实际SHA；没有把这些逻辑字节当实际回收。PHP23,341,985 B输入包已存在且SHA一致，不重上传 / 展开；正常八对备份已含在恢复预留，不重复加算。完整算法和结果为 `check-package-space.py`、`package-space.json` / `package-space-r2.log`，原文件map在客户端 `package-preflight-reference/`。

因此本轮未上传候选应用包、安装release、重启IR / catalog / FPM或切current；没有以删所需回退 / 日备份、压低恢复预留、扩盘或采购使门通过。后续先复核实际空间组成与有依据的峰值，再做新鲜固定helper备份 / F全件核验、受影响co-load与同库回退 / 公开门；原2026-10-08持续1,800秒和两空恢复保持原日期，本轮未重做。共享配置备份是13件配置原件，不能冒充业务库新备份。

## 共享图片gzip优化（已生效）

02:45 CST从实际公开首页 / CSS声明选取OMS PNG和Homepage社交预览JPEG，各读identity / gzip。91,824→91,334 B只省0.534%，32,040→31,853 B只省0.584%；解压SHA相等，样本没有反增，但二次压缩收益很小。PNG仅证明CSS声明，JPEG仅证明社交预览声明，不声称普通访问都会取图；延迟不推导CPU收益。原件 `oms/artifacts/network-review-20261011/public-raster-compression.json`。

02:52 CST完整保全13件配置 / unit / manifest及元数据至本机受保护F目录后，只在 `/www/server/nginx/conf/nginx.conf` 的 `gzip_types` 移除 `image/jpeg image/gif image/png`，保留文本、JS、CSS、JSON、SVG和原其他参数。修改前双站200，宝塔Nginx `-t` / 实际reload通过；之后双站200，两图片gzip请求返回原未压缩实体且与事前SHA完全相同，sources JSON仍1847→496 B、解压相同。符合[MDN压缩指导](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Compression)关于已压缩图片不重复压缩的原则；没有量化CPU百分比或全站流量收益。

03:14:11 CST最后复核13件静态文件的准确内容 / mode / owner，除上述gzip类型表外均与保全原件相同；current仍为原包，三服务active / running且NRestarts0。原件为受保护目录的 `final-static-configuration.json`，摘要为 `artifacts/network-production-20261011/final-shared.log`；这次静态复核不增加持续资源或业务恢复签收。

准确原件与结果在 `artifacts/network-production-20261011/production-private/before/`、`candidate-nginx.conf`、`after-nginx.conf`、`gzip-verification.json`，仅当前用户 / SYSTEM / Administrators可访问，未入Git。配置原SHA `31e39502ead97c790c75c7b82e727097a19eb485ce7cc3badf0b92c3bd0f283c`、新SHA `c1c7326a00aa7594eab98be371c85fdc208d59373f19a0e2ee8a979b2d8619d3`，mode0644 / owner0:0保持。回退时先保全最新配置，核当前SHA仍对应，再从F原件只恢复这条gzip类型表，执行宝塔配置检查、reload与双站 / JSON核对；不替换过时的路由、unit或业务库。本轮没有做该配置往返。共享事实同步[Homepage](../../homepage-website/doc_md/other/oms-network-readonly-20261011.md)与[旧Website](../../oms-website/doc_md/other/oms-network-readonly-20261011.md)。

## 后续按测量推进

先通过发布时的实际空间账和准确来源 / 备份门，才能测本轮生产变化；原持续运行、恢复和真人门保持各自日期。随后优先测有账号排行榜的SSR重复本人查询与难度表JSON每请求解析，再决定是否合并读取；不凭静态审查加私有缓存。vendor约534KiB、CSS约375KiB的未压缩构建提示需按页面水瀑 / 使用覆盖测量后处理，不能直接删上游资源。当前无idle轮询、聊天 / presence / 多人或谱包代理；继续保持显式查询、hash资源immutable及动态API no-store。
