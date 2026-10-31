# 2026-11-01 共享服务器运行时与安全维护

> **后续收据接续**：下文 04:57 段保留当时的验证范围。05:07 SSH / UFW 加固、05:15 受限 Linux QA、05:19 真实模型探针及 05:21 BT 两包补修已分别取得收据，见[后续加固与验证](#host-hardening)；新 Bot 正式切换、独立状态备份、新全备恢复和维护重启仍待后续收据。

本记录是本轮 OMS / BT 运行时、共享主机清理与恢复边界的权威落点。截至 2026-11-01 04:57 CST，OMS HTTP、catalog 和固定备份 helper 已切至 Python 3.12.16，BT 面板已切至 Python 3.13.18；应用来源、同一业务库及依赖包名 / 版本保持。后续 SSH / UFW 加固、Shiro 新运行面与维护重启尚待各自实际收据，不能由这里的有限检查提前签收。

Homepage、OMS 与 Shiro 仍是独立产品，只共享主机、Nginx、TLS 和 SSH。两站设施镜像见 [Homepage](../../homepage-website/doc_md/other/shared-agent-security-20261101.md) 与 [旧 OMS Website](../../oms-website/doc_md/other/shared-agent-security-20261101.md)。Bot 的当前发布、恢复和真人收发边界只取 [Shiro 部署记录](../../../shiro-bot/doc_md/mainline/qq-official-deployment.md)，不在本页复制业务合同。

## 当前运行时与应用来源

| 对象 | 04:57 CST 已验证身份 |
| --- | --- |
| OMS HTTP / catalog / 固定 helper | Python 3.12.16，共用不可变 base `/opt/python-runtimes/cpython-3.12.16-linux-x86_64-gnu`，各产品保留独立 venv |
| BT 面板 | Python 3.13.18，base `/opt/python-runtimes/cpython-3.13.18-linux-x86_64-gnu`；`/www/server/panel/pyenv` → `/opt/bt-panel-runtime/py31318-20261101` |
| 两个新 base 的标准库依赖 | OpenSSL 3.5.9、SQLite 3.53.1、Expat 2.9.0；BT 的 cryptography 另带 OpenSSL 4.0.3，不能混记为标准库版本 |
| HTTP / 网页应用 | `/opt/oms-ir/current` → `/opt/oms-ir/releases/824de121a686-494932756b74`，本轮没有应用发布 |
| 固定维护包 | `/opt/oms-ir/releases/d1f052b93a81-22b4ee54f237/backend/.venv`，没有改指向 HTTP current |
| 实际业务库 | `/var/lib/oms-ir/ir.db`，device 64771 / inode 265517，schema3 / 22 表；切换前后身份保持 |
| 依赖集合 | OMS HTTP 21、固定 helper 21、BT 85 个已安装包，切换前后包名 / 版本完全相同 |

准备阶段先验证下载 SHA、候选 base 和 venv，再切换解释器路径；没有重新求解应用依赖或修改 lock / 历史 manifest。新 base 的安全发布背景取 [Python 3.12.16](https://www.python.org/downloads/release/python-31216/) 与 [Python 3.13.18](https://www.python.org/downloads/release/python-31318/)，不能把公共 base 的版本变化当成业务源码发布。

本地开发 Python 与生产分别登记：本轮没有重建 Backend 本地 `.venv`，其 2026-10-23 Python 3.12.15 / 423 项回归仍属原证据。部署脚本的后续源码 guard 修订亦不等于已经发布新的 HTTP 应用。

## BT init 模板覆盖根因与修复

首轮切换后，指纹检查发现 `/etc/init.d/bt` 被面板自己的模板刷新。`/www/server/panel/class/jobs.py` 的 475～485 行比较 init 与 `/www/server/panel/init.sh` 的 MD5，不同就复制模板。原模板含 `replace_env()`：若发现旧 `/www/server/panel/pyenv313/bin/python3` 为 3.13.14，会移动 active pyenv 并替换。观察时 `pyenv313` 不存在，未发生实际 Python 降级；但只修运行中的 init 会被模板再次覆盖。

因此将 `/etc/init.d/bt` 恢复为切换前已加固的 init，并把模板同步为同一字节；没有修改 `jobs.py` 或 BT 业务 Python 源码。两个文件 `bash -n` 均通过，MD5 / 字节一致且不再含 `replace_env`，随后执行 `systemctl daemon-reload`。具体收据为本轮证据目录中的 `panel-init-guard.json`。

| 指纹 / 权限 | SHA-256 / 结果 |
| --- | --- |
| 不安全模板及其覆盖后的 init | `e0bb54c84c5c1cf7f1f483cc79f204b758f3a21b8cb49a8e7c4abf3b65e7d919` |
| 最终 init 与模板共同指纹 | `2f0afafe3fe6dba4ea5ca04ff4009e3e6f4475544600302704a5ba9fe1b60a0b` |
| 最终 owner / mode | init 为 root:root 0755，模板为 root:root 0600 |

第一轮进程检查曾错误要求 BT-Task 使用 Python；它实际是原生 ELF `/www/server/panel/bt-task.run`，并未映射 libpython。修正检查后保留其原 executable，BT Panel 则通过 `/proc/<pid>/exe` 证明使用新 3.13.18。初次失败和向前修复收据均保留，没有回切漏洞解释器或删除失败记录。后续 BT 厂商更新仍可能改写模板，升级时必须重新检查两处及真实进程，不能把本次修正当成永久保证。

## 切换、备份与有界验证

切换前保全 venv cfg / Python symlink、unit / init、full plan 指纹与 timer 状态，暂停三项 timer，确认对应备份 worker 的 MainPID / ControlPID 均为 0，再调用固定 helper 取得新一致快照。没有读取个人原始行、直接复制在线 SQLite 或回灌生产 raw。

| 阶段 | 固定 helper InvocationID | 完整备份对 |
| --- | --- | --- |
| 切换前 | `24f902e3af5d42e99522fc706999c123` | `daily-20261031T204340Z.db.gz` 及同名 `.json` |
| 新运行时切换后 | `2e13508bee3a43ed9bf1706ee43b9a0f` | `daily-20261031T205333Z.db.gz` 及同名 `.json` |

两份 gzip 均为 9,095 B，SHA-256 为 `70e2905613e390b80836c92b31ba1ed1a79bee0c3d6ec319455b2b6981127be1`；完整解压均为 241,664 B，raw SHA-256 为 `e8f67303bd9aff004a2294f59f08757ce1fa519e77af54e72c65fec31328e48c`。F 盘验证完整 EOF / CRC、sidecar 双摘要绑定、SQLite integrity、FK 0、schema3 / 22 表；这些小型业务库快照不代表全量公开历史投影已重新备份。

候选验证覆盖 OMS FastAPI / httpx / Argon2 / Pydantic / certifi 导入与 Argon2 往返；BT 覆盖 PyJWT HS256、Brotli 往返、Pillow PNG、BSON、gevent 及 requests / psutil / Flask / Paramiko / Redis / Docker / YAML 导入。实际切换后在 45 秒有界窗口内核验双 health 与双站 HTTPS 根页，均返回 200；BT 指定 Nginx `-t` 通过，BT 根页保留原 404 基线。没有把面板根页读取记成真人登录验收。

04:57 终态 OMS HTTP / catalog / OMS Web / Nginx / BT / 旧 Shiro 服务均 active，NRestarts 为 0；OMS Web、Nginx 与当时 Shiro PID 保持，只有目标 OMS / BT 进程按计划重启。BT 生成 unit 的 MainPID 为 0，面板身份另以实际 PID / executable 核实。该快照不签收后续 Bot 部署或重启后的 PID。

已执行的核对入口如下，准确输出、失败和时间均在收据，不以重跑旧命令覆盖当次证据：

```bash
readlink -f /opt/oms-ir/current
readlink -f /www/server/panel/pyenv
systemctl show oms-ir.service oms-ir-catalog.service oms-web.service nginx.service bt.service -p Id -p ActiveState -p SubState -p MainPID -p NRestarts
systemctl show oms-ir-backup.service oms-netdisk-backup.service oms-full-backup.service -p Id -p MainPID -p ControlPID -p Result
curl --fail --max-time 5 http://127.0.0.1:8081/health
curl --fail --max-time 5 http://127.0.0.1:8082/health
curl --fail --max-time 5 https://zdamexy.work/
curl --fail --max-time 5 https://oms.zdamexy.work/
/www/server/nginx/sbin/nginx -t
bash -n /etc/init.d/bt
bash -n /www/server/panel/init.sh
df -B1 /
```

### 三项 timer 恢复

04:57 CST 三项均恢复为原先的 **enabled / active / waiting**，对应备份 worker 均 inactive / dead 且 MainPID=0、ControlPID=0。

| timer | 当时读取的下次触发 |
| --- | --- |
| `oms-ir-backup.timer` | 2026-11-02 04:16:57 CST |
| `oms-netdisk-backup.timer` | 2026-11-02 04:49:49 CST |
| `oms-full-backup.timer` | 2026-11-01 05:32:09 CST |

网盘 timer 恢复后按原 Persistent 语义自然触发过一次；本轮没有手动另开云端上传或解密恢复。timer 等待、任务触发和云端成功是三个状态，不能互相替代。表内是历史读取的具体时间，后续维护仍须读取当时真实状态。

## 恢复计划、证据与保留范围

`/etc/oms-full-backup/plan.json` 仅修改必要解释器对象 / 来源说明：`python` root 改为 `/opt/python-runtimes`，`panel-runtime` root 改为 `/opt/bt-panel-runtime/py31318-20261101`，新增说明键 `python_runtime_security_20261101`。未改云端、OAuth 或密钥字段。新 plan SHA-256 为 `a190fb17f4822a95491376e3e45cfc0eb9f97e08610d823df626db0c74bce3b6`。

**新公共 Python roots、面板 venv 和 init / 模板变更尚未由新的全量云备份及解密恢复签收。** 旧全备仍只证明原日期对象范围；本轮两份新业务库备份、配置保全与候选测试不能代替新 Linux 全机启动恢复。恢复流程继续取 [Backend 全备说明](../../../oms-server/oms-backend/doc_md/other/full-backup-20261017.md#操作与恢复顺序)，禁止为了“回退成功”覆盖回旧漏洞运行时。

F 盘本轮目录为 `shiro-bot/.pytest_cache/server-agent-20261101/python-rollout/`，对应服务器保全目录为 `/var/backups/oms-maintenance/python-runtime-20261101/`。入口为 [final.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/python-rollout/final.json)、`prepared.json`、`panel-init-guard.json`、`post-preservation.json` 和两份 `verified-daily-*.json`；临时执行脚本 01～08 同目录保留。这些忽略产物是本机交接证据，不是 Git 发行物。

受保护的 `private/` 只允许当前用户、SYSTEM、Administrators，保存配置原件、前后 plan 和准确快照对，不在文档展示其内容。配置保全包如下；其 SHA 证明准确字节，不代表已完成新全备恢复。

| F 盘 `python-rollout/private/` 保全包 | 大小 | SHA-256 |
| --- | --- | --- |
| `configuration-before.tar.gz` | 15,201 B | `d47be33a681b04cdf2d4e7b89a63546c6d851b7ae27fe07b5a166f544c409b50` |
| `configuration-after.tar.gz` | 9,021 B | `e385c13241f60f82c7b27cede6959484c909f97b815f03ca98260d7197a8975f` |

旧解释器目录、候选及恢复证据均保留，尚未做优化删除。04:57 根盘剩余约 **5.526 GiB**，仍高于原 **4.10 GiB** 恢复预留；这是时点读数，不是长期容量或并发负载保证。

## 已完成的主机包与闲置设施收尾

04:03 CST，先确认 Docker 的容器 / 镜像 / 卷、containerd tasks 为空，单 virtio 磁盘没有 dm maps / holders，再将 `docker.service`、`docker.socket`、`containerd.service`、`multipathd.service`、`multipathd.socket` 停止并 disable；04:57 复核仍 disabled / inactive。没有卸载包，停止后的 MemoryCurrent `[not set]` 不能填成 0 或当作持续收益。收据为 [performance-services.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/performance-services.json)。

04:32 CST，AppArmor / libapparmor1 从 `4.0.1really4.0.1-0ubuntu0.24.04.6` 更新为 `.9`，bubblewrap 为 `0.9.0-1ubuntu0.3`。双站根页仍 200，具体前后包身份及保全 SHA 见 [host-packages.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/host-packages.json)。[USN-8779-2 官方公告](https://lists.ubuntu.com/archives/ubuntu-security-announce/2026-September/011208.html)说明该 bubblewrap 更新撤回了一项存在回归的 symlink 修复，不能据包已更新推断所有 sandbox 漏洞均已解决；Shiro 真实受限进程验证另归其部署记录。

04:22～04:34 CST，将不被实时 config / process exe / cwd / maps 引用的 `/www/server/nginx/src` 打包，并在 F 盘逐件验证后退役源树及本轮自有服务器转运 tar。源树共 **7,301 个普通文件、545,275,904 B**；完整 gzip EOF / CRC 与各文件 SHA 对清单一致。F 盘 `downloads/nginx-legacy-source-20261101.tar.gz` 为 **228,260,917 B**，SHA-256 为 `6780ad7d3ed41d35e4201ac7ce43da15ae5b8b5fa68d44012e2f2c29154c0e93`。

退役前后 live Nginx 配置 SHA 保持，`nginx -t`、双站 200 及既有服务 active 均通过。根盘当时观察净增 773,541,888 B，包含源树和本轮转运 tar，不能等同源树逻辑字节或宣称长期性能收益。归档、F 验证与实际退役分别取 [nginx-source-archive.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/nginx-source-archive.json)、[nginx-source-verified.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/nginx-source-verified.json)、[storage-nginx-retired.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/storage-nginx-retired.json)。运行 Nginx 与原 TLS / vhost 不因源树退役而更新版本或续期。

<a id="host-hardening"></a>

## 05:07 SSH 与防火墙加固

05:07 CST 已用新公钥建立独立 SSH 会话，确认有效配置为 `PasswordAuthentication no`、`KbdInteractiveAuthentication no`、`PubkeyAuthentication yes`、`PermitRootLogin without-password`，X11 forwarding 关闭；确认新会话可用后取消防锁死回滚 timer。旧 04:55 的口令允许观察保留原时点，不能当作当前状态。收据为 [host-hardening.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/host-hardening.json)，配置原件仍在受限保全目录，不在文档复制密钥。

UFW 保持 active / 默认拒绝入站，精确删除 **20/tcp、21/tcp、39000:40000/tcp、888/tcp、8888/tcp** 的 IPv4 与 IPv6 放行；保留 **22、80、443、BT 12034/tcp** 的双栈规则。此处只记录已确认无用的旧规则收敛，没有改网站、QQ 回调路径或 TLS 续期配置。

<a id="candidate-isolation"></a>

## AppArmor、受限 Linux QA 与模型探针

05:06 CST 已加载 `/etc/apparmor.d/shiro-bwrap`，只针对 `/usr/bin/bwrap` 所需能力；全局 `kernel.apparmor_restrict_unprivileged_userns=1` 保持，没有增加网络共享或全局关闭 user namespace 限制。profile SHA-256 为 `dfab20a13e6650d6d9d570a15e039be1fb685e71a5cc16755b58d8ab8bd6b81a`，见 [bwrap-profile-installed.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/bwrap-profile-installed.json)。

05:15 CST，候选源码树 `540ce53f3c455370084e259bf41ff8c71ce0d57f0293a8ff53076c40726f6a24` 以真实服务用户、`NoNewPrivileges`、CPU 50% / MemoryMax 384 MiB 的受限 unit 执行，**37 passed**。其中 runner 的 **13 项**覆盖真实 seccomp、子进程继承与 ABI；这是针对执行面的缓解验证，不是修复宿主内核。准确命令范围、退出码与执行时段取 [linux-qa-isolation-final.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/linux-qa-isolation-final.json)，不把 Windows 跳过项计作已通过。

05:18～05:19 CST，同一 QA 来源用真实 `deepseek-flash` 完成文件写后读、自建 Python 工具开发与调用、记忆写入及两字中文检索、60 秒延迟任务；另一个 synthetic Actor 的隔离检查通过，QQ send 调用为 **0**。收据为 [model-probe.initial.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/model-probe.initial.json)。这些是合成身份的真实模型 / 工具探针，不是新 Bot 正式部署或 QQ 真人验收；业务合同继续只取 Shiro。

<a id="dependency-security"></a>

## BT 两项依赖补修与精确版本核对

05:21 CST 冷停 BT 后，离线 `--no-deps` 仅将 **dnspython 2.8.0 → 2.9.0、PyMongo 4.18.2 → 4.18.3**；共 85 包，其余包名 / 版本不变。前后包 / 环境 / init 指纹保留，`pip check`、正常 DNS / BSON / JWT / gevent、TLS loopback 根页 404、双站与双 health 200 通过；init 与模板 SHA 仍为上方同一指纹。第一次误用 HTTP 请求 TLS-only 面板得到 curl 56，改用 HTTPS 后回到原 404 基线；该探测失败不记作真实服务故障。准确保全与输出见 [bt-dependencies-updated.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/bt-dependencies-updated.json)。04:57 的“包版本保持”只描述当时 Python 切换窗口，不覆盖这次两包补修。

[dnspython 项目公告](https://github.com/rthalley/dnspython/security/advisories/GHSA-45c3-73f7-pv4m)针对不可信 DNS wire 解压的 CPU 消耗，修复版本为 2.9.0；[PyMongo 项目公告](https://github.com/mongodb/mongo-python-driver/security/advisories/GHSA-98qm-wvgf-w4cf)针对 C BSON decoder 从 mmap / array 等无 NUL 结尾缓冲区读取畸形 Regex 的崩溃风险，修复版本为 4.18.3。公告排除 bytes / bytearray、驱动自身 transport 与纯 Python decoder，不能把版本命中写成当前互联网 Mongo 链必可触发。

[PyPI dnspython 2.9.0](https://pypi.org/project/dnspython/2.9.0/)要求 Python ≥3.11，默认无强制外部依赖；[PyMongo 4.18.3](https://pypi.org/project/pymongo/4.18.3/)要求 Python ≥3.9，唯一强制依赖仍为 `dnspython>=2.7,<3`，与原 4.18.2 一致；BT 3.13.18 满足要求。optional extras 的门槛变化不等于已启用新功能或全面兼容验收。

补修前四环境实际元数据与 115 个去重 PyPI name/version 的 OSV batch 记录在 `dependency-security/`：OMS 与固定 helper 各 20 个公共包未返回匹配，本地 `oms-ir` 未发送公网；Bot 候选 34 包未返回匹配；BT 的 83 包未返回匹配，另外两包命中上述公告。05:25 CST 对已补修两版本重新查询 OSV 均未返回匹配，见 [postfix 收据](../../../shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/osv-postfix-query.json)。初次查询没有失败或未完成分页；未知范围和 BT API 触达条件未由本次扫描证明。完整 [review-summary.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/review-summary.json)保留补修前时点，未命中不代表全无漏洞。

<a id="release-runtime-guards"></a>

## 发布与回退源码防降级

Backend 的 [prepare-release.sh](../../../oms-server/oms-backend/deploy/prepare-release.sh)、[activate-release.sh](../../../oms-server/oms-backend/deploy/activate-release.sh)及 Web [安装器](../scripts/install-production.py)已在本地固定公共 3.12.16 解释器，禁止托管旧版本选择与自动 Python 下载；创建发布目录前和生成 venv 后验证真实 base / Python / OpenSSL / SQLite / certifi，激活与回滚 previous 同样受门槛约束。应用 lock、发布白名单与不可变历史 manifest 保持，没有把固定 helper 改指向 HTTP current。

真实只读验证发现首版 guard 把 OpenSSL 的 `(3,5,0,9,0)` 错当作三元组而误拒 3.5.9；原失败收据保留。修正为严格解析稳定版本字符串后，真实五元组夹具覆盖 3.5.8 拒绝、3.5.9 / 3.6.0 通过、预览及未知后缀拒绝，`-O` 不能绕过。最新定向为 **Backend 39 passed / Web 20 tests OK**，取代先前 29 / 18 数字；OMS / helper 实际各执行三条纯 guard，共 **6 passed**，见 [runtime-guards-verified.json](../../../shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/runtime-guards-verified.json)。这只是源码及纯 guard 验证，没有执行真实 uv sync、应用 build / activate 或改写服务器发布脚本。

<a id="remaining-security"></a>

## 上游安全项与尚未验收范围

04:55 CST 的 [只读观察](../../../shiro-bot/.pytest_cache/server-agent-20261101/security-observation.json)显示系统 OpenSSH `1:9.6p1-3ubuntu13.20`、OpenSSL `3.0.13-0ubuntu3.16`、系统 Python `3.12.3-1ubuntu0.17` 与 APT candidate 相同，已安装内核候选为 `6.8.0-147.147`；`reboot-required=true` 的原因和实际重启尚待后续核实。系统发行版有回移修复，不能只拿上游版本号比较来断言漏洞。

2026-11-01 主源核对时，[CVE-2026-115557](https://ubuntu.com/security/CVE-2026-115557) 的 Noble 系统 python3.12 仍为 **Needs evaluation**；应用公共 Python 3.12.16 / 3.13.18 的修复不自动覆盖系统 Python。[CVE-2026-98260](https://ubuntu.com/security/CVE-2026-98260) 早先观察待评估，当前官网 10 月 29 日状态已列 Noble linux 为 **Vulnerable work in progress in 6.8.0-148.148**；不能把现有 6.8.0-147 或一次重启签成该项已修复。两项保留待跟踪，不写“全无漏洞”。

本轮实际内核仍为 6.8.0-147；6.8.0-148.148 尚未进入本机已签名 APT 候选。前述 runner seccomp 是执行面的定向缓解，不把宿主 CVE 标为关闭。系统 Python 继续由 Ubuntu 回移维护，不手工替换 `/usr/bin/python3`；既有 `intel-microcode` / `cloud-init` hold 保持，不为清空待更新列表强行 unhold。生产 Node 22.23.4 已覆盖 [Node.js 10 月 21 日安全发布](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases)对应的 22.x 修复，具体版本取 [22.23.4 官方记录](https://nodejs.org/en/blog/release/v22.23.4/)，没有据此重建或发布网站应用。

04:17 的 [USN 定向比对](../../../shiro-bot/.pytest_cache/server-agent-20261101/usn-review.json)只检查 Noble 最新 20 条公告与当时 933 个已安装包，匹配包未见低于公告修复版本；其范围不等于全面漏洞审计。实际 BT Nginx 与系统 nginx 包分别核对；此前 PHP / Nginx 修复继续取 [10 月 22 日记录](php-security-maintenance-20261022.md)，上游跟踪入口为 [Nginx 安全公告](https://nginx.org/en/security_advisories.html) 与 [OpenSSL 公告](https://openssl-library.org/news/vulnerabilities/)。

04:55 仍观察到 root password SSH 允许及若干无监听旧端口放行；后续 key-only、精确 UFW 变更、新 SSH 会话和防锁死回滚验证尚待实际执行收据。自 10 月 22 日读取的 6,012 行 SSH 日志中 accepted password 为 0、failed password 为 446，不能把没有成功口令记录当成不需加固。

05:07 的 SSH / UFW 收据已接续上段 04:55 待办；当前仍待新 Bot 正式切换、独立状态备份、新 full plan roots 的全备 / 解密恢复及维护重启各自收据。候选 Linux / 真实模型探针不能提前签收这些门。

本轮没有发布 Homepage / OMS 页面、改业务库内容、改 TLS 续期或提升 OMS 产品阶段。OMS 继续 **已部署待真人验收**，原账号 / 下载 / 桌面 / P-C 等剩余门只取 [现行真人验收](production-maintenance.md#真人验收)。双站 HTTPS 根页 200 不签实际续期；备份 timer 恢复不签新全备；受控脚本不签 QQ 真人收发。
