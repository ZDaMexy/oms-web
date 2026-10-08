# 原版 osu-web 生产迁移：2026-10-07

原版 osu-web 已实际部署，当前状态为 **已部署待验收**。2026-10-08 20:35:11 CST 最终切入 `b879e4233818-b0feceae22e4` / schema3；共享主机完整运行、两次实际空目录恢复、完整 F 保全、八对 / 最大 raw / 额外 2 GiB 空间门、发布前后正式备份及新→旧→新同库回退均通过。公网页面、真实目录 / 参考混榜 / 公开个人、插件 / 源码下载和缓存核验通过；原 timer 已恢复 enabled / active / waiting。下载入库、真实账号 / 密钥、OMS 对照和固定播放器 P/C 仍需真人验收。维护、备份与回退取[维护说明](production-maintenance.md)，本轮发布和失败取[正式发布与收尾](#正式发布与收尾)。

运行来源仍为 Backend `b879e42338183bed3a5b7de057817152a23de46c`、Web `b0feceae22e4af55dc9c974f39e4b5f40a02bfd1`，package SHA `01b2b54ac25cb6dce57dba5797bcbfaadc124f0bf3ef0d85fb73c971dd039568`。后续文档与外置检查工具提交不是运行版本。下文按原时点保留各轮进行中状态和真实失败；新结论不重标旧 false，不代签真人 P/C。

## 不可变来源与数据

- 新站从 OMS Web 当前已提交源码导出 Laravel / Blade / React / Less / Turbo 页面，附同一源码下载、Composer 锁定依赖和散列前端文件；不导出工作目录、环境、数据库或缓存。
- FastAPI / SQLite 仍是唯一账号、成绩和社区权威。需随官网上线网页写入身份断言，不扩大 cookie 路径，不把 cookie / Authorization 交给 PHP 页面读取服务。
- 外部插件保持旧正式包的实际字节、版本及原构建提交，与本轮运行时提交分别登记，不重写 `versions.json`。保留原八个批准下载文件与范围请求。
- 完整公开历史继续挂既有已批准只读投影，25,562,325 摘要 / 334,117 谱面；母库和其他私有数据不访问。本轮生产 schema 3 不变。

## 运行隔离

服务器现有宝塔 PHP 8.2.28 不满足锁定依赖。F 盘构建独立 Alpine 3.24.2 / PHP 8.5.11 根目录，官方 APK 签名校验，固定版本及实际包清单随发布登记；不升级共享 PHP，不添容器守护进程，不在服务器编译。

PHP 专用 `oms-web` 用户，只读挂载 `/app`；唯一写入位置是该发布缓存与日志。根目录不挂 live DB、备份和历史投影，出站仅允许 loopback；两子进程、200 MiB / 50% CPU / 禁 swap。CLI 缓存在正式 `/app` 命名空间及正式 URL 下重建，128 MiB / 50% CPU；每次发布重启 FPM，清除旧 OPcache。

网页 GET 仅将宝塔 Nginx 设定的 FastCGI `REMOTE_ADDR` 传至 API 的可信 loopback 代理边界，访客 X-Forwarded-For 无效；不放宽 600/min 的同出口额度。严格脚本策略为 `script-src 'self'`，原组件内联样式允许；可执行 locale 初始化已进入编译脚本。HTML `no-cache`，带散列资源长期不可变缓存。

## 生产门

1. 先备份真实网站 / Nginx / unit 配置与旧发布来源至 F，核对旧包完整内容指纹。旧设计不在服务器另打备份包；现有不可变旧发布作为源码回退目标。
2. 同一真实共享主机的独立 loopback 入口运行候选；真实 live DB 与旧网站继续在线。全量投影、两玩法各 100,000 distinct 合成公开最佳、实际 PHP 页 / API / 写入及完整榜覆盖。
3. 至少 1,800 秒持续、5 读/秒与重叠写，读取 / 个人 ≤300 ms、提交 ≤500 ms、玩家完整榜 ≤1 s、原生完整榜 ≤10 s；PHP 另列页面延迟与资源，不能用纯静态豁免。MemAvailable ≥512 MiB、swap / OOM 为零，读取实际 cgroup 终态。
4. 两个新空目录恢复。第二轮保留旧 reader，将已提交撤钥 / 隐帖留在 WAL；完整 22 表、sequence、schema、索引及 trigger 指纹在 HTTP quota 写入前一致。实际 PHP 页、资源、UUID 所有权、非空原生容器与完整历史榜都须重验。
5. 逐项记录最大 raw、八日压缩副本与 sidecar、运行环境 / 发布包及恢复工作区的实际磁盘峰值，留 ≥2 GiB。恢复串行，不叠加多个 IR 服务；空间不足记录实测失败，不购资源或降低目标。
6. 通过后使用固定维护 helper 取得实际一致发布前备份，导出保护在 F；停止 timer 并等待已有 worker 完成。原库保留，用新运行时及 PHP 切换配对网站规则。宝塔真实 Nginx `-t` 后 reload，检查 OMS 与个人主页、HTTPS / ACME、旧 API / 下载、缓存与匿名公开边界。
7. 实际日备份来源绑定新 `release.json`；旧 sidecar 不改标签。回退只切旧源码 / 旧网站配置，保留同一当前库，停新 PHP，固定维护 helper 保持批准版本，不回灌旧库。

实际命令、来源指纹和门结果保存在 F 盘受保护证据目录 `F:\oms\artifacts\oms-web-production-20261007`。本地已有成功与失败证据保留，不作为服务器新门的替代。

2026-10-08 首次独立入口启动失败，正式站仍为原发布：FPM 无法重新打开 systemd journal socket 对应的 `/proc/self/fd/2`，改用专属可写日志；宝塔 Nginx 的独立配置缺少现主配置的 Lua 模块路径，补入实际 `/www/server/nginx/lib/lua/?.lua`，启动日志亦明确指向独立工作区。原失败日志保留为 `staging-start-failure-r1.log`；修订后的实际启动与后续门须重新记录。

2026-10-08 独立入口 `/` 已实测 200；CLI 缓存实际峰值 57,188,352 B，128 MiB / 50% CPU、swap / OOM 为零且完成终态成功。完整测试数据在 F 盘物理承载的 WSL 工作盘生成：BMS / mania 各新增 100,000 distinct 公开最佳，实际不同玩家最佳分别 100,050 / 100,001；raw 1,379,868,672 B、一致 gzip 100,862,078 B。该准备报告明确 `shared_host_gate=false`，不是共享主机门。Windows 目录首次慢速中断及非法合成分数的失败记录原样保留，修正后的单次分数遵守现有可表示整数上限。当前宿主磁盘余量与完整恢复、八日保留和 2 GiB 预留仍有缺口，正在按既有证据核对可退役的任务专用重复测试产物；不降低目标、不自动购买资源。

## 待签状态

2026-10-08 新候选安装在 128 MiB / 50% CPU / swap0 有限进程中实际完成，正式 current 保持原样。第一次检查入口引用旧运行包中不存在的验收脚本，已保留失败并改用来源明确的独立检查脚本。随后 PHP 缓存以 `200/CHDIR` 明确失败：有限安装进程的私有 `0077` 被沿用到公开源码目录，实际模式为 `0700`；安装入口现明确采用 `0022` 创建只读公开源码目录，账号 / 合成原始数据继续单独 `0600/0700`。已生成不可变候选未修改源码字节，9598 文件指纹保持；1065 个声明范围内公开目录独立校正为 `0755`，证据 `public-source-directory-modes.json`。重跑缓存实际成功终态，峰值 28,770,304 B，128 MiB / 50% CPU / swap0，receipt `cache-live-r2.json`；loopback 首页 200。完整失败轮的 F 盘 gzip CRC / 136 文件 SHA / 全 22 表已核对；NTFS 上的初次慢速 SQLite 校验保留为中断，完成复核在受保护且物理位于 F 的 WSL 工作盘进行，不签主机门。

2026-10-08 首次完整运行在 `original_directory_and_full_native_latency` 失败，未执行完 1,800 秒门；原报告及实际 driver 失败终态已保存在 F。单独诊断中目录 p95 172.034 ms、四来源完整原生 8.99～9.36 秒，明确只作定位，不能补签失败。后端针对实际随机 payload 读盘改为顺序读取，再恢复最高 EX / 原 ID 顺序；17 项针对性与 337 项全服务回归通过，真实共享主机须重跑。验收工具修正为延迟判失败前保存完整度量，恢复 API 必须运行新空目录的源码与离线冻结重建的虚拟环境，并直接绑定批准公开投影的独立绝对路径，不依赖原源码目录中的 archive symlink；原库和两恢复库的 main / WAL、解包 / 依赖 / 缓存等待期均纳入实际空间观察，八份备份与 raw 空间门必须消费后才能签恢复成功。此段是修订来源，尚不代表新运行或恢复门通过。

2026-10-08 第二次完整运行在 `first_and_repeated_profile_300ms` 失败，首次个人检查观察段 351.299 ms；原 driver 失败终态与报告保持，尚未进入 1800 秒持续阶段。外部 owner 首帧采集发生在 try 外，快失败导致其报告仍为 running；该报告只保留为不完整，不补签成功。工具现将首帧采集纳入 try 并在 finally 保存实际终态，每次个人 HTTP 在判断延迟前落下独立度量。后续诊断的 BMS / mania 最高 147.821 / 51.674 ms 与四来源完整原生 9.737 / 9.395 / 9.091 / 8.372 秒均仅作定位：它们发生在此前访问之后，不能替代首次速度门。原生观察出现 memory.high 回收等待，诊断没有读盘分段，不把它直接当作已证实的唯一根因。

服务修订仅在 BMS 路径省去未使用的 `passed` payload 提取，mania 保留真实 passed；完整原生在同一 BEGIN 快照内改为每批 256 个已选主键顺序读取大 payload，排名仍在完整窄候选上计算，最终按最高 EX / 原 ID 排列有界字节。没有截断人数或删除未知条件。BMS / mania 玩家针对性 107 项、原生针对性 17 项与本次全服务 337 项通过，JUnit `bms-profile-covering-focused-r1.xml`、`native-batch-{focused,full}-r1.xml`。这些软件结果不能提升共享主机或 P/C 状态，新候选须重新运行。

新候选 `cba8b3affe30-2a96c216fa5c` 的不可变安装、缓存实际成功终态及 loopback 首页 200 已取得；缓存峰值 56,066,048 B。首次宝塔配置检查由 root 执行，创建 `0600` 的 error log / pid，阻止 oms-web 单元启动；两次真实失败保持 `nginx-start-failures-r3.log`。仅修正这两个文件归属，后续独立配置检查以 oms-web 用户及任务自己的 `-e` 日志路径执行；恢复 helper 已采用同一路径。正式 Nginx 的 root 配置检查和共享网站规则不改变。

该候选第三次完整运行在目录速度门失败，driver / 外部 owner 均保留实际失败终态，`run-r3-failed.json` / `run-r3-owner-failed.json` 保存在受保护 F 盘。首次 BMS / mania 个人页分别 266.617 / 74.504 ms；四播放器各完整 29,204 人、gzip 原始数组 / 本人 / 并列名次及两类 413 通过，分别 9,559.706 / 9,216.659 / 9,559.015 / 9,352.583 ms。目录九次查询 p95 599.781 ms 超 300，仍未进入完整分页、burst 或 1,800 秒阶段；不能用这些成功分项提升运行总门。

逐项诊断保留各 HTTP、SQL 计划和耗时，均 `staging_host_gate=false`。独立冷态全部目录 HTTP 首次 1,106.674 ms，重复 71.197 / 56.071 ms；主因是 live 目录公开资格探测，单纯移除页面 CTE 或 archive 的空 `WHERE 1` 不能解释或解决原失败。原生完整榜不截断，历史投影保持只读。顺序全分数集合、`IN` / 分组改写和仅公开组覆盖索引的负面结果一并保留，不采用它们。仅合成库的两条窄覆盖索引试验保留原 SQL：live 资格首读 97.157 ms、去历史重复 288.981 ms、完整总数 290.525 ms，精确总数仍为 338,121；结束时移除试验索引，schema / score_groups 指纹前后相同。服务采用 `scores(chart_md5,group_id)` 与 `score_groups(id,public_board)`，不新增表或触发器；空 archive 计数使用真正无条件 COUNT，资格、各来源标题搜索、排重、元数据与 BEGIN 快照保持。软件与完整 HTTP 新门须另行记录，诊断不能代签。

该修订目录 / 备份 focused 32 项及全服务 338 项通过，JUnit `directory-covering-{focused,full}-r1.xml`（13.98 / 106.19 秒）；新增行为覆盖隐藏组、删除部分成绩和删空后仍存在的旧组。只读审查确认固定 d1 日备份验证器仍接受普通 core 索引，旧 b520 / d1 runtime 保留并自动维护它们，表与触发器定义不改。目录探针现在保存每次请求的查询类别、重复次序、精确总数 / 行数和 HTTP 度量，后续失败能准确定位请求。软件通过不提升新 HTTP、空间或恢复门。

完整第二失败工作区 131 文件已独立保全至 F，gzip CRC / 所有 SHA / 全 22 表与真实保全 worker 成功终态通过，archive `stopped-staging-3ae-r3-complete.tar.gz` / SHA `67c9c025276a8e73ff5c95e39205df52b82c40531bb6f0db14b2172057d686ff`。旧失败报告不改；仅停止、核验后的合成 data 在同一文件系统移动给新候选，dev/inode/size 保持，无第二份 raw，记录 `verification-stopped-data-transfer-r3.json`。真实账号库未访问或移动。

第三失败工作区已完整保全至 F，175 文件 SHA、gzip CRC 和全 22 表指纹通过；archive `stopped-staging-cba-r4-complete.tar.gz` / SHA `178a656d36cfbab34fd7ff8bb814efe40e27194defe502c73d6ab748d8f49418`。保全后产生的五个有限进程控制文件另取实际终态保存，未忽略变动；停止后的四个合成数据文件按 dev / inode / size / SHA 在同一文件系统转移给 `2775faec4359-16d467e1a047`。核验 F 盘全文件后仅退役旧任务候选、失败工作区和重复压缩件，两批实际收回 667,779,072 / 293,068,800 B；原正式发布和固定日备份 helper 保留。

该新候选第四次运行在首次来源榜检查失败，正式站仍未切换，目录、原生、完整分页和 1800 秒均未执行。旧检查把 HTTP 状态与 300 ms 合并且未先保存度量，不能据此宣称榜单延迟回归。实际只读 session 元数据证明开跑时该账号两种 access 均已过期 617 秒、未撤销；独立诊断实际请求返回 401 / `invalid_session`，72.064 ms，正常 HTTP refresh 后同一请求 200 / 67.368 ms。诊断及外部 owner 实际有限终态成功，报告 `verification-auth-expiry-diagnostic-r5.json` / `verification-auth-expiry-owner-r5.json`；这些定位结果仍 `staging_host_gate=false`。验收工具改为在首次独立来源进程前刷新原 100 个假 session，随后主访问阶段再刷新，保持正常一小时寿命与账号归属；每次来源 HTTP 在断言前记录状态、耗时、重复和首末位置，状态与速度分别判定。故意撤销后仍须 401，完整运行必须新轮重跑。

新候选安装成功；准备 helper 的首次首页请求在监听就绪前返回 curl 7，真实单元没有重启、错误日志为空，随后同一路径 200。保留该失败，后续入口使用有限的就绪等待。缓存实际 receipt 沿用文件名 `cache-live-r3.json`，其 release、单元和来源指纹绑定本轮；首次错误引用不存在的 r4 文件在注册前失败，原脚本保留，不重标 receipt 文件名或旧失败。

恢复阶段的正常会话刷新改到每轮备份前，第二轮在固定旧 reader 和故意撤销前执行。第一轮完整 F 导出等待计入原 access 寿命；刷新同步探针实际内存与私有凭据文件，保持原 session，不在恢复库另轮转，也不在撤销后复活会话。此处是验收工具修订，尚未运行两次共享主机恢复。

第四失败轮完整 134 文件已保全到受保护 F 盘，gzip CRC / SHA 和全 22 表指纹通过；archive `stopped-staging-277-r5-complete.tar.gz` / SHA `6524957624964b2cd59a1d0cea2173bfd6ab2dd54653d16cf3cff5cb0a235da2`，五个最终控制文件另存 SHA。新 `r2` 缓存峰值 48,984,064 B，实际有限终态成功、首页 200；旧失败报告不覆盖。官网产品包仍为 `2775faec4359-16d467e1a047`、package SHA `fcf59e4ae0be72eb21f8d57c9b5a13264a2ee454890f42c5e458647e5c31194a`；随后修订仅验收工具及文档，外置工具分别绑定提交 / SHA，不把新工具说成原运行包字节。转移 helper 首次因旧 unit 轮次断言在任何移动前失败，原脚本 / 日志保留，改用独立 r5b 入口。

第五轮七个来源选择各新进程、共 77 请求均 200，首尾 / browser 的完整排名、分数、独立灯、人数与未知身份校验通过；各选择最高 95.423 / 93.526 / 72.979 / 91.846 / 108.469 / 120.842 / 88.764 ms，全来源参考榜 29,251 人、单独 OMS 50 人、无来源 0 人。随后工具在主访问前重复刷新；该轮共 44 秒，实测同 IP `refresh:ip:127.0.0.1` 的正常窗口 hits=120，与服务 `120 / 60s` 及首组 100、次组 20 次成功轮转一致。失败 HTTP 未在原断言前落度量，限额定位来自这组状态及源码时序，不伪造其响应记录。原 driver / owner 实际失败终态及报告保留；个人、目录、完整原生和 1800 秒未运行。当前工具去掉主访问前的冗余刷新，只保留初始一次 100 请求；每个刷新失败先留不含 token 的状态 / 错误码 / Retry-After，成功轮转先保全私有 token 再写度量。恢复每轮仍在快照与撤销前正常刷新，不修改服务额度、TTL 或 quota 表。

长验收超过原合成 access 的剩余时间，独立 staging 的 50 个假账号、100 个原 session 已通过真实 HTTP refresh 更新，保持原 session / owner / 一小时正常寿命，凭据原子保存在私有文件；没有 SQL 延长 TTL。工具现于运行及恢复阶段开始调用同一真实刷新边界，故意撤销后的请求仍验证 401。独立刷新启动的 scope / transferred-seed 注册失败记录保留；transfer 仍只由真实 run 注册。运行包中的工具与另行绑定的修订工具分别记 SHA，实际完整运行尚待签收。

已核验 F 盘完整保存的任务专用重复压缩件及失效新候选后，定点退役实际收回 524,623,872 B；另将已停止的第一次失败工作区完整保全、核验 F 盘后定点退役，实际再收回 1,681,768,448 B，receipt `failed-native-r1/retire-failed-native-r1.json`。保留原发布、原设计与所有失败证据，当前剩余空间仍不足完整备份 / 恢复预算。共享主机通用 journal 约 1.9 GB、独立 OMS journal 约 4.5 MB；通用日志保全至 F 后限制为 512 MB 的方案已询问用户，待确认，不自行调整其它应用的日志保留范围。

2026-10-08 第五次运行的 134 文件完整失败轮已保全至 `stopped-staging-277-r6`：104,851,677 B，SHA `a11936fb94ba74e83c79ec3b646e170aa2a4a133b45dc1f8695ea228c6e3eeab`。服务器有限保全进程真实完成，停止库的完整 22 表指纹 / integrity / FK 已测。首次本地解包完成 CRC / 所有文件 SHA 后因 F 盘只剩约 9 MB 出现 WSL 标准库 I/O 错误，SQLite 本地重读未执行，失败保留。后续 Windows Python 流式复核完整 gzip CRC 与 134 SHA，main / WAL / SHM 全部字节等于已测服务器停库，因此可证明导出内容保全；receipt 明记 `local_SQLite_reread_executed=false`，这不是两新空目录运行恢复。保全后仅同盘移动原合成 data 到 r3，inode / size / SHA 不变、无第二份 raw；准备与缓存正常完成。F 盘紧急回收仅删除四个 SHA512 核验过、无构建占用的 npm 可再生成 blob，52,293,952 B；存档、谱面与证据保持。WSL 本地预览现停止，F 盘空间仍需解决，不将虚拟盘内部空闲当作 Windows 实际可用空间。

候选 `2775faec4359-16d467e1a047` 的第六次运行 r3 已取得实际 driver / 外部 owner 失败终态。首次 BMS / mania 个人页 288.758 / 76.645 ms、各十次 HTTP 与两玩法各 100,000 distinct 最佳的完整独立数学通过；完整目录 338,121 张、常用文字查询 284,975 张，九请求最高 125.624 ms。四来源各完整 29,204 人的真实 gzip HTTP 为 9,398.907 / 9,318.737 / 9,428.641 / 9,192.872 ms；本人一次、完整整数身份、顺序、并列全体排名、独立灯与两类明确 413 通过。随后 `resources-original-API` 的 175 样本 / 49.509 秒内主机可用内存最低 478,367,744 B，低于 512 MiB，swap / OOM 零、磁盘最低 3,161,862,144 B；总门仍失败，未到完整分页、burst 或 1,800 秒。不得用这些成功分项提升整轮或 P/C。

验收程序 `native_stage` 在下一来源请求 / 解码完成前还持有上一份完整 JSON 图，实际 driver 峰值 252,182,528 B，memory.high 事件 2,124 次。修订仅在全部字段校验与标量度量保存后 `del data, scores, mine`，保留完整数组、gzip 实际传输与十秒门，不扩服务预算。不可变候选中的服务与工具原字节不改；另行运行的检查入口与 multisource probe 都须在工作区控制中明确绑定独立 SHA / 来源提交，报告分别标记实际服务源码和工具源码，恢复同样消费该工具身份。新一轮实际资源门仍待，不从对象持有定位推导通过。

第六失败轮已由实际 128 MiB / 50% CPU 有限进程完整保存在服务器，archive `stopped-staging-277-r7-complete.tar.gz`，104,922,999 B；因 F 盘空间不足，完整 F 导出仍待，不能记作 F 已核验。保留原 r3 报告与完整压缩件后，只同盘移动四个已核验合成文件到新 r4，inode / size / SHA 不变、无第二份 raw。服务包仍为 `2775faec4359-16d467e1a047`；第七轮独立检查入口绑定 Web `7f507572579548e544cb4231ef6a860b871988ec` / SHA `97aeac055a8a901acd8ac2664208ddc273c4b60ae039a40daa38f1346482ee7f`，probe 绑定 Backend `6fb0c2b710181eb9e89dcb091ced83e6a6565b67` / SHA `aaa551ab3108cfd0c1600e1473a322ffe16e01ba59a3803f58995d62ebc72343`，不修改不可变候选字节。

第七轮 r4 首次 BMS / mania 个人 HTTP 289.083 / 76.480 ms、完整目录九请求最高 132.452 ms、四来源各完整 29,204 人原生 gzip 9,366.089 / 9,211.803 / 9,018.191 / 9,017.897 ms 通过。原生观察 173 帧的最低 MemAvailable 616,833,024 B，swap / OOM 零。全来源 29,251 人 / 1,463 个有行页面及一页越界全验，1,464 HTTP 的 p95 80.662 ms / 最高 127.658 ms；十秒 burst 的 250 读、25 OMS 新 UUID、25 外部更新、10 社区写均通过，读 p95 112.031 ms，三类写 p95 63.123 / 33.955 / 67.513 ms。固定账号的灯此前已为 8，该轮重复交灯不能证明新的独立灯提升；虽然原工具写了 `independent_best_lamp_checked=true`，该项新更新证据不采纳，后续必须核验实际前后值。

同轮持续资源观察覆盖 1,801.093 秒 / 6,671 帧，最低 MemAvailable 430,460,928 B，低于 512 MiB；swap / OOM 零、最低磁盘空闲 2,883,530,752 B，driver / owner 均为真实 exit 1 失败终态。低内存帧集中在观察窗 1,110.860～1,144.302 秒；系统 `apt-daily-upgrade.service` 元数据为 06:30:35～06:31:17，但仅有时间关联，未读取通用 journal、未证实内存贡献，也未停止系统任务。失败报告、外部终态和原日志已保全至 F 的 `run-r7-failed`；全部资源样本通过原 SHA、6,671 行及完整 gzip CRC 复核。原资源断言抛出后未保存 API / PHP 延迟汇总，不能补签持续速度、实际配额、投影结束指纹或恢复门。

修订检查程序在请求线程内完成原 HTTP 200 / HTML 校验后只返回标量度量，消除约 900 个 Future 对正文的持续持有；首次八页大小推算约 28.7 MB，不足以独自解释全部余量缺口。完整 API / PHP 汇总于资源断言前单独保存，最终门仍须资源和延迟全部通过。独立灯改为选择已授权合成账号中实际可提升的状态，要求 `updated=true`、同一状态 ID、分数不变、持久灯从小于 8 提升至 8，保留前后值；不以到顶状态代签。新实际运行仍待，不从工具修订推导通过。

F 盘四份已关闭失败轮的可再生成 raw 解包副本已定点退役，完整压缩件和证据保留；前三份 main SHA 在删除前一致，第四份为磁盘满导致的失败临时解包，其 SHA 不一致与首次退役失败另存，不算成功 SQLite 重读。实际 `/sbin/fstrim` 完成，但专用 WSL VHD 仍为 10,989,076,480 B、F 空闲约 54 MiB，不能将 VHD 内部空闲算作 F 已回收。受保护目录中的 `CompactOwnedOmsWebWsl.ps1` 只对该已停止、归属核验的 VHD 做管理员压缩，尚未执行。额外 npm 缓存回收被自动审批以“策略阻止”拒绝，未执行。F 至少 4 GiB 空间与通用日志完整保全后限制 512 MiB 的授权仍待，不自行购买、扩盘或调整其它应用日志。

两空恢复的五份来源已保存在 F 的 `recovery-protocol-r7`，AST 与只读审查通过，**实际未运行**。预备入口使用 ready / close 握手：仍存活时完成采样，再读真实退出终态，最后发布回执。每轮仅导出自己的完整关闭目录和 snapshot / sidecar，F 全字节证明后才定点退役。新源码 / 冻结依赖、全 22 表、完整原生数组、旧 reader 下 WAL 撤钥 / 隐帖、八份备份及真实 raw 峰值门保持。新检查来源和工作区须重新绑定并保留原预备来源，不能将准备当恢复完成。

第七失败轮已完整保存在服务器 `stopped-staging-277-r8-complete.tar.gz`，106,099,752 B，SHA `5df0ce11d73b54614b51b037550f2755016bcc9f8ebc788776faae91929ae33b`；实际 128 MiB / 50% CPU worker 完成，全 22 表、integrity / FK 与资源观察通过。外部保全 controller 在 worker 正常退出成为 zombie、systemd 尚未清零 MainPID 的瞬间以 `owned_pid_not_reused` 失败，原失败报告和日志保持，不补签其终态。新增独立关闭复核实际 exit 0，读取同一 worker 的 loaded / active-exited / MainPID 0 / 原 PID、预算与真实源码，消费历史 kernel 帧并明确其不是终态；完整归档 SHA、每项 SHA / gzip EOF 及四个停库文件重新核对，原 controller 仍为失败。验证回执保存在 F 的 `run-r7-failed`；完整归档尚未导出到 F，不将服务器保全等同外存成功。

第八轮在新 `r5` 接续同一不可变候选和四个合成数据文件。独立关闭复核、准备 / 缓存、同盘转移三个有限进程已实际成功，转移前后 inode / size / SHA 保持、无第二份 raw；缓存实际峰值 55,132,160 B。原 ownership 只在真实 run 开始时注册一次。新检查入口绑定 Web `f7537f0d2619305b5d96d296d8786b3db02a6360` / SHA `7544623f2264658a2f04a919af73a6072ab335fafa97781a799623d714362ef4`，probe 沿同一 `6fb0c2b7` / `aaa551ab…`；来源原文件在 F 的 `runtime-source-controls-r8`，实际准备 / 缓存 / 转移及 loaded 终态在 `staging-preparation-r8`。本轮工具、候选产品和 Git 文档 HEAD 分别登记，服务预算不扩大。本轮现已失败结束，分项及保全如下；未签资源、恢复或上线。

第八轮首次 BMS / mania 个人页 290.989 / 68.069 ms、目录九请求最高 127.409 ms、四来源完整原生与全来源 29,251 人的全部 1,464 次分页请求通过；分页 p95 77.698 ms。实际合成外部状态同一记录分数 178 不变、灯从 6 提升至 8，HTTP `updated=true`，本轮才采纳独立灯更新证据。持续观察实际 1,801.211 秒 / 6,678 帧，其中一帧最低 MemAvailable 为 526,848,000 B（502.441 MiB），仍低于 512 MiB，driver / 外部 owner 均真实 exit 1；swap / OOM 零，最低磁盘 2,915,807,232 B，原库 main + WAL 峰值 1,414,075,096 B。仅差约 9.56 MiB 也不能放宽门槛，未证实其它系统任务的内存贡献。

本轮资源断言前已保存真实持续 HTTP 汇总：9,000 次读取、250 次 OMS UUID 新局、250 次外部状态更新、50 次社区写全部取得预期状态，确认延迟 p95 分别 108.116 / 43.394 / 22.736 / 50.961 ms；900 次 PHP 页面全部 200，确认 p95 307.673 ms。API / PHP 速度分项通过，`resource_gate_consumed=false`；配额、结束投影指纹与两空恢复尚未执行，不提升整轮。F 的 `run-r8-actual` 保留失败报告、实际外部终态及日志；6,678 行资源流的原 SHA `905d6f6acb9e7a64b2011ada341416ebf15d8557b24fd83865c84e8a191394f3`、完整 gzip CRC 已独立核验。完整失败目录仍须有限保全，F 全件导出仍受空间限制。

检查程序在个人页与来源校验结束后仍持有上一份独立完整数学图，现分别在全部断言与标量度量保存后释放该图及别名，下一玩法 / 来源再构建自己的完整图。只读审查确认后续不消费已释放对象，无隐藏完整图别名；不删校验、分页或原生数组，不修改服务源码、资源预算或旧失败报告。下一轮必须从实际新提交导出独立工具 SHA 后重跑，不能由对象寿命修订推导资源通过。

同轮浏览器通过临时 SSH loopback 入口打开实际候选的新闻首页、Ginger 目录、谱面详情与历史榜；清空来源后人数由 9 变 0，选择 LR2 历史后恢复 9，再恢复全来源。旧 namespace、历史摘要、未知游玩时间和未确认的下载连通性如实显示。统一账号面板实际打开 / 收起，未填账号或提交表单；临时标签与转发已关闭。回执 `browser-staging-r8.json` 不保存个人原始行，明确下载入库、真人账号 / 客户端、资源与生产切换未验。

两空恢复预备入口另保留为 `recovery-protocol-r8`，消费 `r5` 与本轮准确工具 SHA；在任何重启前读实际已关闭完整 run driver / 外部 owner 成功状态。ExecStart 不在原工具的属性列表内，预执行只读审查发现直接索引会失败，已改为恢复 owner 单独实测执行定义，原终态不补字段、运行中工具不改。正常退出仅接受原 PID / starttime 的 zombie 或确实消失，再等待 systemd 实际 MainPID 0，所有原终态 / 预算断言保持。五份修订源 AST 与只读审查通过，旧源和修订前 receipt 保留；两次恢复仍**未执行**，F 空间和共享日志决策仍待。

当前未宣称部署成功。切换后应登记“已部署待验收”，给出正式首页、谱面、个人、来源筛选与客户端账号对照路径；保留公开发行版尚未包含 IR 的说明。P/C 完整闭环仍需真实播放器交分与原生读榜及指定玩法矩阵的人工作证。

第八失败轮现已完整保存在服务器 `stopped-staging-277-r9-complete.tar.gz`，106,208,929 B，SHA `73d818f886c7c8ed55e2e3aa5007ebf9035bacfa49f9387a602bfd8b0f43a83b`；实际 128 MiB / 50% CPU worker 的 275.180 秒资源观察通过，最低 MemAvailable 787,116,032 B、最低磁盘 2,811,510,784 B。完整 171 成员 SHA / gzip EOF 和 CRC、全 22 表、integrity / FK 已实测。新 controller 只接受原 PID / starttime 的正常退出状态，随后等待真实 MainPID 0；本次 controller / worker 均实际成功终态，原 R7 保全 observer 失败与 R8 run 失败保持。F 的 `run-r8-actual` 已保留本次完整归档 receipt 与最终控制报告 / 日志，完整 gzip 仍待 F 空间，不记作已导出。

第九轮在新 `r6` 接续同一候选与四个合成文件，准备 / 缓存与同盘转移已实际完成，缓存峰值 54,837,248 B；四个保全 / 准备 / 转移有限单元的实际 loaded 成功终态在 `staging-preparation-r9`。新检查入口从 Web `1a9d8d23bcc02e6e17cc1117cecf6a6a86e463ae` 的 Git blob 导出，SHA `a2e00a461f2705e67ebebf566eec87ac6601d5fcd4382e3bd71290ac0e89ebb1`，probe 仍为 `6fb0c2b7` / `aaa551ab…`；已按 binding 明确复制到 r6 后注册 native11。本轮于 UTC 00:48 失败结束，实际 driver / 外部 owner 均 loaded、MainPID 0、exit 1；服务、包和预算不改，旧 r5 工具字节及失败报告不改。

第九轮首次 BMS / mania 个人页 295.085 / 64.735 ms、目录 p95 123.953 ms、四来源完整原生 8.96～9.35 秒及 1,464 次完整分页通过；全来源人数 29,251，分页 p95 79.563 ms。1,801.152 秒 / 6,654 帧持续阶段的 API、PHP 和资源门均通过：9,000 读取、250 OMS UUID 新局、250 外部状态更新、50 社区写全为预期状态，确认 p95 108.872 / 44.278 / 23.692 / 51.808 ms；900 PHP 页面全 200，确认 p95 303.477 ms。最低 MemAvailable 538,857,472 B（513.895 MiB），余量仅约 1.895 MiB，不能宣称宽裕。

随后同出口读榜 / 登录检查的 68.604 秒 / 254 帧资源门失败，最低 MemAvailable 472,223,744 B（450.348 MiB），最后一次低于门槛的连续区间为约 61.998～68.604 秒。全部阶段的 host / cgroup swap 与 OOM 均零；该阶段最低磁盘 2,765,701,120 B。最低内存同帧的 driver PSS 144,124 KiB、backend PSS 194,392 KiB；后者确实执行原单槽 Argon2 验证，不能删除密码检查或降低安全成本。原同出口 HTTP 汇总在资源断言后才保存，本次未落下，不从数据库或其它分项重建登录 / 配额成功。真实 peer 配额、结束投影指纹与两空恢复未到达；整轮 `staging_host_gate=false`，正式 current 仍为旧发布。

F 的 `run-r9-actual` 保留原失败报告 / 日志、两个实际 loaded 终态和全部 17 段资源流，共 7,754 帧；每段原 SHA / 行数及完整 gzip EOF / CRC 均已核对，压缩合计 1,667,979 B。检查程序同出口阶段的 650 个 Future 原结果仍含已读完的 sources 正文，直到登录重试结束才释放；现保持 650 请求、50 线程、同一 planned 时间与全部指标，只在任务内返回 metric。同出口 HTTP 汇总改在资源断言前真实保存并标 `resource_gate_consumed=false`，最终资源及配额断言保持；修订尚未签新运行门。

实际 driver PSS 从 original-API 阶段约 59 MiB 升至 128 MiB，持续阶段仅再增加约 8 MiB；不能用 PSS 推断泄漏或保证 Future 修订解决缺口。有限标量诊断已完成，来源 SHA `6a3fc2cd392a1b189122cd564bee2cd34cbae1b6cba68c8247f316fc6500abfe`，使用原 a2 / aaa 冻结源；原 native11 已真实关闭，诊断不补签延迟或容量。完整数学校验后 traced current 为 1,194,592 B；四份原生数组每次完整解码约 58 MB、释放后约 1.2 MB，最终 current 1,238,339 B、tracer 内部 485,360 B，但 PSS 仍为 166,688 KiB。这排除了这些已追踪完整图继续存活的解释，未证明底层分配器是唯一原因。

诊断实际 76.779 秒 / 191 帧、最低 MemAvailable 628,199,424 B、最低磁盘 2,657,734,656 B，driver 峰值 216,043,520 B；同 256 MiB / high240 / 50% CPU / swap0，实际 loaded 成功终态。F 的 `memory-diagnostic-r9` 保存真实报告 / 日志 / 终态、完整原 SHA / 行数 / gzip CRC 的资源流。普通合成会话刷新保留真实生命周期，不改 SQL 到期时间；该步骤确实更新合成会话与配额，发生在原 R9 完整归档之后，后续转移须明确绑定当前状态，不能假称仍与归档原 raw / 凭据一致。

完整 R9 失败目录已在诊断前完成保全：`stopped-staging-277-r10-complete.tar.gz`，106,346,316 B，SHA `1559c3a5d5a3a6f1de1d97e553ef1d5958285c3d5b9fc46b0d50905bc5d0d61b`，178 成员完整 SHA / gzip EOF / CRC、全 22 表 / integrity / FK 均已核验。保全源 SHA `9be12ee957a289b13f68ec742a1e02229acb23120263380079091c9aa7539498`；128 MiB / 50% CPU worker 的 286.390 秒 / 1,062 帧资源门通过，最低 MemAvailable 819,716,096 B、最低磁盘 2,658,586,624 B，controller / worker 均真实 loaded / MainPID 0 / exit 0。F 的 `run-r9-actual` 保存 receipt、真实终态 / 日志及全部保全资源流；完整 gzip 仍受 F 空间限制，未记作外存全件成功。

下一轮将完整数学 / 目录 / 原生 / 独立灯与全部分页校验移到临时 `api-core` 子进程，完成后实际 wait / 回收；原断言、真实 HTTP、人数与数据不缩减。子复用 Context 的完整来源与归属边界，只借用经原 argv / cwd / 预算核对的父后端，不启停后端或前端。父子所有导入、来源复核、CPU、PSS、memory.current / peak 均在原 driver cgroup 及连续观察内；子报告完成、实际 exit0 与父资源门分别消费。分页汇总 / digest 于内层资源断言前保存；超时 / 异常先回收子，再关闭父拥有的后端。AST 与只读源码审查通过，实际共同峰值与完整运行仍待；不从进程拆分推导新门通过。

两空恢复预备源按本轮准确 r6 / 工具 SHA 和独立 restore09 / export09 / retire09 / rest09 单元绑定，五份新源在 `recovery-protocol-r9`。AST 与只读审查通过，原 R7 / R8 预备源及所有 SHA 保留；成功 run 终态、ready / close、完整 F 证明后退役及原资源 / 空间门保持。实际恢复仍**未执行**，不能消费失败的 R8 或 R9 run；须待新完整运行通过及 F / 共享日志条件满足后，按新实际绑定修订恢复源再执行。

R9 内存诊断后的实际合成状态已独立复核，来源 SHA `7e091ad7f3036414071d8fb1a940a303dccf027cf41f7188e6ba49bfc6eb0421`。完整 22 表对比只允许真实 `sessions / refresh_tokens / rate_limits` 变化，原账号 / 核心成绩 / 灯 / 社区 / schema / sequence 保持；实际停止、无持有者下的 `wal_checkpoint(TRUNCATE)` 返回 `[0,0,0]`，随后 immutable main 的完整指纹与 checkpoint 前逻辑状态相同，WAL 为空。原归档的 WAL / SHM 及归档后的保全控制文件分别登记，不虚称当前四文件仍与旧 archive 相同。该单元实际 exit0 / success，394.315 秒 / 1,503 帧，最低 MemAvailable 834,772,992 B / 磁盘 2,654,646,272 B；F 的 `post-diagnostic-reconciliation-r9` 保存所有原帧、SHA / 完整 gzip CRC、独立 ExecStart 和真实终态。

第十轮在 `r7` 接续同一产品包 `2775faec4359-16d467e1a047`。停止后的合成数据同盘转移，dev / inode / size / SHA 在移动前后保持，无第二份 raw。准备、缓存、转移均取得真实 exit0 / success；缓存峰值 87,785,472 B。新工具独立输入位于 `/opt/oms-web/incoming/20261008-r10`，原 r4 同名脚本未覆盖；Web 检查器为 `f0ef69e60a2bf4b90c1eca461013316c4391c387` 的实际 blob / SHA `57b8fa540aea95f04a0823735c8b623545b7246e8ef8abb6e4935c9967f670ae`，probe 为 `a0bbfe23678b135864b79fb9bbd3dd1a5f976dba` / SHA `ee62d45390a587837baf42c5028dd37746c7e9db24629b143c35bd73d9a7e9c3`。实际原文件、注册和绑定在 F 的 `runtime-source-controls-r10-isolated-input`，源码提交、实际工具与产品包来源分开。

R10 实际从 `2026-10-08T01:48:15.114141+00:00` 至 `01:48:57.193814+00:00`。七个独立来源范围检查完成后，首次 BMS 个人 HTTP 200 / 319.090 ms，超过 300 ms；单独度量在断言前已保存，整轮明确失败。九个后端均正常关闭；driver / owner 是实际 loaded / MainPID 0 / exit1，driver 峰值 252,366,848 B。F 的 `run-r10-actual` 保留原失败报告 / 日志、实际 ExecStart 和全部九段资源流共 53 帧，原 SHA / 行数 / 完整 gzip EOF / CRC 均通过，压缩合计 18,781 B。资源分项通过不能签延迟，mania / `api-core` / 原生整榜 / 分页 / burst / 1,800 秒 / 同出口与实际配额 / 两空恢复均未由本轮签收；`api-core` 子进程实际尚未运行，不宣称共同峰值已验证。

R10 失败全件以 R11 实际保全：`stopped-staging-277-r11-complete.tar.gz`，105,232,733 B，SHA `93119c154254113a6b6cff7fbc5be0c34366585efdde0665d134c2d33ab27e12`，181 成员 SHA / 完整 gzip EOF / CRC、全 22 表 / integrity / FK 核验通过。source SHA `ff66981ffa2f71e466babc9be3ce1c76a1a2704ae9ab0b564a8c380ccb87092c`；controller / worker 均实际 loaded / MainPID 0 / exit0 / success，worker 280.307 秒 / 1,040 帧、最低 MemAvailable 778,362,880 B / 磁盘 2,545,750,016 B，128 MiB / 50% CPU / swap0。F 的 `r11-actual-preservation` 已保留 receipt、报告 / 日志、独立实际终态及所有原帧 SHA / 完整 gzip CRC，压缩 75,955 B；**完整 archive 尚未导出到 F**，不将服务器保全记成外存全件成功。停止后的 main 1,414,680,576 B / SHA `240bd1e68523336b47574a4bc0969367826bda6d44b61d2607c750d870461783`，WAL 实际 0 B。

随后只读分段诊断以已保全、空 WAL 的合成 main 为输入，不读凭据、真实生产库或通用日志，不启动 PHP。source SHA `b0b645eb2caaa456154ef1342cc3317a9e3bc785a892e012f8eb72e9dbc96784`，实际有限单元 PID 2596473 / exit0 / success；F 的 `profile-cost-diagnostic-r10` 保留报告、实际终态及三个完整资源帧。OMS / ED / 两源 / 全源的 `totals / lanes` 全字段及 canonical JSON SHA 均与原记录计算一致；原最佳挑选为 48.312 / 1.194 / 34.975 / 86.994 ms，现有统计读取含名次为 8.092 / 1.499 / 3.081 / 61.955 ms。该 CPU50 的停止后只读测量不证明首次 HTTP、物理冷缓存或 300 ms 门；不能替代原 319.090 ms 失败，也不能据此断言唯一耗时原因。

Backend 候选源码 `b879e42338183bed3a5b7de057817152a23de46c` 只将 BMS `performance` 在原 `public_population()` 一致快照内改用已维护的来源 / 条件统计，跨来源谱面仍按 MD5 去重，最佳家庭仍分别计数，名次用原方法；scope 贡献不匹配仍明确失败，不返回部分榜。mania 保留原最佳记录的真实 `passed`，个人最佳 / 最近记录及认证不改；没有新增表、索引、迁移、缓存或配额。F-backed Windows Python 3.12.14 / SQLite 3.53.1 下，针对性 87 项 / 21.86 秒与全服务 340 项 / 70.15 秒通过，JUnit `bms-statistics-{focused,full}-r2.xml`；新用例覆盖单 / 多 / 全 / 空来源的序列化等价、普通旧 SQLite writer 隐藏后的修复和部分统计缺行的明确失败。pytest 采用 `failed` 临时数据留存策略，实际结果与源 SHA 长期存 F；残留成功临时目录的显式清理被自动审批以 `blocked by policy` 拒绝，未执行，保留原目录继续非清理检查。本次不是客户端发行构建。当时尚未生成新运行包，后续实际安装 / 运行如下；两空恢复仍待。

生成新候选前，F 仅约 33 MiB，专用 WSL 未重启，管理员压缩回执不存在，当时无法生成新完整包或取得上述完整失败备份。共享主机当时空闲约 2.37 GiB，按最新压缩件、八日副本、额外恢复 raw 与 2 GiB 余量预估需约 4.11 GiB；实际恢复峰值尚未测得。通用日志完整保全后限为 512 MiB 的选择仍待，尚未读取、导出或清理通用日志，资源门不降低。先前额外 npm 缓存回收的自动审批拒绝仍有效，没有执行或换路径绕过。正式服务、旧站、固定日备份 helper、全量公开投影与所有失败证据保持原状态。后续 F 实际空间及导出结果如下，不回写上述历史失败回执。

### R11 新候选实测与 R12 检查器修订

新不可变候选 `b879e4233818-b0feceae22e4` 已构建并由实际有限进程安装，包 58,270,622 B / SHA `01b2b54ac25cb6dce57dba5797bcbfaadc124f0bf3ef0d85fb73c971dd039568`。独立核验全部 9,600 成员、9,598 声明文件及完整 gzip EOF / CRC；相对旧 277 包只改变 BMS 统计服务、probe、检查器及对应源码下载，PHP、编译网页资产、八插件和只读投影保持原字节。实际 install controller / worker 均 loaded、MainPID 0、exit0 / success；准备、缓存和四合成文件同盘转移也取得实际成功终态，inode / size / SHA 不变，无第二份 raw。缓存峰值 36,487,168 B。F 的 `r11-actual-install`、`staging-preparation-r11` 留存独立 ExecStart、准确源码与所有 117 资源帧，不能将这些准备门当完整运行或部署。

R11 完整运行为 UTC `2026-10-08T02:54:13.401550` 至 `02:59:28.983284`，driver / owner 均实际 exit1，driver 峰值 252,383,232 B。七个来源范围、首次个人页 BMS 61.441 ms / mania 243.574 ms、完整目录及四份各 29,204 人的完整原生 gzip HTTP 通过；原生为 9.819 / 9.922 / 9.158 / 9.018 秒，仍执行完整字段与明确 413。全部 1,464 次分页 HTTP 和数学通过，随后真实资源断言失败：最低 MemAvailable 480,673,792 B（458.406 MiB），连续约 53.7 秒低于 512 MiB；同帧 driver PSS 194,242 KiB、backend PSS 109,858 KiB，swap / OOM 零。分页度量保存在资源断言前并明确 `resource_gate_consumed=false`。burst、1,800 秒、同出口 / 配额、结束投影与两空恢复未到达，整轮仍 false。F 的 `run-r11-actual` 保存全部 15 段 / 1,643 帧、原 SHA / 行数 / 完整 gzip CRC、报告、日志及真实终态，原冻结工具 `57b8fa54…` 和 probe `ee62d453…` 不改。

R11 停止现场由实际 R12 preserve controller / worker 完整保全，二者均 loaded / MainPID 0 / exit0 / success，源码 SHA `53b40683457d90982d9ac5343410a803cdbe31439f74c57a76aa4bbf9cb4e6df`。archive `stopped-staging-b879-r12-complete.tar.gz` 为 105,655,250 B / SHA `ae17a111371906a5995cde62ca92a8d5d75938e8ac7ae8627ec67fe19887ebee`，198 成员逐项 SHA / size / 完整 gzip EOF / CRC 在 F 独立通过；完整 22 表指纹按已测停止库字节一致保全，不伪称执行本地 SQLite 重读。全部 1,020 资源帧 / 原 SHA / gzip CRC 通过，F 回执为 `r12-actual-preservation/independent-complete-F-preservation-receipt.json`，没有第二份 raw。

此前服务器上完整失败压缩件 r7～r11 现全部导出 F，共 528,810,729 B / 838 成员；每份完整 SHA、每个成员 size / SHA 与 gzip EOF / CRC 均实际核验，见 `closed-failure-full-archives-r11/all-five-full-F-exports-verified.json`。首次 receiver 因旧 r7 / r8 回执没有后续 CRC 字段在下载前失败，原源码及失败保留；v2 如实记录旧字段缺失并独立执行全部核验，不补写旧回执。这证明外存保全，未签主机门、恢复门或服务器退役。

新的检查器冻结 SHA `999c11ab87830585a6d66504a5842312f7ac129df1d9e9df23284c8f56ebae52` 通过 AST / whitespace 和只读审查：七来源仍由父进程逐次启动后端并在 `finally` 关闭，子进程只借用经 argv / cwd / PID / cgroup 核对的后端；首次个人数学、完整原生及全部分页依次借用同一主后端，服务不重启。所有初始化、来源 / 全量投影核对、CPU、PSS、终态与实际 wait 均覆盖在原 driver 预算及外层观察中；人数、完整内容、速度和资源断言不删。中间将七个服务交给子进程的 `f21d5dc9…` 方案被审查指出超时所有权缺口，未采用、未执行，原源码留存。新实现仅通过源码检查，必须独立绑定提交后实际完整重跑，不能从进程寿命修订推导余量通过。

本轮观察 F 可用 7,125,651,456 B，足以保存上述全件；没有管理员压缩回执，不归因于未执行的压缩或 root 清理。R12 保全后服务器可用 2,237,583,360 B，完整恢复和八日副本预算仍不足，真实恢复峰值仍待。当时已外存核验的 OMS 专用重复件尚未退役，随后实际退役见下段；通用日志授权仍待，未访问。成功 pytest 临时目录及额外 npm 回收的自动审批拒绝保持未执行。正式 current、生产账号 / 数据、旧站、固定 helper 和母库均未改；P/C、真人及两空恢复未闭环。

### R12 实测、进程归属诊断与已核验重复件退役

实际 R12 为 UTC `2026-10-08T04:32:16.047369` 至 `04:40:22.157985`，产品来源 B879 / B0 与 package SHA `01b2b54a…` 保持；外置检查器来自 Web 提交 `a0d5e62aa72b` / SHA `999c11ab87830585a6d66504a5842312f7ac129df1d9e9df23284c8f56ebae52`。新 r2 / native14 的准备与同盘数据转移各真实成功，缓存峰值 54,534,144 B，独立 F 回执保留全部 117 帧 / 两资源流。原四合成文件及实际非空 WAL / SHM 按 dev / inode / size / SHA 转移，未复制第二份 raw，未重用旧失败报告。

七个来源 / 77 HTTP 与完整数学通过；首次 BMS / mania 64.433 / 148.999 ms，原 API 与目录全部通过，目录 338,121 张 / 九 HTTP / p95 161.578 ms。四来源各 29,204 人的完整原生 gzip 为 9,623.707 / 9,300.578 / 9,185.817 / 8,463.221 ms，完整字段、名次、原 ID、两种明确 413 和真实独立灯检查保留。api-core 子 PID 2664252 实际 exit0 / wait 回收，但这不代签整轮。

分页子 PID 2665107 在 `actual_complete_verification_child_source_and_cgroup` 失败，实际 TERM / wait 为 -15，日志 0 B、报告不存在；原断言未落不匹配 argv / cwd / cgroup，失败原因仍未知。该段两帧 / 0.103720 秒，最低 MemAvailable 689,278,976 B、磁盘 2,962,169,856 B，swap / OOM 零，仅证明这一观察段，不证明整轮或完整分页通过。driver / owner 均实际 loaded / MainPID 0 / exit1 / exit-code，driver 峰值 252,502,016 B。全部 23 资源流 / 1,999 原帧、SHA / 行数 / 完整 gzip EOF / CRC 和真实终态在 F 的 `run-r12-actual` 完整保全。分页、burst、1,800 秒、同出口 / 配额、结束投影与两空恢复均未到达。

检查器现记录预期身份及首次 / 末次实际字段、轮询数 / 耗时；成功须精确 command / cwd / 同 cgroup、同 PID / starttime 且进程存活，10 秒期限内才接受。600 秒总门从 Popen 前计时，身份等待只消费原剩余时间；失败仍 TERM → KILL → 实际 wait。父 Observation 从 Popen 前开始、子初始化 / 完整来源和投影哈希均在原 driver 256 MiB / high240 / CPU50 / swap0 内；父后端连续所有权、全部原请求与资源门保持。修正 SHA `f46f33a1e137a8f1a7cb6e3233540b3abe8bbbcba7dba2d12d7ca4d3a6567a1a` 的只读复核无剩余阻断，尚未实际重跑，不重标原 R12。

此前 R5～R11 七份完整失败 archive / sidecar 在 F 重新逐件 SHA / size 核验，共 738,507,369 B gzip。首次退休入口在任何删除前因 R5 / R6 历史控制器实际 not-found 与预期不同失败，原源 / 日志保留；不是自动审批拒绝。r1b 将缺席控制器与实际 loaded 停止单元分别记录，核对确切十四路径 / 来源 / 停用 / 无 lsof 占用后仅退役服务器重复 gzip / sidecar，真实有限单元 MainPID 0 / exit0 / success，128 MiB / CPU50 / swap0。实际空闲变化 +738,672,640 B，完成时可用 2,965,970,944 B；F 全件保持，真实恢复预算仍未签。独立回执 `server-failure-duplicate-retirement-r1/independent-actual-retirement-receipt.json` 保存两入口真实终态和十四路径实际缺席，不把这一边界采样当作持续门。通用 journal 的外存及 512 MiB 保留决策仍待用户授权，未读取或修改。

R12 完整失败现场随后由 R13 保全 controller PID 2673651 / worker 2673672 实际成功终态保存，源码 `a1d3f443…`、128 MiB / CPU50 / swap0。F 的 `r13-actual-preservation` 完整 archive 105,649,886 B / SHA `2ea977c42b1dd5497fb35d9e7ef389240255ed12f05b6c3a516e9b33c64615f4`，232 成员逐项 SHA / size / 完整 gzip EOF / CRC、原 22 表指纹按停止库字节一致保全；全部 976 帧 / 原 SHA / gzip 校验通过，最低 MemAvailable 792,317,952 B / 磁盘 2,854,600,704 B，没有第二份 raw。独立完整 F 回执 SHA `af93c5b8fde39928f7bf17671a70d6ce7a6009084da32598084e9b6ab52fc30c`。

新检查目录 r3 / native15 的九控制源、完整 F 输入及准备 / 转移 / 启动脚本先只读复核再上传，全件实际 SHA 绑定。原 R11 安装及 package 的实际路径不改；准备和同盘停止数据转移均实际 loaded / MainPID 0 / exit0 / success，F `staging-preparation-r13` 保留两流 / 123 帧及实际缓存峰值 57,335,808 B。工具装入且核 SHA 后才登记实际 PHP 2679756 / Nginx 2679758；UTC `2026-10-08T05:12:37.503909` 启动 R13 owner 2682209 / driver 2682213，使用 Web `60e28ecba6378ca9086fd6f2c2a39460fe748de3` / `f46f33a1…` 和 probe `ee62d453…`，原 B879 / B0 产品包不变。该轮随后实际失败如下，不补签总门 / 原 R12 或两恢复。

`recovery-protocol-r13` 的五预备源已 AST / SHA / 只读复核，原 R12 源及准备回执保留。仍必须先取得真实成功 R13 run / owner，再消费实际数据库 gzip / sidecar、raw / WAL、恢复 source / cache 峰值、八对和 2 GiB 余量；主 run 的子进程资源不代签恢复进程。两空恢复尚未执行，prepared 不能当部署或恢复通过。

### R13 实际资源失败与完整原生解码修订

R13 实际于 UTC `2026-10-08T05:20:43.988724` 结束，owner 2682209 / driver 2682213 均 loaded / MainPID 0 / exit1 / exit-code，driver 峰值 252,604,416 B。全部九次实际子进程启动在首次轮询精确匹配预期 argv / cwd / cgroup / PID / starttime 且存活，耗时 1.4～3.8 ms；不据此推断原 R12 的未记录失败原因。七独立来源 / 77 HTTP 和数学、首次个人、目录及四完整 29,204 人原生榜内容通过，目录九请求 / 338,121 张 / p95 127.589 ms。真实独立灯由 6 升至 8，EX 183 保持；最后记录在资源断言前，不把内容通过当 api-core 成功终态。

api-core 子 PID 2687210 实际 exit1。完整父观察 `api-core-worker` 为 315 帧 / 87.769 秒，最低 MemAvailable 534,925,312 B（510.14453125 MiB），四帧共约 0.861 秒低于 512 MiB；内层 `original-API` 为 173 帧 / 49.673 秒，最低 536,379,392 B（511.53125 MiB），一帧低于门。同一内层最低帧 driver 两进程 PSS 178,791 KiB、backend PSS 111,516 KiB；swap / OOM 零、磁盘最低 2,843,197,440 B。实际总门 `shared_host_512MiB_no_swap_no_OOM_and_disk_margin` 失败，不能由两个观察中较高者补签。完整分页、burst、1,800 秒、同出口 / 配额、结束投影和两空恢复未到达。F 的 `run-r13-actual` 保留全部 22 流 / 1,992 原帧、SHA / 行数 / 完整 gzip EOF / CRC、报告 / 日志与实际终态；原 R13 工具字节和失败保持。

停止现场由 R14 保全源 SHA `65a0bd1b20efcc45dc57fd83606a60b55effb5b97b8d6462dec0169d89bee5e5` 处理，实际 controller PID 2696654 / worker 2696673 均 loaded / MainPID 0 / exit0 / success。F 的 `r14-actual-preservation` 已完整保存 archive 105,662,318 B / SHA `09abb1535570cfce39ab899dc3081da3c9087c230783248e34f8918760a4bc9e`，239 成员逐项 SHA / size / 完整 gzip EOF / CRC 与停止库全 22 表指纹的字节一致证明通过；没有本地 SQLite 重读或第二份 raw。全部 984 原资源帧 / SHA / 行数 / gzip CRC 保全，最低可用内存 806,842,368 B / 磁盘 2,735,370,240 B；独立完整 F 回执 SHA `bb118a3e3de8cf8a1f6d22f809d95e1a2d9e1287625eda5b58e29a74dd11994b`。只证明失败保全，不补签运行或恢复；仅停止专用 staging，未访问正式数据或通用日志。

Backend 的外置 `multisource_probe.py` 只在 `native_stage` 的四次完整原生请求启用对象解码钩子：每行全部字段都解析，立即释放不参与本阶段校验的重复 identity / lamp / conditions / native 图，保留原 `native_player_id / is_me / ex_score` 值；顶层元数据 / 灯汇总不变。原完整收包、gzip EOF / CRC、传输与解码字节上限、全部行数 / 身份唯一 / 本人一次 / 分数排序 / 并列名次 / OpenLR2 灯汇总 / 10 秒断言及观察范围保持；默认调用、独立灯和两个明确 413 使用原完整解析。真实产品 B879 / B0、API 和数据库未改。

新增 loopback HTTP 测试覆盖 gzip / identity 编码、完整字节度量、全行 / 原值 / 元数据 / 灯汇总、默认完整字段、损坏 gzip 的明确失败，以及原 `native_stage` 的四版本 / 并列 / 两个 413。首条 focused 命令的相对 `--basetemp` 指向没有父目录的 Backend 临时路径，5 passed / 19 setup errors；原 `native-probe-decoding-focused-r1.xml` 保留，不作为有效 gate。改用入口实际创建的 F 盘 Web 临时目录后，24 项 / 10.49 秒通过，`native-probe-decoding-focused-r2.xml` 长期保留，既有 Starlette / httpx 弃用提示不变。只读 diff 审查无阻断；必须绑定新的 probe 提交和 SHA 再在原共享预算重跑，不能由软件结果宣布资源门通过。原五 R13 恢复源未执行，不能在新 probe 来源上复用其签收。

### R14 新工具实际重跑与恢复预备来源

外置 probe 从 Backend 已提交 `967af4d26248274a79f7ceee2b5f1bff8f323484` 导出，实际 SHA `85d396aab0770dcc3da6e41cb9aa3ce0911198a2af5e2aed4056ef66e49bbfc9`；harness 仍 Web `60e28ecba6378ca9086fd6f2c2a39460fe748de3` / `f46f33a1…`。产品来源 B879 / B0、实际 R11 安装和 package `01b2b54a…` 不改。九控制源在 F 全件 SHA / AST、只读复核后上传到新 `20261008-r14`；停止 R13 的全 F seal `bb118a3e…`、实际失败终态、全原成员和 main / WAL / SHM SHA 均先核验，才将同一四合成输入从 r3 同盘移动至新 r4，没有第二份 raw。原输入 / 失败 / 预备源不覆盖。

实际 prepare PID 2703390 / transfer 2704009 均 loaded / MainPID 0 / exit0 / success，128 MiB / CPU50 / swap0；F 的 `staging-preparation-r14` 已保留两完整资源流 / 126 帧及真实缓存峰值 57,663,488 B。新核 SHA 后才登记 native16 PHP 2703623 / Nginx 2703625；真实 owner PID 2705880 / driver 2705884 于 UTC `2026-10-08T05:55:30.041243` 启动，1800 秒、全部请求、原 256 MiB / high240 / CPU50 / swap0 预算保持。R14 本地 retainer 原生成字段错误标为 F_R11，执行前修正为实际 F_R13 并同步 builder，旧回执不改；实际来源复核回执在 `runtime-source-controls-r14`。

本段取截至 UTC 06:08 的运行中分项：七个来源 / 77 HTTP 与完整数学通过，首次个人 worker 实际 completed；对应完整父观察 324 帧，最低 MemAvailable 694,001,664 B。api-core 实际 completed，四份各 29,204 人完整原生为 9,925.515 / 9,421.013 / 9,624.943 / 9,097.898 ms，全部完整字节 / gzip / 身份 / 本人 / 并列名次 / 灯汇总及两种 413 通过；目录总数 338,121 / 九 HTTP / p95 138.198 ms。api-core 完整父观察 332 帧，最低 MemAvailable 596,721,664 B（569.078125 MiB），原 512 MiB 门通过；独立灯内容保留。尚未取得整轮成功终态，不能用这两段资源补签分页、burst、持续、同出口 / 配额或恢复。

`recovery-protocol-r14` 五预备源已分别绑定实际新 r4 / native16 与 probe967af / 85d396，原 R11 package 实际路径保持。AST / SHA 和只读复核无剩余源码阻断；只签 prepared，未执行。实际 R14 run / owner 成功、独立恢复观察、原 22 表 / 非空 WAL 策略增量、完整 F 证明及八对 / 最大 raw / source-cache / 2 GiB 的真实预算仍是前置。原 R13 五源未执行、未替换成新来源。

只读外存盘点未发现另一份可新计入的 GiB 级已保全 raw：早期 e801 / 3ae / CBA 包和首轮 raw 的实际退役回执已在相应完整 F tar 内，不能重复计净空闲。R12 / R13 / R14 三完整 B879 gzip 与旧 277 包记录合计 375,219,377 B 加 sidecar；旧 277 的 F 包现独立核验 9,600 成员 / 完整 gzip CRC，通过回执 `package-r6/independent-all-members-F-verification-r14.json`。其服务器实际存在、闲置、引用与净空闲还须在运行结束后复核，不先记退役或节省。通用 journal 授权仍待，未读取或修改，不自行购买资源。

### R14 完整运行成功、R15 原件保全与实际压缩预测

R14 于 UTC `2026-10-08T06:39:18.348420` 完成，`verification-run.json` 的 `staging_host_gate=true`；原 owner 2705880 / driver 2705884 均实际 loaded / MainPID 0 / exit0 / success，driver 峰值 252,444,672 B。七来源、首次个人、完整目录 / 原生与独立灯、全部 1,464 次分页及原始数学、burst 和结束投影均通过；原 public projection 的完整 SHA / 元数据保持。软件、产品包、外置 probe / harness 来源沿上一段，原 R11～R13 失败不改。

| 实际阶段 | HTTP / 写入结果 | 资源观察 |
| --- | --- | --- |
| 持续读榜 / 交分 | 9,000 读取全 200；250 OMS UUID 新局、250 外部最佳更新、50 社区写全部确认，重复新局为 0；确认 p95 分别 109.736 / 49.305 / 25.668 / 51.816 ms | 1,801.188 秒 / 6,739 帧，最低 MemAvailable 645,066,752 B，最低磁盘 2,675,744,768 B |
| 同期真实 PHP / Nginx 页 | 900 页全 200，确认 p95 304.875 ms / HTTP 最大 615.920 ms，满足原 PHP 1 秒门；50 个实际 loopback 来源 peer，访客转发头不选额度桶 | 与同一持续窗口、原 UUID / 外部 / 社区写重叠 |
| 同出口读榜及密码登录 | 650 读为 600×200 / 50×429；50 账号遵守实际密码单槽 / Retry-After / 登录额度，66.792 秒从计划 burst 起全部确认，队列耗尽 | 68.819 秒 / 258 帧，最低 MemAvailable 588,206,080 B |
| 真实 peer 配额 | Nginx API 与 PHP SSR 各 650 读均为 600×200 / 50×429；另一真实 peer 两请求 200，伪造 XFF 桶为 0 | 15.851 秒 / 59 帧，最低 MemAvailable 631,480,320 B |

全部 29 资源流 / 10,462 原帧已独立导出至 `run-r14-actual`，每流原 SHA / 行数、报告最小值及完整本地 gzip EOF / CRC 一致，压缩合计 2,261,566 B。全阶段最低 MemAvailable 588,206,080 B（560.95703125 MiB），host / 每组 swap 和 OOM 均零，最低磁盘 2,675,744,768 B。保留实际 ExecStart、准确工具 SHA 和 loaded 终态；这一真实完整运行门不代签新空恢复、磁盘八对 / raw 预算、公开生产或真人门。

原停止现场由 R15 成功保全源 `b1c43346495c3156fb47acfbad61373a094c803a00c488e544e976dd0f2e64e3` 处理；实际 controller 2739778 / worker 2739785 均 loaded / MainPID 0 / exit0 / success，128 MiB / CPU50 / swap0。源直接消费已在本轮关闭的真实 PHP / Nginx 终态，不对死 PID 重新建立 BudgetUnit、不重复关闭。F 的 `r15-actual-preservation` 完整 archive 107,025,395 B / SHA `52fb143d3fb2e6ab49c4a48b2578ed0977ed94138fa847fe2c568fe7ae833402`，257 成员逐项 size / SHA / 完整 gzip EOF / CRC、原 22 表按停止库全字节一致保全；全部 1,036 原资源帧及 SHA / CRC 保持。最低可用内存 639,082,496 B / 磁盘 2,568,843,264 B，无第二份 raw；原成功不改为失败，未访问正式库或通用日志。

三旧失败 B879 gzip / tar.json 与历史 277 包在 F 再次整件 SHA 绑定，计划 SHA `8d9257796381cef6b79688f97947bda62a38fb74121f01ea31b0a9839bd8626e`，源 `915c72ac…`。所有实际停止单元、引用、确切路径 / SHA 和 lsof 在删除前核验；唯一七文件由有限单元 PID 2745214 实际退役，loaded / MainPID 0 / exit0 / success。净空闲变化 +375,312,384 B，完成时可用 2,944,094,208 B，完整 F 回执 `server-exact-duplicate-retirement-r2/independent-actual-retirement-receipt.json`；正式 current / 数据 / 公开投影 / 固定 helper / 当前 B879 package 保留。仅边界采样，不签恢复容量。

随后有限单元 PID 2746669 仅测完整停止合成 main 的 level6 压缩，来源 `b3afc393f3b708c6fd959d1a3344291aca093c8ff4a7a57b630563ddc77a9c7d`。先消费真实七文件退役终态与相同 plan SHA，核原 main / WAL / SHM 的存在集合和逐 SHA，再比全 22 表；实际 checkpoint 为 `[0,0,0]`、原 WAL 0 B，显式 close 连接后完整逻辑指纹相同，main 仍 1,415,454,720 B / SHA `8a3ab7db1caa96bff8442bb4d15e934091ad9e6c3d1b52563cbd550b54c95a0e`。完整 gzip 为 103,017,163 B / SHA `8d45b0718667065db870daad6553cace956945cae9deddcbc22ee28067a2f0a1`，在 F 独立解码全部字节、核原 SHA / size / gzip EOF / CRC；无第二 raw。457.588 秒 / 1,706 原帧与真实 loaded 成功终态均保全，最低可用内存 811,220,992 B / 磁盘 2,838,175,744 B，128 MiB / CPU50 / swap0。

`stopped-gzip-capacity-r1/independent-complete-F-capacity-forecast-receipt.json` 明确仅压缩预测，不是 `SQLite backup` 一致快照、两新空恢复或正式容量门。按完整压缩值、每 sidecar 1 MiB、八对、当前最大 raw 与 2 GiB，基础所需空闲预测为 4,395,464,280 B；尚须实际恢复源 / 缓存与非空 WAL 峰值。预测结束时当时空闲 2,838,183,936 B，差 1,557,280,344 B。完整 F 保全后的成功 / 预测两 gzip 已按确切路径、完整 SHA 和 lsof 核验退役；有限单元 PID 2753929 实际 loaded / MainPID 0 / exit0 / success，源 `2244ebea17124fe8530f54d2a6396754cfba80d9583c48136c84107d0f31d623` / plan `e5b5fa1c6304d138027f6c8e2ea9e7fe6eb50a5ef90859652c18c02e025bfd2f`，净空闲 +210,046,976 B，完成时可用 3,048,042,496 B。独立 F 回执 `server-success-forecast-duplicate-retirement-r1/independent-actual-retirement-receipt.json` 已保全真实终态、原报告 / 日志 SHA、两确切路径缺席和两份完整 F gzip；原 main / WAL / SHM、R15 sidecar、正式 current / helper / B879 package 保留。基础预测仍差 1,347,421,784 B，不能据压缩或退役签完整容量。

### 系统日志原件完整 F 保全与实际 512 MiB 保留

用户 2026-10-08 明确回复“同意，保全核验后清理旧日志”。授权范围是先完整保存并核验系统日志，再清理服务器旧日志；未购买或扩盘。原件实际为 46 个 journal / apparent 2,113,929,216 B / allocated 2,061,086,720 B，只有两个 active，合计 37,748,736 B；`/run/log/journal` 实际零文件。OMS namespace 原 `SystemMaxUse=32M / MaxRetentionSec=14day / MaxFileSec=1day` 保持，默认 namespace 480 MiB，两者合计上限 512 MiB。

实际 systemd 255.4 的[官方 rotate 源码](https://raw.githubusercontent.com/systemd/systemd/v255/src/journal/journald-server.c)会自动 vacuum，不能先 rotate 再声称全原件保全。首次保全源 `8a7c3259…` 和独立 CONT 看门源 `129a4192…` 在固定 128 MiB / CPU50 / swap0 内分别 sync 两个 namespace，独立 ready 看门有效后短暂停写。44 个已封闭原件同盘硬链接、两个 active 复制；实际暂停 0.651124 秒，两原 PID 1482909 / 4007287 恢复 running 后全部 46 件 `journalctl --verify` 通过。首轮 owner 2768130 随后传输实际 BrokenPipeError / exit1，F gzip 为 0 B；全部原失败、1,842 资源帧与 snapshot 保留于 `journal-first-transport-failure-actual-r1`，失败原因没有被补推成 SSH idle。

R2 只重新导出同一固定 cut，没有再暂停、旋转或重新生成原件。源 `e370635a…`、receiver `c7cdb618…` 经复核；有限 export owner 实际 loaded / MainPID 0 / exit0 / success，峰值 21,680,128 B。F 的 `journal-full-F-preservation-r2/complete-original-systemd-journals-r2.tar.gz` 为 547,802,803 B / SHA `7b0e14560ded5d32ac84eb6c1aa8ee0f823699b577f7569b7471f1a99336f38e`，46 原 journal / 52 成员逐 SHA、size、完整 gzip EOF / CRC 与原可读性证据全部核验。独立 F 回执 SHA `1518fdf0…`；全部 1,007 原资源帧也独立按 SHA / count 核验，最低可用内存 822,603,776 B，swap / OOM 零。原压缩件仅存受保护 F 证据目录，不进入 Git；服务器没有新增大 gzip。

随后才执行 source `519a6b28…` / receiver `35480024…` / plan `67b1d0c3…`：先新核完整 F SHA 与原配置，再解除 46 个准确 snapshot pins / active 副本。仅添加默认 `/etc/systemd/journald.conf.d/90-oms-shared-host-budget.conf` 的 `[Journal] SystemMaxUse=480M`；一次 restart default 后 rotate / vacuum，分别 sync default 与 OMS。原 OMS 32 MiB 策略未改。真实 owner 2785801 loaded / MainPID 0 / exit0 / success，128 MiB / CPU50 / swap0；全部 61 原资源帧核验通过。日志实际 allocated 488,648,704 B，测得净空闲 +1,610,194,944 B，完成时 root 可用 4,614,737,920 B（约 4.30 GiB），完整 snapshot 目录实际已解除。实际原 report / config / log / raw frames / terminal 在 `journal-budget-actual-r1/independent-actual-journal-budget-receipt.json`。

这些实际结果只签原件保全和已授权日志容量。基础恢复盘账 4,395,464,280 B 已可容纳，但恢复 source / cache / snapshot 与 WAL 峰值仍须实测。正式 current / 账号成绩库 / fixed helper / 公共投影保持原状态；两新空恢复、最终盘账和新站切换仍未签收。

### 旧闲置候选的准确源码退役与两空恢复启动

旧 277 原 F 包 58,251,923 B / SHA `fcf59e4a…` 的全部 9,600 成员、map与9,598个源码资源、完整 gzip EOF / CRC 在准备及执行前分别新核验。plan `73e89196…` 将原空 ready 的实际 dev / inode / size / mtime 保存 F；源 `5485d063…` 和 receiver `87903ae0…` 经只读复核，无剩余阻断。执行时正式 current 仍 D1 / e6，B879 环境独立；两次 `/proc` argv / cwd / maps / FD及OMS实际单元、正式配置检查均无 live 引用，才解除同一个空 ready 和全部固定 SHA / size 的 9,598 个普通文件，不跟随 symlink、不递归删除旧环境。

真实 owner 2793879 loaded / MainPID 0 / exit0 / success，128 MiB / CPU50 / swap0；77 原资源帧逐 SHA / count 核验，最低 MemAvailable 846,622,720 B。净空闲实增 121,434,112 B，完成时 root 可用 4,735,619,072 B（约4.41 GiB）。`.venv`、非清单生成文件、map / release.json、archive symlink、uv / cache / managed python、当前正式发布、fixed helper、B879包及所有验收库 / 证据保留。F原包、原 empty-ready metadata、typed / raw terminal、全部原件和原帧在 `unused277-mapped-retirement-actual-r1/independent-actual-mapped-retirement-receipt.json`；不签恢复或部署门。

`recovery-protocol-r14` 五源的准确 SHA 与既有只读复核保持；四主机源按各自 `__file__` 约束名上传 r4，并在启动前全件 SHA 核验。新 owner 2797323 于 UTC `2026-10-08T08:50:33` 以128 MiB / CPU50 / swap0实际启动，driver 2797345为256 MiB / high240 / CPU50 / swap0，只消费原成功R14运行及actual owner终态，原R11的B879完整包路径不改。两新空目录、原22表 / 撤钥隐藏增量WAL、完整前后端 / 原生 / 分页、F全件交接、source-cache峰值和真实盘账正在执行；该启动记录不是恢复通过。实际两门及最终切换仍待。

### R14 两空恢复失败与输入修订

实际恢复于 UTC `2026-10-08T09:38:15.010236` 失败，driver / owner 均 loaded / MainPID 0 / exit1；原 `verification-recovery.json`、owner、源码和终态保持。第一轮新空目录的全22表、API / 玩家 / PHP、完整1,464页（最大126.335 ms）及四原生通过，完整F包 / snapshot pair共11,548项独立SHA / gzip EOF / CRC已核验，随后准确退役其恢复工作区。第二轮实际raw恢复1,415,491,584 B / SHA `627a3dd88c55837cbd8a5cc2a29f01ba71f5bf223c6a3338e432beceb1846e66`，一致gzip103,043,775 B，恢复前后22表比较、实际WAL撤销隐藏、9598源码及其API / 玩家 / PHP已到达；完整分页在首个请求的复合门 `full_board_all_pages_300ms` 失败，原请求状态未保存，不能据标签宣称慢于300 ms。四原生及第二轮完整F交接尚未执行。F的 `empty-recovery-r14-failed-actual` 保存全部29资源流 / 11,659原帧，完整SHA / 行数 / gzip EOF / CRC和真正失败终态；最低可用内存622,678,016 B，最低磁盘2,986,385,408 B，不能签恢复总门。

源码审查发现第二轮主动注销 `users[0]` 桌面会话、并已检查其旧access / refresh401，随后分页第1页却重用该旧access。公开board带Authorization时按原合同验证登录，revoked session明确401。检查器现保存逐页请求度量及失败页身份 / 状态 / 耗时；第二轮完整200分页轮转其余49有效身份，`me`随同一身份校验，期望榜仍保留全部玩家 / 来源 / 人数 / 灯 / 名次，300 ms门保持。正常运行和第一轮仍使用全部50身份。下一步在同一个实际第二轮还原现场独立补验全部HTTP及四原生身份映射，绑定停止原件、前后业务 / schema指纹，再执行完整F交接和全部实际峰值盘账；不回写原失败报告、源码或owner为成功。

恢复等待期间按既有“保全核验后清理旧日志”授权，又退役原完整F日志切面中的四个准确closed文件，两批实测净空闲变化95,559,680 / 98,832,384 B；不旋转或改上限 / 活跃文件。F的 `additional-two-closed-journals-actual-r1/r2` 保存各7帧、原实际成功终态、删除清单、完整F核验和原配置指纹。第二批原收集SSH连接超时，失败源保持；之后只补收同一已成功关闭单元的缺失证据，未重跑清理。最后恢复余量仍按实际全部采样另验。


## 第二次恢复补验与正式切换前保全

第一轮 R14 空恢复及其全件导出 / F 核验 / 精确退役已实际通过。原第二轮原始库、9598 项源码、离线虚拟环境与 fresh 缓存也已还原，原完整检查器在主动撤销 user0 的桌面会话后，仍把该 access token 轮入全分页请求而失败；原合取断言没有记录失败请求，不能把失败说明为已经证明超过 300 ms。Web `133eb509b273` 的外置工具显式接收有效用户范围，每次请求先留状态 / 延迟，失败前落原度量，原 300 ms 与完整榜数学保持。原 R14 driver / owner 的 failed / exit1、全部 29 流 / 11659 原帧和第一轮完整 F 证明保持，第二轮采用独立补验，不重标原失败或伪造第三次 raw 还原。

独立补验 r1 因 Nginx 标题成员检查失败，r2 因沿用旧 sample 文件名失败，原件均完整保全。r3 实际完成 99 次正常 refresh，最新凭据逐次原子保存为服务器私有 0600 文件；Nginx 在 Type=exec 返回之后合法将 argv 改为 master process 标题，同 PID 2868624 / starttime / cwd 完全一致，检查器过早绑定 argv 而误报 `owned_pid_not_reused`。r3 的三完整资源流 / 847 帧、真实失败终态及 0 B 孤立 auth sample 在 F `second-restore-completion-r3-actual` 完整保全，诊断保存初始 / 实际身份；已旋转 refresh 不能再从原 credentials 消费。精确关闭该 Nginx 的首入口已执行 stop，随后因期待缓存旧 PID / exited 的断言失败；原源保留，独立只读收取真实 loaded / inactive / dead / MainPID0 和 PIDgone，真实 ExecMainPID0 / MemoryPeak=[not set] 原样记录，不重复 stop 或补签旧终态峰。

补验 r4 实际于 UTC `2026-10-08 10:52:52` 启动，driver PID 2877091；源 `b218295686a5b0346656971ffa08a889635084242b6e56f83bf8f8bad633c0a7`、绑定 `24c9a24d…`。先核上轮 F 失败 / 关闭 / 新凭据 SHA 和全部账户身份，真实首页 200 就绪后再绑定新 PHP / Nginx 身份，全部观察 / 报告为独立新路径；99 次正常刷新、撤销会话 / 密钥、原生旧身份、完整 API / 玩家 / PHP / 全分页 / 四原生及全 22 表核对保持。该次随后真实失败：冻结检查器的 UNIT_PROPERTIES 没有读取 ControlPID，新关闭检查在前置消费该字段而 KeyError；实际业务与新凭据尚未操作。原 failed / exit1 与一流 / 两原帧已完整 F 保全。新 r5 明确一次读取实际 ControlPID，与原部分字段读取分开，其他预算、稳定身份及完整检查保持；源 `64fcf4b5…`、启动器 `c50a7cba…` 已 AST / 绑定核对，并于 UTC `2026-10-08 11:10:45` 实际启动，driver PID 2884955；完整门仍运行，未按启动或单项结果签收成功。第二轮全件 F 导出、有限 worker 精确退役和八对 / 最大 raw / 2 GiB 最终盘账也未签。

原固定日志 cut 的 46 件已完整 F 核验后，追加准确清理的四件旧 closed journal 原终态保持；再追加三件也已实际完成，源 `9e1bbc17…`、有限 worker 成功、全部 10 帧留 F `additional-three-closed-journals-actual-r3`。三件实测净增可用空间 148500480 B，结束实余 3214774272 B；这一实际值包含尚在盘的第二恢复与共享主机其他活动，不当作完整恢复预算通过。default480 + 既有 OMS32 MiB 的合计 512 MiB 保留设置保持。

正式切换前新鲜配置已完整保存并逐件 size / SHA 核验至受保护 F `production-before-switch-r4`：11 件实际 OMS / 个人站 / shared Nginx 规则、IR / catalog / fixed backup / timer unit、旧真实 format3 内联 files manifest 及固定维护源码。旧 manifest 原样保全，不臆测 runtime-files.json 必然存在。8081 / 8082 健康均实际 200，timer 仍 enabled / active / waiting，尚未暂停、未启动本轮正式备份、未切 current。准备入口的旧 ACL shell / 错误 manifest 假定各自原件保留，不作为完成证明。正式备份观察源 `c98a4917…` 与第二轮导出收尾源 `81c6e8b7…` 只读复核及本地 AST 已过，尚未实际执行；终态可得性、真实当前 InvocationID / PID 的完整流、全件 gzip / raw / 22 表及 worker 独立期限仍须实测。

## 两次恢复完成与正式备份接续

2026-10-08 第二轮独立补验 r5 于 UTC `11:10:46.787116` 至 `11:21:54.424692` 实际完成，原 PID 2884955、loaded / MainPID0 / exit0 / success。完整 29,250 人的 1,464 页全部 200，最高 124.325 ms；四次完整原生 29,204 行为 9,261.613 / 9,026.690 / 8,764.532 / 8,134.590 ms。99 次正常续期、已撤销桌面仍 401、原生旧身份、隐藏及密钥边界与完整 22 表对照通过；只允许真实会话、配额变化。全部 10 资源流 / 2,360 原帧及终态留 F `second-restore-completion-r5-actual`。原 R14 / r1～r4 的失败不改。

同一第二恢复的有限导出 / 退役收尾 r3 于 UTC `11:23:39` 实际启动并成功，源 `3b26991d…`，父 PID 2892020 与两个独立 worker 均 loaded / PID0 / exit0 / success，128 MiB / CPU50% / swap0。11,550 项完整 archive 为 168,063,778 B，SHA `314c1b4b58f5df91eea07e73c9b08059f8e03503ceb3e5ca461de7f3ce44b1ac`；F `empty-runtime-r14-2` 完整 gzip EOF / CRC、全部成员 size / SHA 与 snapshot 对均核验，raw / WAL / SHM 字节等于已测完整 22 表停库组合。回执如实记 `local_SQLite_reread_executed=false`，不把字节继承证明说成本地重读。F 完整回执送回后只精确退役该第二恢复 raw / snapshot 两件，原库未动；六资源流 / 3,327 帧、真实终态及导出证明留 `second-finalization-r3-actual`。第一恢复原导出 / 退役两流的遗漏也独立补收共 961 原帧，不伪造原回执覆盖。

汇总实际验收源 `eb247097…` 于 UTC `11:36:56` 通过：`recovery-protocol-r14/actual-two-restores-capacity-r1.json` 逐件绑定两完整 F 恢复及全部 81 资源窗口 / 29,724 原帧。最大 main + WAL 1,422,161,928 B，八对压缩件 / sidecar 加 2 GiB 的保守底线 2,980,222,456 B；实测终态空闲 4,661,727,232 B，合计所需 4,402,384,384 B、余量 259,342,848 B。恢复全窗口最低可用内存 622,678,016 B，swap / OOM 零；原恢复空间最低只高于底线 6,162,952 B，如实保留，不四舍五入成宽裕。这一门通过不等于生产或真人 P/C。

UTC `11:39:04` 原 timer 在核原配置不漂移、旧 worker 已成功关闭后实际暂停，enabled 保持，回执 `production-release-controls-r1/actual-installed-timer-pause-r1.json`；发布结束须恢复 active / waiting。R4 首次本地 ACL 核验将开发存储输出读为 JSON 而失败，尚未 SSH；R5 文件名绑定仍旧而失败，也未 dispatch。R6 已实际 dispatch 一次：固定 `oms-ir-backup.service` 的 InvocationID `a43659f4de76494da11ece2e89b47cc8` / PID 2902914 成功关闭，但 observer 在启动 61 ms 后因 bash 身份尚未通过而失败，原七帧均旧 invocation，不补签完整观察。完整原失败保全于 `fixed-production-backup-pre-switch-680f098971de`；随后仅从这次精确 invocation 完成行取得实际 `daily-20261008T114256Z.db.gz` 对并完整 F 核验 gzip / raw SHA、integrity / FK、22 表及当时真实 current 绑定，留 `fixed-production-backup-pre-switch-680f098971de-completed-pair-r1`。原 observer false 与正式备份门 false 保持，补验需有限等待实际 oneshot 启动身份和完整同 invocation / PID / cgroup 观察，不修改固定 helper、unit 或数据。正式 current 仍 `d1f052b93a81-e6fdf914cb04`。

## 正式发布与收尾

2026-10-08 原版网站已实际上线，最终 forward 于UTC `12:35:06.934686` 至 `12:35:11.684265` 成功；当前 `b879e4233818-b0feceae22e4` / schema3，状态 **已部署待验收**。真实库同一dev / inode265517，22表及原定义保持，正常启动只增加此前已采用的 `scores_directory` / `score_groups_public_directory` 两条普通目录索引；没有生产raw恢复、迁入合成账号、重造UUID或旧身份认领。catalog原PID1862556未停止，三个源码文件与新包一致；固定维护包D1/22不改。

### 固定正式备份观察完成

R7观察源 SHA `97a0d2a727a490ab1bd4020d428cc8e5fef2e0c3c02038eb33301e1d65bfb021` 经AST / 只读复核后实际执行。oneshot启动最多30秒等待，同InvocationID / ExecMainPID、实际cgroup成员及原argv / cwd / starttime须精确符合；每个候选身份均原样保存，ControlPID或MainPID只在真实同实例内接受。完整流与最终同实例终态分别核对，不用后来成功补帧，不放宽固定128 MiB / CPU50% / swap0。

| 正式对 | 实际身份及 F 目录 | 完整运行证据 |
| --- | --- | --- |
| 发布前 `daily-20261008T120531Z.db.gz` / 同名JSON | PID2913687 / InvocationID `cfe2f25eeb744c9dafebe84fc9cc842e`；`fixed-production-backup-pre-switch-f3f004b6adaa` | 109原帧 / 104匹配live；最低MemAvailable843,034,624 B / 空闲4,659,793,920 B；真实终态峰134,217,728 B / exit0 / success |
| 发布后 `daily-20261008T124145Z.db.gz` / 同名JSON | PID2940634 / InvocationID `1be3e1a9061e4baa8cc94dc1b1217210`；`fixed-production-backup-post-switch-7be5768366c7` | 113原帧 / 107匹配live；最低MemAvailable845,819,904 B / 空闲4,654,452,736 B；真实终态峰134,217,728 B / exit0 / success |

两完整gzip / sidecar在F三ACE受保护目录逐件字节 / SHA、完整gzip EOF / CRC、raw SHA、integrity / FK、全部22表 / sequence / 索引 / trigger及真实运行manifest绑定通过；raw分别233,472 / 241,664 B。业务库大小不冒充全量公开投影大小。原fixed helper / unit / timer配置保持；原R4 / R5前置拒绝、R6 observer false与独立完成对保全不改。

### 正式准备、首次失败与同库回退

prepare R2源 `8c1b38e6…` / 绑定 `633d0281…` 于UTC12:20实际通过，owner PID2921947、40完整原帧、真实退出成功 / 峰118,153,216 B。正式cache正确在 `/app` 与公开URL下生成；公开缓存父目录明确0755可遍历，private bootstrap / storage保持0700，不将0077私有进程掩码沿用为不可访问的公开父目录。正式PHP / cache unit以0644安装，原主IR / catalog / fixed backup保持。CLI cache真实128 MiB / CPU50% / swap0及终态，F全部配置 / 来源 / 原件绑定保持。

R3源 `f8e6286b…` 的第一次forward实际失败，F `production-native-forward-r1-actual` 的false保持。Nginx检查与直接reload返回0之后立即HTTPS读取仍落在旧worker：主页404，旧路径还返回旧slash规则。候选正常启动已增加两条批准目录索引；自动恢复正确停止候选主IR与PHP，但原严格schema全等检查拒绝这两条已证明兼容索引，使恢复停在服务关闭，造成短暂中断。原响应、全部资源、错误及schema差异保留，不把reload异步或旧守卫失败写成生产回退成功。

独立实际恢复只接受原全部schema定义加精确两条批准索引，恢复F原配对路由、current至D1/e6、旧主IR健康200及宝塔正式reload，新PHP停止 / disabled；同一库保留，不删除索引或恢复旧raw。实际owner PID2929173 loaded / MainPID0 / exit0 / success，完整14件源 / 报告 / 步骤日志与真实终态已独立收取到F `failure-recovery-r1-actual`。该收取明确没有完整资源采样，不伪签资源门，也不重跑已结束恢复。

修订R4只在此真实故障范围内处理：停止主IR即记发布变动、任何schema守卫之前停止候选主IR / PHP；兼容检查保留原全部定义，最多允许这两索引；宝塔用实际 `/etc/init.d/nginx reload`，随后30秒有界检查真实HTTPS就绪并留每次尝试。源 SHA `ce619c6476c4f004429328ec6ffdd133c2288749aadffc0037f8d1e32b3cb236`，绑定 SHA `3e54c957fd649befc8ee4c046f5610a7a00574f5a4c9ea1c21c7018ed0f0d973`，不修改B879/B0不可变产品字节。

| 实际阶段 | UTC起止 / owner PID | 完整 F 核验 |
| --- | --- | --- |
| 首次成功forward | 12:31:37.432068–12:31:42.243867 / 2930586 | `production-native-forward-r2-actual`，13原帧，实际终态峰23,584,768 B |
| 旧源码 / 旧路由同库回退 | 12:33:15.558872–12:33:19.346074 / 2933321 | `production-native-rollback-r1-actual`，9原帧，实际终态峰22,970,368 B；旧主页完整3023 B / SHA `5be0319667268160bbfc2a9df46fa176a57491276bca590f3e0c2e48508a5d86` 等于原manifest |
| 最终恢复新站 | 12:35:06.934686–12:35:11.684265 / 2936103 | `production-native-forward-r3-actual`，13原帧，实际终态峰22,413,312 B |

三次均真实loaded / MainPID0 / exit0 / success、128 MiB / CPU50% / swap0；原全部帧 / SHA / 行数及实际terminal独立核验。最终forward最低可用内存797,302,784 B / 空闲4,657,381,376 B，swap / OOM零。七页面实际200 / 重新验证缓存 / 安全头、八原插件完整字节、个人站原完整body SHA及固定helper / catalog均核对；每次保留同一live，不回灌旧数据。回退只签本次schema3与两索引范围，不宣称任意历史源码兼容。

### 公网核验、timer 与最终来源保全

公网R1实际207检查 / 562请求，196通过；11失败来自检查器把静态Blade页当IR React JSON、或把PHP空数组强当对象。R2依真实controller / action / section、原DOM、正文 / 新闻、完整导航与账号空数组核对，原件另留；18页检查等仍因root href实际无尾斜杠误报，且Ginger一次实际502 / 98 B / 3,734 ms。后续独立Ginger查询真实200 / 7,394 ms，不改原失败或推定其未记录错误原因。

R3只将空root path与 `/` 视为等价，仍保留其他path / 查询 / fragment及BMS / mania菜单参数；Ginger仍要求本次实际200、没有自动重试或换源补签，真实API错误先落公开code / message再判断。冻结源 SHA `967dbe0cf3aea5da20cf0f5a897c37ec686266d9e12fb135abf284f3727ea738` 经ROOT AST / SHA / diff核对后，于UTC `12:56:46.767101` 至 `12:58:47.032102` 实际 **207检查 / 564请求全部通过**，报告 `production-public-smoke-r3-actual/public-smoke.json`。这只签实际匿名公开HTTP，不签真人、浏览器、恢复或完整资源门。

覆盖原首页 / 两篇真实新闻全文、独立下载三步骤 / 帮助 / 许可、谱面目录与真实MD5详情 / 来源选择、三个真实下载源目录 / 详情、真实公开OMS ID1个人页、BMS / mania榜和实际空社区、匿名me401。来源筛选仍作用整榜，灯 / 人数 / 名次 / 条件 / 分页原合同保持。八原插件完整SHA及range206、对应AGPL源码整个gzip EOF / CRC和每成员绑定、164自站资源完整runtime-map字节与缓存、普通条件HTTP刷新两次200及整HTML相同、原个人站和资源、双站TLS及静态ACME404通过。未跟随下载谱包，未生成帐号 / 帖子 / mania玩家假数据；静态ACME404不声称实际续签已发生。

原timer于UTC12:44:45实际恢复 enabled / active / waiting，原04:15 CST / RandomizedDelay300 / Persistent配置和固定备份unit SHA未变；当时NextElapse为2026-10-09 04:16:57 CST，完整回执 `production-finish-r1/actual-timer-restored-and-current.json`。最后只读收取于UTC `13:02:46.039604`，actual current仍B879/B0，主IR / catalog / PHP running、原timer waiting、备份实际PID2940634已成功关闭。11件新实际配置完整SHA / size / 身份及三ACE私有F保全在 `production-after-switch-configs-r1/independent-final-production-state.json`；本次收取不修改主机或代签资源窗口。

最终瞬时MemAvailable868,077,568 B（约828 MiB）、root空闲4,645,654,528 B（约4.33 GiB）、swap0，loadavg0.07 / 0.03 / 0.02。真实阶段门取上方完整窗口，瞬时值不代替它们。F原旧路由文件为 `production-before-switch-r4/08-39.105.55.78.conf` / `09-oms-ir.conf`，新路由 / PHP / cache / 主IR / catalog / fixed backup / timer及default journal设置另完整保全，维护步骤取[当前维护](production-maintenance.md)。系统日志原件完整F保全与default480＋OMS32 MiB合计512 MiB限制保持，不扫描母库或其他私有数据，不增服务器旧设计备份。

线上浏览器初次创建30秒超时；inventory实际取得标题“首页 | OMS”的已存在tab，但绑定读取再次30秒超时，未取得线上DOM / 截图。工具结果保留F `production-browser-observation-r1.json`，不把tab标题 / HTTP / 本地截图代签线上视觉、普通浏览器刷新、点击、真实登录 / 密钥或下载入库。用户本地视觉认可保持原范围；接续[真人路径](production-maintenance.md#真人验收)，先OMS＋全量公开历史＋ED7K的P，再逐格完成指定宿主和玩法矩阵C。当前结论仅 **已部署待验收**，P/C、非调试客户端和原发行 / 设备 / 皮肤门均未关闭。
