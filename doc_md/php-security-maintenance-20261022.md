# 2026-10-22 PHP 与共享服务器安全维护

用户授权在既有 SSH 别名 `zdamexy-srv` 上实施修复及必要维护。本轮更新生产运行环境、启动配置与恢复材料；HTTP 应用仍为 `824de121a686-494932756b74`，没有发布新网页功能、改数据库结构或生成 Windows 客户端发行包。OMS 产品仍为已部署待真人验收。

## 已实施

| 对象 | 变更及实际结果 |
| --- | --- |
| OMS PHP | CLI、FPM 及所有 `php85*` 扩展统一由 8.5.11 升至官方签名 Alpine 包 8.5.12-r0；实际运行根为 `/opt/oms-web/runtime/php85-922304e595f8`。只修改 Web / cache 的 RootDirectory，保留原应用、私有缓存、URL、环境与资源限额。 |
| 旧 BT PHP | 8.2.28 仅供 phpMyAdmin 和状态页，OMS、Homepage、BT Python 面板不依赖它。进程正常退出，socket 消失，`php-fpm-82.service` 已 disable / mask；安装文件保留。使用 phpMyAdmin 前须先安装受修复版本，禁止直接重启旧 PHP。 |
| 状态页 | 原 localhost 虚拟主机仅有 allow、缺少 deny。补上 IPv4 / IPv6 loopback allow 和 `deny all`，外网携带 `Host: 127.0.0.1` 的良性 GET 已从 200 变为 403。 |
| Nginx | 从 1.28.3 升至官方签名源码 1.30.6，保留 BT 原模块和配置；移除静态 OpenSSL 1.1.1w，使用 Ubuntu 安全维护的 `libssl3t64 3.0.13-0ubuntu3.16`。原 BT Lua 模块仍使用发行版 libpcre3，未强行改成不兼容的 PCRE2。 |
| Nginx 服务 | 原系统单元指向 `/usr/sbin/nginx` 且处于 failed，实际 BT master 不受该单元管理。现 `/etc/systemd/system/nginx.service` 指向 BT binary / config / PID，实际进程位于其 cgroup，开机自动恢复已验证。模板见 [nginx-bt.service](../deploy/nginx-bt.service)。 |
| 缓存顺序 | 正式 FPM 增加对 `oms-web-cache.service` 的 Requires / After；实际重启及整机重启均通过。现存发布使用 [drop-in](../deploy/oms-web-cache-order.conf)，新发布由 [生成器](../scripts/production-config.py)直接生成依赖。隔离 staging 不依赖正式 cache 单元。 |
| Ubuntu 安全包 | 安装 ca-certificates、distro-info-data、liblzma5、liblzma-dev、xz-utils、libunbound8、python3-jwt 共 7 项安全更新；没有执行全量 dist-upgrade、autoremove 或升级 Docker / Node 主版本。 |
| 内核与重启 | 安装 `linux-image-virtual` 及 6.8.0-147 内核 / 模块，保留原 6.8.0-106 内核。约 04:48 CST 执行受控重启，实际运行 6.8.0-147-generic，重启需求标记消失。既有 cloud-init / intel-microcode hold 保持。 |
| APT | Docker 镜像的 bz2 索引与已签名 Release 不一致，未绕过校验；改用同源已校验 gzip 索引，并将既有 Docker 公钥绑定到该仓库的 Signed-By。原镜像保持，普通 apt-get update 已成功。 |

PHP 依据为官方 [2026-10-21 发布记录](https://www.php.net/archive/2026.php#2026-10-21-5)及 [CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w)、[CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp)。状态页访问规则取 [Nginx access module](https://nginx.org/en/docs/http/ngx_http_access_module.html)；Nginx 版本选择取[官方安全公告](https://nginx.org/en/security_advisories.html)和[下载页](https://nginx.org/en/download.html)。本次确认存在需修复的版本与暴露面，没有据此宣称服务器曾被成功入侵，也未发送利用载荷。

## 发布与回退约束

- 新 PHP 包 `php85-8.5.12-alpine3242.tar.gz` 为 26,433,379 B，SHA-256 为 `922304e595f840bb322acfcc3d387cd4513dad86985159d2951a4d6e6fb8bb35`；已保全到受限 F 盘并校验。旧包另行保留，不覆盖原应用的历史 release.json。
- [运行时检查](../scripts/php_runtime.py)从归档或安装目录的 APK 数据读取真实版本，要求 CLI / FPM / 扩展齐备且版本一致，并拒绝低于 8.5.12。构建 manifest、安装器及配置生成器均使用该检查，不能只把旧包的版本标签改成新版本。安装器验证发生在创建发布目录之前；复制这些脚本到服务器执行时，须同时复制同目录的 php_runtime.py。
- 原应用 release.json 中 8.5.11 属于历史构建元信息；当前实际 PHP 身份取合并后的 systemd RootDirectory、进程 executable 和独立 `runtime-security.json`。本轮未篡改不可变应用包以伪造一次应用发布。
- 应用回退须保留受修复 PHP 和本轮 Nginx / 状态页修复，不能盲盖 10 月 11 日旧单元重新启用 8.5.11。先保全当时配置、新鲜数据库备份及 timer 状态，再按当前应用需要生成缓存 / 路由。旧设计和数据库恢复边界仍取[现行维护](production-maintenance.md)。
- 此轮没有启动或升级本地 WSL；原本地 PHP 8.5.11 记录保留原验证日期，再次启用前须更新并重新验证。本轮生产启动证据不能代签更新后的本地恢复。

## 验证与恢复材料

重启前 04:44:44 CST 的固定 helper 备份已取回受 ACL 保护的 F 盘，gzip / 原始 SQLite 的字节数与 SHA-256、gzip CRC、integrity、外键、schema3 和 22 张表全部通过。完整配置原件、旧 Nginx binary、新 PHP 包与新 Nginx binary 亦已外取；没有向线上恢复 raw 数据或读取个人行。

重启后实际核对新 boot ID、新内核、Nginx / FPM executable、五个业务 / cache 单元、双 health，以及 Homepage、OMS 首页、IR、新闻、帮助和 client-content。实际业务库 device / inode、schema3、22 表及 HTTP release 保持；服务 NRestarts 为 0，失败单元为 0。BT Python 面板进程正常，三个备份 timer 恢复原 enabled / active 状态，错过的数据库云备份已补跑并验证。

[7 项专项检查](../scripts/test_php_runtime.py)通过，覆盖受修复包、旧包拒绝、仅 common 升级的混装拒绝、缺失 FPM、元信息伪标、现存旧目录和安装前拒绝；实际新版归档检查及服务器配置生成亦通过。首次 PHP 切换因 Type=simple 的短暂 systemd-executor 身份触发保护性回退；按真实启动时序等待后重新切入成功。Nginx 两次隔离准备分别发现 LuaJIT include 路径和 PCRE API 不匹配，修正构建参数后才替换线上 binary，没有替换第三方模块源码。

备份 plan 已将当前 PHP 从旧固定根改为新根，补入 Nginx 依赖的 jemalloc / LuaJIT 文件及链接、APT 配置、本轮维护原件和 Nginx 签名源码 / 模块 / 构建参数；仍排除虚拟 app / dev / proc / run / tmp 与缓存。旧云端恢复点保留，凭据和恢复私钥不变。

新分类与上传前预检来自 Backend `24d38cf8318ff4f9d28e5c844b63290dd8e680fb`，维护工具为 `/opt/oms-netdisk-backup/releases/da6084e4c2262c98`，17 个绑定文件加清单共 18 项；包 SHA-256 `fc9298cc44b6434752f40a8d3a9511d812ab5988e71712f2fe228caa262c69f6`，4,097,130 B。现有四个 backup unit、凭据 / 公钥 / 数据库云备份收据指纹及四个 HTTP 进程均保持；旧工具保留。54 项聚焦检查全部通过，启用真实 age 加密 / 解密，没有跳过恢复测试。既有 Starlette 弃用提示保留。

首轮扩围在新增对象缺少目录分类时明确失败，旧成功目录未被覆盖；补齐分类并增加上传前预检。新工具首次安装又因 root 的 0077 umask 使公共程序目录不可由 oms-ir 穿越而失败；仅将该不可变工具的目录修正为 0755，程序 / 数据文件仍按原 0555 / 0444，私有状态权限保持，并实际以 oms-ir 执行入口检查。05:10:35 CST 重跑完成 39 个数据对象及新总目录，目录密文 SHA-256 `54244fbc8e4810b8c9a50bd8d6eccf392192ede06992bfa8af7df811ca7a6f6d`。成功那轮新传数据对象 28,079,650 B、目录 9,813 B；此前失败轮已完成的对象另外保留，该值不代表本轮累计出网。

随后从真实网盘向受保护、大小写敏感的 F 盘取回总目录及 16 个变化对象，共下载密文 56,021,023 B，逐个验证密文 SHA、age EOF、gzip 和普通文件 SHA；其余 23 个对象核对密文指纹并复用先前已验证的准确 F 副本，没有把旧对象重新记成当次全部下载 / 解密。当前目录引用 39 个对象、69,120 个普通文件，原始 2,763,740,205 B，另有 1,572 个待 Linux 恢复的链接记录。该目录密文引用总量不代表网盘所有历史版本总占用。

取回后再次核对 PHP 安装元信息确为 8.5.12、Nginx binary 与运行版 1.30.6 字节一致、备份 plan 指向新 PHP 且六类新增材料齐备；从真实云端业务快照在新 F 文件恢复 SQLite，字节 / SHA、integrity、外键、schema3 和 22 表均通过。另从本机公网完成 6 个页面 / 内容请求、CSS 与不可变发布原件逐字节核对，以及伪造 localhost Host 的状态页 403，共 8 项有限 HTTP / TLS 检查。

本次对现有主机完成了真实重启验证；这不等于在一台新 Linux 主机完成整机灾难恢复。原 AGPL 应用源码下载、线上真人验收、实际自动续证及容量门保持原范围。

原始收据和脚本位于忽略的 `artifacts/php-maintenance-20261022/`，配置 / 数据库仅在其受保护 `private/`。其中 preboot 的 systemd 静态检查误按宿主 `/usr/sbin/php-fpm85` 路径报缺失，已保留诊断并核对真实 RootDirectory 与进程 namespace；首次 postboot 探针请求不存在的 `/sources`，其 404 不属于服务故障，后按实际路由复验通过。原失败证据未覆盖或删去。
