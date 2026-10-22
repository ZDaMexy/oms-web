# 2026-10-22 全工作区架构安全筛查

本轮范围为总工作区的七个正式 Git 项目、旧设计 / 上游参考副本的用途边界，以及这些项目使用的开发、部署、共享服务器和备份链。`private-data/`、HDD、玩家数据、私有素材与恢复私钥不进入源码扫描；服务器一致快照仅走已授权的受限备份流程，不读取个人行。此前 PHP / Nginx / 内核维护取[原记录](php-security-maintenance-20261022.md)，不重复算成本轮应用发布。

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
4. **开发与静态构建链**：本机全局 Node 24.13.0 / uv 0.11.2，以及停用的 WSL PHP 8.5.11 / Node 24.18.1 仍需更新；本轮使用独立 F 盘已验 SHA 的 uv 0.13.4 处理锁文件，没有更改系统盘工具或启动 WSL。Homepage 的 Astro / sharp / Vite 等锁图、旧设计 braces 亦保留待办；升级须验证生成内容与构建，不能因它们不是生产动态服务就永久忽略。参考快照保持原历史身份，启用前另行核对依赖，不做批量 `audit fix --force`。

AutoMapper 13.0.1 的当前固定映射图已有深度约束，SharpCompress 0.39.0 没有调用该公告涉及的 `WriteToDirectory`，SQLitePCLRaw 2.1.10 的旧在线缓存没有攻击者可提交的任意 SQL 入口。这些保留版本告警及复核理由，没有跨付费 / 主版本迁移后声称修复实际不存在的服务；本地归档预算缺口与 SharpCompress 的目录 API 公告是两回事。.NET 8.0.32 符合本轮已查微软 10 月安全修复版本。

## 验证与运行边界

最终重新编译后，客户端 Release 外链 / 皮肤读图等回归 71 项通过，本地 BMS / 下载 / 导入专项 138 项通过，Desktop Release 编译通过；未应用 ImageSharp 3.2.0，故这些结果不能代签新版图片库。扩大 BMS 回归因空闲内存下降主动中断，既有单个皮肤产品 fixture 的数百绘制组合仍可占较高内存；不将部分 TRX 或已完成的 10 组 2077 通过 / 4 跳过冒充完整回归。当前导入改动按存储验收矩阵的 importer focused + Release 完成，细节取 [P1-A 本轮日志](../../../oms/doc_md/subline/P1-A/CHANGELOG.md#2026-10-22全工作区安全筛查与本地导入边界)。

Backend 认证、目录、外源、网盘与布局聚焦检查 113 通过 / 6 跳过；跳过的是未在该命令启用的真实 age 案例，不写成全部通过。Web 发布器 7 项检查通过。两个实际发布 guard 的代码在生产 Python / SQLite 上分别接受当前证书包，拒绝旧版 / 无效版本，共 2 正例 / 6 反例；安装器 Python 语法和准备脚本 Bash 语法亦通过，没有为了测试而安装或激活新 release。源码、测试与实际线上验证分别留存，未重新运行完整容量、真人或新 Linux 灾难恢复门。

服务器变更前已从固定 helper 取得新鲜快照，原配置 / 证书包 / uv 和旧 Node 安装包取回受 ACL 保护的 F 盘，核 SHA / 字节、gzip CRC、原库指纹、integrity、外键、schema3 / 22 表。第一次执行因日期版本的前导零表达不同在写包前停止；第二次安装继承私有 0077 umask，导致新包只有 root 可读，两个业务服务短暂启动失败。已修正两处公共包目录 / 文件权限，以 `oms-ir` 实际导入 / 读取后重启成功；失败日志保留。当前应用目录、业务库 device / inode、schema / 表数保持，双 health 和双站 200，三个备份 timer 恢复。

恢复范围已将 `security-maintenance` 从 PHP 单次目录扩至 `/var/backups/oms-maintenance`，保全两轮原件、已核验 wheel、旧 / 新 Node 包及运行时身份；工具根包含新 uv。补丁后完整云备份于 11:54 CST 成功完成；从真实云端下载 10 个密文（含当前目录）共 290,608,522 字节，age 末块认证、gzip CRC、逐文件 SHA 全部通过，另对 30 个未变的既有云端恢复对象重新逐文件哈希。当前 39 对象共 69,150 文件 / 2,933,260,011 原始字节，1,572 项原 Linux 链接仅保留清单，没有在 Windows 实体化。已核两处 certifi / CA、uv 字节、旧 / 新 Node 包和扩展 plan，并离线恢复云端业务快照，integrity / 外键 / schema3 / 22 表通过；没有执行生产库恢复或新 Linux 整机启动。

最终公开六页、CSS 与 release 字节、状态页拒绝共 8 项检查通过。原始收据放忽略的 `artifacts/architecture-security-20261022/`，客户端证据在 `oms/artifacts/security-architecture-20261022/`；秘密与数据库只在受保护目录，不进 Git。

原等待完整备份的 SSH 长连接未返回，已在独立核验后关闭，原包装命令因此退出 1；该结果仅表示等待连接中断。备份成功依据为新连接读取的 systemd `Result=success / ExecMainStatus=0`、当前目录身份与上述真实云端恢复检查，不以旧连接的退出码替代服务实际结果。

最终客户端定点 formatter、211 篇客户端文档和跨工作区 189 篇协作文档校验通过。受影响五仓按本轮增量提交；已有未提交的其它文档 / 页面工作及两桥原有未推提交保持各自状态，不纳入此次安全修复，也不将推送视为应用部署。
