# 2026-10-22 全工作区架构安全筛查

本轮范围为总工作区的七个正式 Git 项目、旧设计 / 上游参考副本的用途边界，以及这些项目使用的开发、部署、共享服务器和备份链。`private-data/`、HDD、玩家数据、私有素材与恢复私钥不进入源码扫描；服务器一致快照仅走已授权的受限备份流程，不读取个人行。此前 PHP / Nginx / 内核维护取[原记录](php-security-maintenance-20261022.md)，不重复算成本轮应用发布。下方原修复与验收保留上午证据，傍晚新增结论和维护另列，不能以重新整理日期刷新旧验证。

## 范围与方法

| 对象 | 实际架构与本轮结论 |
| --- | --- |
| `oms/` | net8 Windows 客户端，BMS / mania、外部谱包 / 皮肤 / 图片 / BGA、固定 OMSIR。核对实际 NuGet 图、原生 DLL 身份、官方公告及当前调用入口，修复本地 BMS 归档与外链信任判断；图片 / 原生媒体缺口见下节。 |
| `websites/oms-web/` | Laravel 13.35.0、Blade / React 17 / Turbo，PHP 仅承担网页；账号 / 成绩权威在 Backend。74 个生产 Composer 依赖没有确认的受影响匹配，另对新发布 Laravel 公告人工核对；npm 318 个锁定包版本对命中 Bootstrap 3.4.1 的旧 XSS 公告，但实际仅导入 Less，未加载其 button / tooltip / popover 插件。没有因此跨版本重写网站。 |
| `websites/homepage-website/` | Astro 6.3.7、sharp 0.34.5、Vite 7.3.3，391 个锁定包版本对中 13 个包有公告命中。生产只由 Nginx 提供静态文件，没有 Node SSR、`/_image`、远端图片代理或公开开发服务器；源码没有 View Transitions，也没有 CMS / 用户输入驱动的 RSS 或图片转换。旧依赖仍需安排构建链更新，不能称已修复。 |
| `websites/oms-website/` | 已退役的静态设计 / 回退来源。177 个锁定包版本对命中 braces 3.0.3 的构建期公告；不属于当前官网的运行依赖。保留历史原件，不以安全名义重启旧网站功能或重新发布。 |
| `oms-server/oms-backend/` | FastAPI 0.139.2 / Starlette 1.7.0 / Uvicorn 0.54.0 / HTTPX 0.28.1，实际 Python 3.12.14、SQLite 3.53.1。26 个 Python 包的精确版本扫描确认 certifi 受证书事件影响；已更新源码锁与线上实际环境。 |
| `dev_bridge_md/`、`oms_client_bridge_md/` | 文档 / 事实登记，校验脚本只用 Node 内建模块，没有 npm 第三方依赖或公开 HTTP 服务。核对脚本调用与项目范围；不改 API、事实来源、统一阶段或已有未提交工作。 |
| 参考与成品 | `osu-web-reference/` 是未运行的旧上游来源，不能当成可直接安全启动的环境；`deliverables/` 是私有成品与手动维护工具，不发布、清理或执行其内容。维护脚本另做只读边界检查。 |

npm 官方 audit 接口本轮两次返回 503，未记为通过；改用 OSV 对锁文件精确版本逐项查询，并回查维护者公告和功能入口。Composer / Python 亦保留原始响应。另对七仓当前源码和文档做有限模式检查，只记录规则、相对文件和行号，没有命中本次检查的私钥、GitHub PAT 或 AWS Key 签名；这不等于全历史凭据审计或证明不存在泄露。

## 已修复

- **本地 BMS 包导入**：原 `BmsArchiveReader` 会把流无界复制到内存并无界展开。现在本地 ZIP / RAR / 7z 与现有下载路径共用真实提取器：压缩包 2 GiB、展开 8 GiB、单文件 2 GiB、50,000 项、谱文本单件 32 MiB / 总计 128 MiB；声明与实际流量均检查。非 seek 流有界暂存到 F 盘，取消进入实际复制 / 解压；拒绝后回收本次临时内容、释放句柄、保留源包，单目录取消不再被吞掉后删除源文件。路径、冲突、链接和 ZIP 完整性沿原安全实现，没有复制第二套校验。客户端权威状态见 [P1-A](../../../oms/doc_md/subline/P1-A/DEVELOPMENT_STATUS.md)。
- **外链提醒**：空旧官网地址使 `StartsWith("")` 信任任意绝对 URL。现只信任明确配置的 HTTP(S) scheme / host / port，拒绝前缀假站、userinfo 和端口 / 协议变化；固定 OMSIR 同源链接仍按原合同处理。
- **冻结在线依赖**：MessagePack 3.1.8 → 3.1.9，三个 SignalR 9.0.17 → 9.0.21 引用同步。旧在线入口仍关闭；不能把依赖更新描述成修复了一个线上正在开放的 SignalR 服务。[MessagePack 公告](https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-qhrr-8q5h-9q3h)
- **服务器 Node**：NodeSource 的签名仓库内同系列更新 22.22.2 → 22.23.4，未切主版本或触发站点发布。此前没有 Node 常驻业务进程，主要影响 Homepage 构建及维护工具；更新依据为 [10 月安全发布](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases)。
- **证书信任**：实际 HTTP 应用和固定备份 helper 的 certifi 2026.7.22，以及宝塔环境的 2024.02.02，均更新为 2026.10.19。宝塔 Python 3.7 无法使用新版 pip，保留其 pip 代码，只将内置 CA 文件替换为已核验 wheel 中的同一公开证书束；没有把旧 pip 元信息改成新版。服务 / 面板重启后复验。Ubuntu 实际 CA 束不含本次被移除的根，无须再次手动改系统信任规则。[Python 官方说明](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576)
- **后续发布**：Backend 显式锁 certifi 2026.10.19，uv 改用 0.13.4 的官方固定 SHA；Web 安装器与 Backend 准备脚本要求实际 certifi ≥2026.10.19。线上两个环境对历史 lock 的唯一已安装依赖偏离是 certifi，另有独立 `runtime-security.json` 保留这项运行时补丁身份。原 HTTP release / 源码包不改标签，应用回退不能用旧 lock 重新引入旧 CA。

## 未解决及处置顺序

1. **ImageSharp**：framework 实际带入 3.1.11，不可信皮肤 / 封面图片解码可达。维护者确认 v3 的修复版为 3.2.0，涵盖 BigTIFF、ICC、Histogram 与 TIFF 编码问题；NuGet 索引范围尚未同步，不能只为消告警跨到 v4。本轮真实试升后，Release 被新增许可检查拒绝。用户没有许可；已撤回该候选引用、恢复实际可构建状态，没有跳过检查或把未生效升级写成已修复。合规的最小后续是申请 `osu.Game` 的免费程序集限定社区密钥；官方允许这种限定密钥进入开源仓库。当前上游也仍固定旧库，没有找到公开可复用密钥。若不采用该许可，需要独立设计图片解码替代，不以表面改引用形状规避许可。[v3 修复](https://github.com/SixLabors/ImageSharp/releases/tag/v3.2.0)、[官方支持与许可政策](https://sixlabors.com/posts/security-support-and-license-enforcement/)、[申请入口](https://licensing.sixlabors.com/)
2. **BGA 原生媒体**：当前 NativeLibs 2025.806.0 中 Windows `avutil-56` 表明 FFmpeg 4.3.3，处于进程内真实 BGA 解码链。官方 4.3 分支后续已有修复；该构建只启用部分容器 / 解码器，尚未逐项证明每个 CVE 可达。需要核对补丁和 ABI，选择匹配的整套原生库或正式迁移；不能只覆盖不同主 ABI DLL，外部 `ffmpeg.exe` 的更新也不能替代它。最新 framework 只支持 net10，仍用同一旧 NativeLibs，不构成本轮安全捷径。[官方 FFmpeg 安全页](https://ffmpeg.org/security.html)
3. **宝塔运行环境**：实际面板仍使用 Python 3.7.16。此次只闭合证书信任缺口，没有把它记为受支持的新 Python；需要走供应商支持的面板 / Python 更新或收缩管理面的独立维护窗口。SSH 口令策略与管理入口未改，避免在不知道维护者备用入口的情况下锁定登录。
4. **开发与静态构建链**：上午观察到的本机 Node 24.13.0 已过时，傍晚实测为已修复的 24.22.1，并非本轮代更新。uv 0.11.2 与停用 WSL PHP 8.5.11 / Node 24.18.1 的原待办保留；本轮使用独立 F 盘已验 SHA 的 uv 0.13.4 处理锁文件，没有启动 WSL。Homepage 的 Astro / sharp / Vite 等锁图、旧设计 braces 亦保留待办；升级须验证生成内容与构建，不能因它们不是生产动态服务就永久忽略。参考快照保持原历史身份，启用前另行核对依赖，不做批量 `audit fix --force`。

AutoMapper 13.0.1 的当前固定映射图已有深度约束；SQLitePCLRaw 2.1.10 的旧在线缓存没有攻击者可提交的任意 SQL 入口。SharpCompress 0.39.0 未调用目录穿越公告涉及的 `WriteToDirectory`，但这个判断只适用于该条公告，不能覆盖傍晚确认可达的 LZMA2 死循环。未以跨付费 / 主版本迁移冒充修复；.NET 8.0.32 符合本轮已查微软 10 月安全修复版本。

## 傍晚公告增量复核

2026-10-22 18:56～19:18 CST 再核七仓锁文件、官方公告、开发工具和实际服务器。记录公告首次发布日期、最近修改日期与本次发现日期，未将同一证书事件的多平台通知或旧漏洞的新发行版补丁算成多起新攻击。此轮是适用性复核，没有执行利用载荷或开展主机入侵取证。

### 新增待处理结论

- **SharpCompress：优先接续的客户端风险。** [GHSA-5wf8-cxh5-32fv](https://github.com/adamhathcock/sharpcompress/security/advisories/GHSA-5wf8-cxh5-32fv) 10 月 19 日已公开，维护者现列修复版 0.50.6；10 月 20 日的 0.50.7 可作为升级目标。当前 0.39.0 的旧解码代码同样存在 EOF 处理问题，`BmsDownloadImporter.ExtractArchive` 接受 7z，`OpenEntryStream` → 同步 `Read` 可进入 LZMA2；特制坏包可令线程持续空转，检查在 `Read` 外的字节预算和取消无法中断它。上午修复的预算问题仍有效，但没有闭合这项底层 DoS。此项是此前漏检，未在本机运行恶意样例。新版同时改动 ArchiveFactory / ZipArchive / WriterFactory 入口及 LzmaStream 创建方式，还须核 framework 预编译依赖；本轮未改引用、禁用 7z 或假称升级完成。迁移需覆盖原谱包导入、ZIP 与回放压缩读写及明确的坏包终止行为。
- **独立运行时不能由宿主机版本代签。** 当前 HTTP 应用和固定备份 helper 的 Python 3.12.14 均自带 OpenSSL 3.5.8，仍落在 9 月 29 日 [CVE-2026-35189](https://openssl-library.org/news/vulnerabilities/#CVE-2026-35189) 的版本范围内；维护者评级 Low，恶意对端证书可造成额外内存占用，3.5.9 修复。TLS 路径存在，特定恶意证书未复现；需以完整受支持 Python 运行时升级验证，不能只修系统 libssl 或替换单个库。此项亦非最近两天才公开。
- **PHP 独立环境的 libcurl。** 实测 PHP 8.5.12 / c-ares 1.34.9 / OpenSSL 3.5.9，但 libcurl 为 8.22.0-r0。上游 [CVE-2026-92392](https://curl.se/docs/CVE-2026-92392.html) 于 10 月 14 日公开，涉及 HTTP/2 上传的 use-after-free，8.23.0 修复。19:15 直接核 Alpine v3.24 main / community 官方 APKINDEX，libcurl 候选仍为 8.22.0-r0，安全数据库没有该补丁条目；未取得此构建含回移修复的证据。现行 OmsApi 只请求配置的 Backend、禁止重定向，未确认有访问恶意远端 HTTP/2 上传的入口，不能据库版本宣称公网请求已经可利用。保留独立 PHP 完整运行时升级 / 回移待办，不混入 edge 仓库或把宿主机 curl 8.5.0 的回补版本当作这个副本已修复。
- **MessagePack 的条件性告警。** 当前 3.1.9 仍在 [GHSA-7rj2-5w9w-r9jx](https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-7rj2-5w9w-r9jx) 的版本范围内，3.1.11 修复；该公告 10 月 3 日公开，触发依赖 Lz4Block / Lz4BlockArray 与不可信反序列化。实际代码只用 Standard.WithResolver，没有启用压缩，旧在线入口保持关闭，未确认当前可达。不将上午 3.1.9 的单项修复概括成消除了全部 MessagePack 公告，后续维护升级一并验证。

### 本次服务器补丁与验证

刷新 Ubuntu 签名源后确认宿主机还有两项公告对应更新，已按既有运维授权于 19:14:59 CST 完成：

| 对象 | 安装前 → 安装后 | 适用范围 |
| --- | --- | --- |
| libnss3 | `2:3.98-1ubuntu0.2` → `2:3.98-1ubuntu0.3` | [USN-8947-1](https://ubuntu.com/security/notices/USN-8947-1)，10 月 21 日通知移除受证书事件影响的信任根；与上午 certifi / 系统 CA 束是不同信任存储。 |
| libcares2、libc-ares-dev | `1.27.0-1.0ubuntu1` → `1.27.0-1.0ubuntu1.1` | [USN-8951-1](https://ubuntu.com/security/notices/USN-8951-1)，24.04 的 DNS CPU / 内存资源消耗补丁；公告另列的旧 16.04 任意代码执行不适用于当前版本。 |

变更前后均核两处 loopback health 和两个公开站点，全部 200。安装仅升级上述三包，无新增 / 删除；dpkg --audit 无输出。加载旧 NSS 的 udisks2 已重启，五个业务 / Web / 面板服务保持 active，主 IR / catalog / FPM / Nginx PID 与启动时间未变，无 reboot-required。未升级 Docker、发布站点、切应用目录或更改数据库；当前仍为 `824de121a686-494932756b74`。PHP 独立 c-ares 1.34.9 与 Node 自带 1.34.9 已高于上游这两项 DNS 问题的修复版 1.34.7，不能因宿主机更新而重复替换它们。

先保存三包原有文件 / 链接与 dpkg 元信息共 178 项，再从受签名源下载精确新包；原件及三份新 deb 已取回受限 F 盘，逐件核字节和 SHA，原件 gzip CRC / tar 成员检查通过。服务器原件位于 `/var/backups/oms-maintenance/security-delta-20261022T111349Z`，已在原完整恢复材料计划覆盖的父目录内；本次没有重跑云备份，因此上午 11:54 的云恢复验证不包含傍晚新增文件。F 盘副本与云端覆盖分别记账，没有为库补丁重新执行数据库恢复。

### 其余核对与覆盖边界

- 重新查询 OSV 的 Web npm 318、Homepage npm 391、旧设计 npm 177、Backend PyPI 26、Composer 74 个精确版本对。相对上午没有新命中 ID；既有静态构建链 / Less 插件条件性告警未因此关闭。GitHub 最新 reviewed、unreviewed、malware 各 100 条同时比对锁图；未出现新的精确适用项或包名恶意软件命中，但这不是全历史供应链审计。CISA 公告入口返回 403，未算检查通过。
- NuGet 最新增量索引时间为 13:33 CST，与上午保存的 218 个客户端依赖名无交集；索引未收录上述 SharpCompress / MessagePack 维护者公告，实际以官方公告与调用链为准，不能凭扫描零命中放行。
- 生产 PHP 8.5.12、Node 22.23.4、Nginx 1.30.6 保持当前已查修复系列。Node 自带 OpenSSL 3.5.9，与 Python 自带 3.5.8 分开判定。本机 Node 实测 24.22.1 / OpenSSL 3.5.9 / Undici 7.30.1；原 24.13.0 待升级项更正，不声称本轮安装。
- 本机 Windows 26H2 `26300.9711` 对应微软 [10 月 13 日安全累计更新](https://support.microsoft.com/en-us/servicing/os/windows-11/2026/10/kb5127648-windows-11-24h2-25h2-26h2-security-update)，符合本轮查到的正式通道版本。Git 2.56.0.windows.2、VS Code 1.142.0 已高于本次找到的相关修复；未据普通功能新版提示进行系统更新。
- Chrome 安装版本 156.0.8078.48 对应 [10 月 20 日稳定版](https://chromereleases.googleblog.com/2026/10/stable-channel-update-for-desktop_02018666648.html)，不据此保证运行中的旧进程或 CA 组件已经更新。Edge 155.0.4283.62 与最近正式版一致，但 [10 月 20 日厂商说明](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-relnotes-security)仍表示相应 Chromium 修复准备中，保留厂商补丁缺口。未找到标准安装位置的 Firefox；未从 PATH、卸载登记、App Paths / 关联或标准位置确认 7-Zip，故不把 [10 月 21 日 26.05 安全版本](https://github.com/ip7z/7zip/releases/tag/26.05) 写成已安装或无须更新，也未遍历用户便携程序目录。
- ImageSharp 项目许可、进程内 FFmpeg、BT Python 和已记录构建链问题保持未解决。此轮未改客户端代码、导入正式玩家内容或启动新测试宿主；上午 Release / 聚焦回归数字不算本次重跑。

新原始响应、七仓开工差异、精确包版本、APKINDEX 和服务器收据在忽略的 `artifacts/architecture-security-20261022/evening-delta/`。仅提交本轮受影响文档，既有七仓无关未提交工作保持原样。

## 验证与运行边界

最终重新编译后，客户端 Release 外链 / 皮肤读图等回归 71 项通过，本地 BMS / 下载 / 导入专项 138 项通过，Desktop Release 编译通过；未应用 ImageSharp 3.2.0，故这些结果不能代签新版图片库。扩大 BMS 回归因空闲内存下降主动中断，既有单个皮肤产品 fixture 的数百绘制组合仍可占较高内存；不将部分 TRX 或已完成的 10 组 2077 通过 / 4 跳过冒充完整回归。当前导入改动按存储验收矩阵的 importer focused + Release 完成，细节取 [P1-A 本轮日志](../../../oms/doc_md/subline/P1-A/CHANGELOG.md#2026-10-22全工作区安全筛查与本地导入边界)。

Backend 认证、目录、外源、网盘与布局聚焦检查 113 通过 / 6 跳过；跳过的是未在该命令启用的真实 age 案例，不写成全部通过。Web 发布器 7 项检查通过。两个实际发布 guard 的代码在生产 Python / SQLite 上分别接受当前证书包，拒绝旧版 / 无效版本，共 2 正例 / 6 反例；安装器 Python 语法和准备脚本 Bash 语法亦通过，没有为了测试而安装或激活新 release。源码、测试与实际线上验证分别留存，未重新运行完整容量、真人或新 Linux 灾难恢复门。

服务器变更前已从固定 helper 取得新鲜快照，原配置 / 证书包 / uv 和旧 Node 安装包取回受 ACL 保护的 F 盘，核 SHA / 字节、gzip CRC、原库指纹、integrity、外键、schema3 / 22 表。第一次执行因日期版本的前导零表达不同在写包前停止；第二次安装继承私有 0077 umask，导致新包只有 root 可读，两个业务服务短暂启动失败。已修正两处公共包目录 / 文件权限，以 `oms-ir` 实际导入 / 读取后重启成功；失败日志保留。当前应用目录、业务库 device / inode、schema / 表数保持，双 health 和双站 200，三个备份 timer 恢复。

恢复范围已将 `security-maintenance` 从 PHP 单次目录扩至 `/var/backups/oms-maintenance`，保全两轮原件、已核验 wheel、旧 / 新 Node 包及运行时身份；工具根包含新 uv。补丁后完整云备份于 11:54 CST 成功完成；从真实云端下载 10 个密文（含当前目录）共 290,608,522 字节，age 末块认证、gzip CRC、逐文件 SHA 全部通过，另对 30 个未变的既有云端恢复对象重新逐文件哈希。当前 39 对象共 69,150 文件 / 2,933,260,011 原始字节，1,572 项原 Linux 链接仅保留清单，没有在 Windows 实体化。已核两处 certifi / CA、uv 字节、旧 / 新 Node 包和扩展 plan，并离线恢复云端业务快照，integrity / 外键 / schema3 / 22 表通过；没有执行生产库恢复或新 Linux 整机启动。

最终公开六页、CSS 与 release 字节、状态页拒绝共 8 项检查通过。原始收据放忽略的 `artifacts/architecture-security-20261022/`，客户端证据在 `oms/artifacts/security-architecture-20261022/`；秘密与数据库只在受保护目录，不进 Git。

原等待完整备份的 SSH 长连接未返回，已在独立核验后关闭，原包装命令因此退出 1；该结果仅表示等待连接中断。备份成功依据为新连接读取的 systemd `Result=success / ExecMainStatus=0`、当前目录身份与上述真实云端恢复检查，不以旧连接的退出码替代服务实际结果。

最终客户端定点 formatter、211 篇客户端文档和跨工作区 189 篇协作文档校验通过。受影响五仓按本轮增量提交；已有未提交的其它文档 / 页面工作及两桥原有未推提交保持各自状态，不纳入此次安全修复，也不将推送视为应用部署。
