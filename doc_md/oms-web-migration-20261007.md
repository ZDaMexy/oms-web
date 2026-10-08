# 原版 osu-web 本地迁移（2026-10-07）

## 决定、来源与当前状态

用户确认“开始本地实施，暂不部署”，要求接续原项目并裁掉不符合 OMS 能力的部分。新仓 [ZDaMexy/oms-web](https://github.com/ZDaMexy/oms-web) 最初为空，通过非浅克隆导入完整上游祖先；初始上游 `2c596022a1345fbed288978e7fa5304df0359f50`，在线 master 当次 `a09a1750e9a1fc47e0f3e266edbcda9de3f29ed1`，不盲目同步。旧参考目录不修改。

当前原版站 **已部署待验收**。2026-10-07 用户随后反馈“效果很好，那部署？”，确认本地效果并授权生产部署；2026-10-08 已实际上线。准确来源、维护与未完成真人门只取[维护说明](production-maintenance.md)，实际发布及各轮失败取[生产记录](production-deployment-20261007.md#正式发布与收尾)，不重标下方本地证据。

[正式官网](https://oms.zdamexy.work/)的玩家范围见 [OMS.md](../OMS.md)；原[本地入口](http://127.0.0.1:8090/)继续仅用于隔离测试。网站以原 Laravel / Blade / React / Less / Turbo 运行，无 MySQL / Redis / ES 或实时服务。

下方记录适用于 2026-10-07 本地迁移阶段：当时旧生产 `d1f052b93a81-e6fdf914cb04` / schema3 保留，没有观察或修改服务器，新仓尚未部署。旧静态适配没有获得用户视觉认可，其历史运行门不证明新仓完成。生产阶段另行留证；启动和当次恢复流程见[本地说明](local-use-and-recovery.md)，统一阶段取 [Dev Bridge](../../../oms-server/dev_bridge_md/doc_md/mainline/dev-plan.md)。

## 基线与已有工作保全

开工在线 fetch 后旧 Website `4bc0b44d330301b6ec562c782a201aa00f3b238a`、Backend `5cdcb9287e9d80d2d2c03795fd4c987b9edf1a0b`、Dev Bridge `e4702c1c2c9ab745c4426e4dfa49b21e1f4b59eb` 均对 origin 0 / 0，原 16 / 14 / 17 路径差异保留。客户端 master `e4bbcae5c281420fba6796ec63df24febd4135d2` 干净，本轮未改客户端或生成发行物。开工水位不等于生产水位。

客户端继续保留[原 lazer 用户按钮、登录窗口和个人页复用合同](../../../oms-server/dev_bridge_md/doc_md/subline/oms-ir/constraints.md#范围与来源)。本地新网站不替代这一要求，也不签收客户端界面和账号真人门；后续沿现有 Client Bridge 来源核对两端。

新仓在 main。Backend 本轮只增加网页身份断言及其行为回归，选择性提交 `b3ac16c`；Dev Bridge 同步采用和新仓导航，选择性提交 `86f096d`。旧治理移动 / 删除、旧设计差异及其他产品不纳入本轮提交。新仓最终提交与跟踪由收尾实际Git记录，源码、恢复时水位和生产各自保留。

## 原项目裁剪与玩家路径

| 范围 | 当前实际行为 | 未完成或没有的能力 |
| --- | --- | --- |
| 首页 / 新闻 / 下载 / 帮助 | 原新闻首页和 sidebar、原桌面 / 移动导航；两篇有日期的真实新闻，独立下载和入门，旧 `/#download` 跳转 | 公开 20260626 未含 IR；不制造玩家动态 |
| BMS | Ginger / 616 原分页、MD5详情和批准原站下载路由；榜单不依赖目录可用性 | 不托管大包，真实下载入库待真人 |
| mania | Sayobot mode3、键数筛选、sid详情和原下载；已知 MD5 保留实际 sid，缺关联如实说明 | 实查 DARK ROM SYNCER / sid2009238 缺 MD5，不伪造同谱榜 |
| 谱面榜 | 完整索引、单 / 多 / 全 / 空来源、独立灯、全范围名次 / 人数 / 分页及主动同条件 | 不拼 TopN；未知字段、原灯和 LR2IR旧身份保留 |
| 账号 / 个人 / 密钥 | 原登录弹层、个人页和账号表单；本人 BMS / mania UUID全历史、公开最佳、一次显示的秘密 | 私人记录不公开，不按同名合并旧账号 |
| 玩家榜 | 原排行 Blade接真实收录 / 通关和 mania累计公开最佳分 | 没有 PP、地力、等级、国家或能力评级 |
| 社区 | 原列表 / 帖子 / 编辑器外形承载纯文本；本地真实发帖回复、作者管理和运营隐藏 | 无富文本执行、上传、聊天或在线状态 |

删除无真实能力的路由、模型、任务、全局初始化和构建入口。闭包实际报告在 `artifacts/pruned-*.json`：保留 JS / Coffee / 类型 76 个不同文件、BEM Less101、Blade39、app类14；另移除未使用上游数据库 / 测试 / Docker / 工具文件1,025个。删除数量不代替产品验收。

Torus / Venera七个未引用原字体文件已逐文件核对原 HEAD 字节后移除，指纹取 `artifacts/pruned-unused-fonts.json`；当前字体为 Inter 与 Font Awesome。AGPL、原作者归属和依赖许可保留；原说明逐字节保存于 [UPSTREAM_README.md](../UPSTREAM_README.md)。原发布CI删除，新只读检查不含部署。

## 数据与身份

现 FastAPI / SQLite 是账号、成绩和社区唯一权威。cookie Path仍为 `/api/ir/v1`、HttpOnly、同源写；PHP不维护认证session。候选 `X-OMS-Actor` 只断言已认证规范账号，旧A页面遇B cookie返回409 `actor_changed`、无写入；无该头旧调用和Desktop保持。合同见 [玩家 API](../../../oms-server/dev_bridge_md/doc_md/subline/oms-player-site/player-api.md#网页写入身份断言2026-10-07)。

退出 / 换账号 / 跨页清理私人内容和一次显示的秘密；迟到响应不能回填。社区草稿绑定原账号与UUID，重试保留ID，换账号需主动重建。OMS UUID新局、外部最佳更新、LR2IR历史摘要分别显示；不补造局ID、缺字段、未知灯或旧身份归属。

本地仅新建隔离库 `.dev-cache/local-runtime/live.db`，合成账号、OMS / ED成绩和社区都在此库，未迁入生产账号，不作为公开活动宣传。只读引用批准投影 `F:/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db`：1,600,610,304字节，SHA256 `a25a5f8b38d62fc32a9630e653a5eedf5ed127882dcae9941fad36f90c9108bb`，334,117谱面 / 25,562,325摘要。母库和其他私有数据未访问；恢复包不复制投影。

## 原设计保全

完整保全只在 `F:/oms/artifacts/oms-web-migration-20261007/legacy-r3/`：Git bundle、当前原始工作区 / 16路径差异、HEAD、实际发布包及对应源码、最早介绍页 `e8b764bcbbc9a7c25c330f5a6b144692bb374dd5`。两个新空目录实际恢复核对：132当前tracked文件和原介绍页五文件字节一致，原工作区未改变。`recovery-report.json` SHA256 `398f08efb1a0e9bd8bdc685697308aabba746a38488f402331e035dc0d0d9d91`。

r1 / r2的LF与archive autoCRLF失败保留；r3用明确LF archive修复，不忽略差异。Google Fonts另保全234唯一文件 / 10,115,348字节及四份官方OFL。首轮网络失败保留，第二轮使用进程内既有本地代理；原归档不改，单独离线恢复副本覆盖链接。不能证明今天取得的是六月字体历史原字节。设计回退保留当前账号 / 成绩库，不用旧库覆盖。

## 本地环境与软件检查

专用WSL `oms-web-dev` 的VHD实际位于F盘 `.dev-cache/wsl`。Alpine3.24.2 rootfs SHA256 `c5ca053cfe1d85c5b96dff8b9bc57045f7f184a30ffb6b65776409ca90388677`；PHP8.5.11、WSL Node24.18.1、Windows Node24.13.0、Python3.14.8、SQLite3.53.4、Nginx1.30.4，恢复manifest记录同一现存OS版本。未启动Docker或迁移其他WSL；每个开发shell先存储入口。

Nginx一个worker、PHP-FPM按需最多两个 / 96MiB、OPcache32+4MiB，加现backend和独立目录worker，只监听loopback。每次启动重建 Blade / 配置缓存并通过一次实际本地页面暖检查；运行时不逐请求查模板 / PHP文件时间，源码更新后必须重建并重启。HTML no-cache、hash资产immutable、Turbo无页面cache / prefetch。

API由Nginx直接接固定服务，移除未被实际使用的通用PHP代理；PHP只提供八个白名单适配器且不转发身份。原八文件从受保护旧包取得，SHA不变；未知文件404，PHP / 点文件拒绝，超限JSON413。实际适配器 GET / HEAD / Range206 / ETag304 / 越界416已逐项验证，证据 `artifacts/adapter-http-gates.json`。

| 检查 | 实际结果与证据 |
| --- | --- |
| Composer | 原Laravel13.26.1被 `PKSA-d5tc-s1qs-h781`拒绝，锁到13.35.0，无dev安装通过；不跳过漏洞或平台检查 |
| npm | Coffee2.7 / loader5对齐、qTip同commit codeload，修有依据依赖。Bootstrap3仍有moderate提示，仅用CSS、不启用JS；不称零漏洞 |
| 前端 | 最终typecheck / production r10通过，有三项包大小建议；r9实际交互通过后仅清理34文件的EOF多余空行，重新构建的442资源（含manifest）逐文件字节与r9完全一致，证据 `artifacts/whitespace-r10-*.json`。启动重编当前视图 / 配置并实际暖检查通过；误用不存在的build script原失败保留 |
| 后端 | 337通过 / 105.67秒，一项Starlette/httpx弃用；正式temp在F-backed VHD。r1 DrvFS捕获失败、r2慢600请求跨过60秒的配额断言失败保留，未放宽配额 |
| 实际HTTP | `artifacts/http-gates.json` r7：56项通过 / 47.491秒；完整投影 / 末页 / 来源条件 / Cookie / 私人UUID / 换账号409 / 密钥撤销 / 社区 / 全部分类搜索 / 适配器 / 413 / 路径 / 缓存；不是fixture |
| 浏览器 | 桌面与390px实际登录、本人UUID / 公开最佳、空 / 多来源 / 同条件、真实源详情、发帖回复、退出清理；502后普通跳转会清除提示。截图 `artifacts/*.jpg`，当次检查没有代签用户视觉；后续用户确认本地效果见本文当前状态 |

HTTP r4人数断言误以为重复测试前无合成账号，改为核验实际完整集合 / 自己条件，原失败保留。旧NavButton初始化错误移除，旧7:21日志不删除；当前无新增该错误。目录SSR重复、mania筛选刷新 / sid、社区编辑器 / 时间 / 窄屏搜索、账号样式、恢复提示都按实际故障修复。

首次导入历史并推送源码后，远端Actions已启用、工作流active，但未产生运行记录；原因未确认，不猜测成通过。新增手动检查入口后，源码 `29ea4f5046` 的[实际远端检查](https://github.com/ZDaMexy/oms-web/actions/runs/37615589952)已success：干净Ubuntu checkout、Node24 / PHP8.5、锁文件安装 / 漏洞检查、类型 / 生产构建、PHP语法及Blade / 路由检查均通过。工作流仅contents:read，不含部署、私有投影或凭据；本地完整历史与HTTP门仍取其独立证据。收尾仅文档变化不重标这次CI的源码水位。

实际浏览器另核过期下载：仅将已知合成账号的访问会话设为过期、保留刷新资格，停止本任务目录worker后点击自动下载。真实刷新旋转恢复登录，目录503留在谱面页提示错误；换来源清理错误并恢复按钮。`artifacts/expired-download-gate.json` 与 `expired-download-desktop.jpg` 留证，没有下载外部大包，不能代签真人原包入库。

r9又实际复核社区默认“全部分类”搜索、手动 Ginger / 616 返回“自动”及删除参数、帮助页当前站点与原账号保存后登录顺序。离页取消使用真实API的307，加本地受控延迟：目标尚在加载时取消请求并恢复按钮，迟到回应不触发第二次下载导航，最终显示真实新闻页。`artifacts/download-navigation-gate.json` / `download-navigation-events-r2.jsonl`留证；第一轮因工具定位超时晚点导航的检查失效和helper端口冲突日志均保留，不作为产品通过依据。临时helper已停止，原Nginx配置已恢复；没有下载原包或访问生产。

r10最终原工作区已重新启动并实际暖检查；浏览器退出隔离测试账号后显示匿名主页，普通reload仍为当前新闻和入口。桌面及当前窄侧栏截图为 `artifacts/home-final-r10.jpg` / `home-final-visible-r10.jpg`，验收页已保留在浏览器。本地普通刷新分项不代表用户视觉认可、生产缓存已修复或下载入库通过。

## 持续资源与本次新站恢复

完整本地读写和突发测量已执行1,801.445秒，采样覆盖0.004～1,801.260秒：5,159次请求、40次写入、6,332次采样、零失败，`complete=true`。证据为 `artifacts/local-performance.json` / `local-memory-samples.jsonl`。初轮/proc右括号解析失败、第二轮为修页面主动中止的141.415秒部分观察均保留incomplete，不缩短计时冒充通过。

第三轮虽执行1,801.967秒，1,151请求中有一次回复429，HTML p50约2.4～2.7秒；完整门为false，保留 `artifacts/local-incomplete-r3-*`。原因分别为现有20回复 / 600秒限额与逐请求文件检查开销。没有放宽服务限额；最终负载按45秒写一次，仍每2秒读七条路径、三次八并发24请求突发，并显式缓存当前源码。最终报告还要求采样覆盖至至少1,799秒。

网页进程组PSS峰值33,208KiB（32.43MiB），低于候选200MiB；backend94,843KiB、目录worker45,916KiB。CPU平均占一个核心的3.274% / 5.924% / 0.109%。RSS来自 `/proc/stat`，与较晚读取的smaps PSS及内核RSS近似计数不同，不把它们当成同一瞬间的精确物理占用。首页p50 / p95为231.531 / 342.078ms，完整IR索引1,055.669 / 1,467.651ms，混榜177.772 / 267.792ms。Alpine WSL / F DrvFS不等于生产或cgroup，`production_host_gate=false`；不能替代共享主机内存 / 系统盘 / 延时门。

这轮容量观察冻结在production r8，对七条实际HTTP路径测量，不执行浏览器JS。随后r9修正下载来源 / 离页取消、说明及社区空分类参数，分别重新构建并运行实际HTTP / 浏览器检查；不得把r8测量说成r9全部交互或浏览器绘制容量已通过。

收尾r10仅移除源码EOF多余空行并同步文档，类型检查与实际生产构建重新执行，全部442构建文件和manifest与r9字节一致。两恢复包保留捕获当时的工作区字节；其Git HEAD和成功报告不会重标为后来提交或r10整树恢复。r9实际HTTP / 浏览器 / 恢复仍对应当时的源码，当前运行资源一致性由新构建的逐文件比较另证。

最终r9的 `artifacts/assets-final-r9.json` 实际首页两次254.192 / 262.957ms，七个HTML声明资源的gzip实体312,377字节，全部构建资源1,018,697字节。此前缓存r2报告仍保留。最初启动后首次编译仍需数秒，成本由启动检查明确记录，不宣称物理冷缓存；上述资源不含CSS子字体 / 图片、JS触发API、懒资源与浏览器绘制。普通刷新、实际用户网络与主机首请求仍待对应门。

新站第一轮新空恢复已通过：`F:/oms/artifacts/oms-web-migration-20261007/local-native-restores/r1` 实际还原11,599文件并逐项核SHA、SQLite完整性与只读备份不变；启动实际HTTP后687项 / 648请求通过，236.106秒。原包111,370,240字节，SHA256 `b32b51486198300812136c9fd48c90ed4ebfcac77ad59fbacacbcbe0881be046`。证据为目标 `restoration-report.json`、`websites/oms-web/artifacts/recovery-http-r1.json` 和原工作区 `artifacts/recovery-memory-r1.json`，不是OS重装或真人签收。

最大公开谱面 `f8dcdfe070630bbb365323c662561a1a` 含29,204摘要，其中两条quality_flags=4隔离；实际参考榜29,202独立旧身份 / 585页均逐页核对完整集合、原分、全局名次、未知时间与原灯，未按TopN拼接。聚合选取只读完整公开投影，未导出个人行或访问母库；证据 `artifacts/largest-public-board*.json` 与r1 HTTP报告。期间服务PSS峰值网页36,924KiB、backend56,459KiB、目录47,031KiB，取同一smaps rollup的PSS / RSS，一秒采样；仍不签生产预算。

第二轮新空恢复也已通过：`F:/oms/artifacts/oms-web-migration-20261007/local-native-restores/r2` 实际还原11,599文件、核对五个符号链接与SQLite完整性，备份未变；启动实际HTTP后688项 / 648请求通过，235.867秒。r1 / r2的文件恢复分别耗时998.306 / 993.071秒，包含实际DrvFS写入、逐文件SHA和完整归档核对，不是内存解包。第二轮仍实际核过最大榜的585页和完整公开投影；混合索引334,118谱面含一个本地测试谱面，公开投影本身仍为334,117谱面 / 25,562,325摘要。

第二轮实际固定旧读事务，主文件撤销 / 隐藏仍为0，WAL及一致备份为1，主文件SHA未变，`baselineCheckpoint=[0,0,0]`；r2包SHA256 `03f84faff232c700e650948467dccce840af4848849eac09ab921c896b60a5c3`。恢复后已撤销秘密被拒写，隐藏帖子及其回复不可读改，维护审计保留。证据为第二目标的 `restoration-report.json` / `websites/oms-web/artifacts/recovery-http-r2.json` 和原工作区 `artifacts/recovery-memory-r2.json`。期间一秒采样237次、观察器无错误，PSS峰值网页33,304KiB、backend56,792KiB、目录47,104KiB；不签生产预算。

命令和范围取 [恢复说明](local-use-and-recovery.md)。快照 / 状态 / 新目标均在仅当前Windows所有者和SYSTEM可访问的F盘目录，实际11处NTFS权限核对取 `artifacts/recovery-acl-final.json`，不能用chmod代签。两个恢复实例已用自身入口停止；文件恢复、实际HTTP、同一现存OS和真人分别记录，不称两次OS重装。

最终原工作区四服务的实际PID归属及两个恢复目录无残留master已核对，取 `artifacts/handoff-runtime-r2.json`。第一份临时收尾探针误要求停止后的Nginx PID文件存在，遇正常删除而失败；原探针与错误记录保留在 `.dev-cache/temp/verify-handoff-processes.py` / `artifacts/handoff-runtime-r1-failure.txt`。修正后按原工作区PID和恢复目录实际进程命令行核对，不重标原失败，也不把检查工具问题当网站故障。

## 未完成门

本轮授权及原生运行环境、生产切换、预算和新恢复门取 [生产迁移记录](production-deployment-20261007.md)。生产事实单独登记，不重标本地历史证据。

本地视觉已获用户认可；生产普通刷新、真实BMS / mania原包下载入库、真实账号 / 一次秘密、自己 / 他人 / 旧身份及OMS同谱来源 / 条件 / 首末页仍待真人。客户端由VS Code非调试启动。指定ED7K先导P后完整固定宿主 / 30玩法C未签收，单插件或合成成绩不结项。

最初本地实施按“暂不部署”完成，未部署事实仅适用于该阶段；2026-10-08 已部署的结论取[正式收尾](production-deployment-20261007.md#正式发布与收尾)。后续沿[现行维护与真人路径](production-maintenance.md)承接反馈，F 盘旧设计和原失败证据保留，不以本地认可关闭线上真人或 P/C 门。
