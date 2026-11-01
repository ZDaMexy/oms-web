# 2026-11-01 共享服务器运行时与安全维护

> 证据落点更新（2026-11-01）：旧 Shiro 开发目录已完整 ZIP 校验后移除；下方旧业务文档固定到封存提交，原本地收据从 ZIP 按成员路径查阅，位置与校验身份取[交接](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md)。本次只调整引用，不刷新原验证日期、网站发布或恢复结论。

> **当前接续至 06:37 CST**：运行时、安全加固、Shiro v0.2 切换 / 同机恢复、[旧面板退役](#panel-retirement)、[新全备完成](#current-release-backup)及[维护重启](#maintenance-reboot)均已取得实际收据；四个 timer 均 enabled / active / waiting。[本地 Web 构建依赖修复](#web-dependency-security)已提交但未部署。真人验收、两项上游 CVE、本轮云端 age 解密 / 异机演练边界保持；下文 04:57 段保留当时范围。

本记录是本轮 OMS / BT 运行时、共享主机清理与恢复边界的权威落点。截至 2026-11-01 04:57 CST，OMS HTTP、catalog 和固定备份 helper 已切至 Python 3.12.16，BT 面板已切至 Python 3.13.18；应用来源、同一业务库及依赖包名 / 版本保持。后续 SSH / UFW 加固、Shiro 新运行面与维护重启尚待各自实际收据，不能由这里的有限检查提前签收。

Homepage、OMS 与 Shiro 仍是独立产品，只共享主机、Nginx、TLS 和 SSH。两站设施镜像见 [Homepage](../../homepage-website/doc_md/other/shared-agent-security-20261101.md) 与 [旧 OMS Website](../../oms-website/doc_md/other/shared-agent-security-20261101.md)。Bot 的当前发布、恢复和真人收发边界只取 [Shiro 部署记录](https://github.com/ZDaMexy/Shiro-BOT/blob/364fb1dcf34c6f4ba669dedb1bcd87a34f66b915/doc_md/mainline/qq-official-deployment.md)，不在本页复制业务合同。

<a id="current-release-backup"></a>

## 05:43～06:35 当前发布与备份状态

05:43 CST，Shiro v0.2 已正式切至 `4dc8422e191447a7b842f59f2c7f594e49926450`；独立状态快照和同机新目录恢复已通过，准确来源、恢复范围与真人门只取 [Shiro 部署记录](https://github.com/ZDaMexy/Shiro-BOT/blob/364fb1dcf34c6f4ba669dedb1bcd87a34f66b915/doc_md/mainline/qq-official-deployment.md)。同机恢复不代替这轮云端全备的 age 解密或异机启动。

Backend `1de5eab4f0743cda626ea70e935608bc1053b5a0` 已提交并推送，新增八类备份归档和按 plan 条件采集的主机元数据：只有纳入 Shiro roots 时才要求其账户、记录其 current / venv 和相关 unit。结合真实 age 的发布 guard / 备份聚焦回归共 **108 passed**，保留 **1 条既有 Starlette 提示**；这是本轮组合回归，不能以先前仅 guard 的 39 项概括，也不签收云端全备。

05:54 CST，新工具 `/opt/oms-netdisk-backup/releases/d9a42ff093e1799d` 和 plan 已实际部署；旧 `f7b8b9b0a39b7971` 保留。plan SHA-256 为 `6f7b547d9c299ee598f7a30013dbbb4e44344851609e791ad711a58aa9416df6`，**42 个声明 roots，预期展开 49 个对象**；49 是计划预期，不是已上传对象数。八类新增标签为 `shiro-source`、`shiro-venv`、`shiro-gallery`、`shiro-config`、`shiro-snapshots`、`ssh-config`、`ufw-config`、`bwrap-policy`，归档映射只取 [Backend 分层记录](../../../oms-server/oms-backend/doc_md/other/netdisk-layout-20261017.md)。Shiro 仅收已完成的独立快照，不直接复制在线 SQLite / WAL；固定 helper 和 age 1.3.2 二进制保持，见 [full-plan-prepared.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/full-plan-prepared.json`）。

05:55:51 CST 已启动真实全备；05:57:13 CST 收据仍为 `oms-full-backup.service` activating、MainPID **146489**、InvocationID `d94fff5199f147b99e88feb09c1d6022`。full timer 已恢复 **enabled / active**，当时 substate 为 running，仍是同一 worker；恢复 Persistent timer 没有并行启动另一份全备。证据为 [启动记录 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/full-backup-started.json`）与 [timer 恢复记录 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/full-timer-restored.json`）。该 05:57 收据没有签收本轮完成、age 解密 / 异机启动或整机重启；后续旧面板退役见下段 06:29 记录。

**06:35:34 CST 本轮全备完成**：同一 InvocationID 返回 ExecMainStatus=0 / Result=success，worker inactive，MainPID=0 / ControlPID=0，无 pending 或 last failure。42 个声明 roots 实际展开 **49 个对象及 catalog**；本轮新传输对象密文合计 **1,034,400,938 B**（不含 catalog）。catalog 密文 **12,326 B**，SHA-256 `e675b44bf3a1c7f2b99c4b7ddbfb1ac7a39605c1cd66a23941674f61a58754a2`。本轮新增 / 变化密文均由已部署工具上传后完整下载核 SHA；八类新增对象的 verified_at 均晚于本轮开始，未变化对象只做 metadata probe 后复用，不能写成 49 对象本轮全部重传 / 下载。准确终态见 [full-completion.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/full-completion.json`）。

host metadata 已实际收录 Shiro UID 994 / GID 984、当前 `4dc8422` / `venv-agent-20261101` 和启用的快照 timer；catalog 明确只收已完成快照，不复制在线 Shiro DB / 工作区。三 OMS timer 加 Shiro 独立快照 timer 均 **enabled / active / waiting**，完成时根分区 free **6,601,326,592 B**。没有读取恢复私钥，也没有验证本轮云端 age 解密或异机启动；全备成功与 Shiro 同机恢复继续分别记账。维护重启在备份 worker idle、Shiro 任务执行数 / 排队数均为 0 后发起，最终验证见[06:37 收据](#maintenance-reboot)。

以上没有发布 OMS HTTP / Web 应用，现行应用与固定 helper 身份仍取下方 04:57 记录。

<a id="panel-retirement"></a>

## 06:29 旧面板历史目录退役

06:29:16 CST，仅删除 `/www/server/panel.before-security-20261022`（device 64771 / inode 523268）和本次自有 transport archive。删除前已经在受限 F 盘逐普通文件 SHA 核对 **22,327 文件**，验证 **24,521 个 tar 成员**的 metadata / links 与完整 gzip EOF / CRC；未解压、未运行旧面板。保留归档 **220,333,211 B**，SHA-256 `f5ce966217e80fea8945898a6b65ca5671962245e988700cf8fcabad61bef085`；manifest SHA-256 `1e9a66ab46107815248f0e420eb8979c37649c1c5b768ca37afd185bac2b4a79`，主执行者独立重算两者通过。保全阶段见 [panel-preservation-verified.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/panel-preservation-verified.json`），其中“服务器源仍保留”只描述 06:24 当时交接点；最终删除结果取 [storage-panel-retired.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/storage-panel-retired.json`）。

删除前检查 **131 个进程 / 891 个 FD**，live references 与 unreadable surfaces 均为 **0**，现行 full plan 对该路径 overlap 为 **0**。复核 18 份 Nginx 配置，配置指纹 SHA-256 `47835bcc7386f6506d21b5037b8fc592d6dfd11111fd504fa932695b93824262` 前后保持；Nginx `-t`、双站 / 双 health 200、面板 HTTPS 404 基线通过，既有业务服务和 PID 保持、NRestarts=0；并行全备 MainPID 146489 未受干预。live panel 目录、现行 pyenv 与产品 current 指针保持。

源 allocated 为 **762,077,184 B**，自有 transport archive allocated 为 **220,340,224 B**，收据确认二者均已不存在，F 保全件保持。实际 free bytes 从 **5,553,983,488 → 6,536,396,800 B**，净增加 **982,413,312 B**；该窗口有并行全备，这是磁盘净观察，不能冒充纯删除的理论增量，也不代表全备已经完成。

<a id="maintenance-reboot"></a>

## 06:37 维护重启与有限运行复核

06:37:46 CST 已确认 boot ID 从 `c86831bc-72d2-4120-833a-0492c4fed5de` 变为 `90046c1e-0cff-4692-aa98-276bef790d7e`，运行内核仍为 **6.8.0-147-generic**，reboot-required 已消失，原提示来自 AppArmor 更新；这次重启没有把 WIP 的 CVE-2026-98260 修复到 148。终态取 [maintenance-reboot-verified.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/maintenance-reboot-verified.json`），细项取 [maintenance-observation-after.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/maintenance-observation-after.json`）。

业务服务均 active / NRestarts=0；备份 workers MainPID / ControlPID 均为 0，四个 timer enabled / active / waiting，准确下次触发时间取收据，不沿用重启前调度观察。新 SSH 公钥会话验证通过，key-only 配置、启用的 ssh.socket、UFW 双栈精确规则、bwrap AppArmor profile 与全局 userns restriction=1 均保持。配置 SHA、pyenv / venv / current links、OMS DB device 64771 / inode 265517 / schema3 / 22 表保持；BT-Panel 实际 executable 为公共 Python 3.13.18，原生 BT-Task executable 未改，init 与模板 SHA 一致。

双站 / 双 health 200、Bot health ok（queued=0 / active=0）、内外 QQ challenge 200 及 Ed25519 验签、bad hex 403、面板 HTTPS 404、Nginx `-t` 均通过。真实 shiro-bot 身份与严格 unit / bwrap 在重启后复核保留的 synthetic 恢复态：两个原文件、两字“青色”记忆索引、`custom_sum_pair(20,22)=42`、已完成任务和 history 均保持；QQ / 模型调用 **0**，没有覆盖 live state。收据见 [post-reboot-agent-probe.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/post-reboot-agent-probe.json`），业务恢复合同仍只取 Shiro。

06:37 的根分区 free **6,613,368,832 B（约 6.159 GiB）**，MemAvailable **965,308,416 B（约 920.59 MiB）**，swap 使用 0；约 6 秒 startup 样本 CPU busy **6.86%**、IOwait **0.42%**。这是重启后的短时观察，不证明长期吞吐、持续峰值或单由框架替换带来的资源节省。

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

> 本节保留 **04:57 切换阶段**的 plan / 保全原文，以下“尚未新全备”是当时状态。后续新 plan、06:35 全备完成及 06:37 重启分别见[当前状态](#current-release-backup)与[重启收据](#maintenance-reboot)；本轮云端 age 解密 / 异机启动仍未验收。

`/etc/oms-full-backup/plan.json` 仅修改必要解释器对象 / 来源说明：`python` root 改为 `/opt/python-runtimes`，`panel-runtime` root 改为 `/opt/bt-panel-runtime/py31318-20261101`，新增说明键 `python_runtime_security_20261101`。未改云端、OAuth 或密钥字段。新 plan SHA-256 为 `a190fb17f4822a95491376e3e45cfc0eb9f97e08610d823df626db0c74bce3b6`。

**新公共 Python roots、面板 venv 和 init / 模板变更尚未由新的全量云备份及解密恢复签收。** 旧全备仍只证明原日期对象范围；本轮两份新业务库备份、配置保全与候选测试不能代替新 Linux 全机启动恢复。恢复流程继续取 [Backend 全备说明](../../../oms-server/oms-backend/doc_md/other/full-backup-20261017.md#操作与恢复顺序)，禁止为了“回退成功”覆盖回旧漏洞运行时。

完整 ZIP 内的原本轮目录为 `shiro-bot/.pytest_cache/server-agent-20261101/python-rollout/`，对应服务器保全目录为 `/var/backups/oms-maintenance/python-runtime-20261101/`。入口为 [final.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/python-rollout/final.json`）、`prepared.json`、`panel-init-guard.json`、`post-preservation.json` 和两份 `verified-daily-*.json`；临时执行脚本 01～08 同目录保留。这些忽略产物是本机交接证据，不是 Git 发行物。

受保护的 `private/` 只允许当前用户、SYSTEM、Administrators，保存配置原件、前后 plan 和准确快照对，不在文档展示其内容。配置保全包如下；其 SHA 证明准确字节，不代表已完成新全备恢复。

| F 盘 `python-rollout/private/` 保全包 | 大小 | SHA-256 |
| --- | --- | --- |
| `configuration-before.tar.gz` | 15,201 B | `d47be33a681b04cdf2d4e7b89a63546c6d851b7ae27fe07b5a166f544c409b50` |
| `configuration-after.tar.gz` | 9,021 B | `e385c13241f60f82c7b27cede6959484c909f97b815f03ca98260d7197a8975f` |

旧解释器目录、候选及恢复证据均保留，尚未做优化删除。04:57 根盘剩余约 **5.526 GiB**，仍高于原 **4.10 GiB** 恢复预留；这是时点读数，不是长期容量或并发负载保证。

## 已完成的主机包与闲置设施收尾

04:03 CST，先确认 Docker 的容器 / 镜像 / 卷、containerd tasks 为空，单 virtio 磁盘没有 dm maps / holders，再将 `docker.service`、`docker.socket`、`containerd.service`、`multipathd.service`、`multipathd.socket` 停止并 disable；04:57 复核仍 disabled / inactive。没有卸载包，停止后的 MemoryCurrent `[not set]` 不能填成 0 或当作持续收益。收据为 [performance-services.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/performance-services.json`）。

04:32 CST，AppArmor / libapparmor1 从 `4.0.1really4.0.1-0ubuntu0.24.04.6` 更新为 `.9`，bubblewrap 为 `0.9.0-1ubuntu0.3`。双站根页仍 200，具体前后包身份及保全 SHA 见 [host-packages.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/host-packages.json`）。[USN-8779-2 官方公告](https://lists.ubuntu.com/archives/ubuntu-security-announce/2026-September/011208.html)说明该 bubblewrap 更新撤回了一项存在回归的 symlink 修复，不能据包已更新推断所有 sandbox 漏洞均已解决；Shiro 真实受限进程验证另归其部署记录。

04:22～04:34 CST，将不被实时 config / process exe / cwd / maps 引用的 `/www/server/nginx/src` 打包，并在 F 盘逐件验证后退役源树及本轮自有服务器转运 tar。源树共 **7,301 个普通文件、545,275,904 B**；完整 gzip EOF / CRC 与各文件 SHA 对清单一致。F 盘 `downloads/nginx-legacy-source-20261101.tar.gz` 为 **228,260,917 B**，SHA-256 为 `6780ad7d3ed41d35e4201ac7ce43da15ae5b8b5fa68d44012e2f2c29154c0e93`。

退役前后 live Nginx 配置 SHA 保持，`nginx -t`、双站 200 及既有服务 active 均通过。根盘当时观察净增 773,541,888 B，包含源树和本轮转运 tar，不能等同源树逻辑字节或宣称长期性能收益。归档、F 验证与实际退役分别取 [nginx-source-archive.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/nginx-source-archive.json`）、[nginx-source-verified.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/nginx-source-verified.json`）、[storage-nginx-retired.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/storage-nginx-retired.json`）。运行 Nginx 与原 TLS / vhost 不因源树退役而更新版本或续期。

<a id="host-hardening"></a>

## 05:07 SSH 与防火墙加固

05:07 CST 已用新公钥建立独立 SSH 会话，确认有效配置为 `PasswordAuthentication no`、`KbdInteractiveAuthentication no`、`PubkeyAuthentication yes`、`PermitRootLogin without-password`，X11 forwarding 关闭；确认新会话可用后取消防锁死回滚 timer。旧 04:55 的口令允许观察保留原时点，不能当作当前状态。收据为 [host-hardening.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/host-hardening.json`），配置原件仍在受限保全目录，不在文档复制密钥。

UFW 保持 active / 默认拒绝入站，精确删除 **20/tcp、21/tcp、39000:40000/tcp、888/tcp、8888/tcp** 的 IPv4 与 IPv6 放行；保留 **22、80、443、BT 12034/tcp** 的双栈规则。此处只记录已确认无用的旧规则收敛，没有改网站、QQ 回调路径或 TLS 续期配置。

<a id="candidate-isolation"></a>

## AppArmor、受限 Linux QA 与模型探针

05:06 CST 已加载 `/etc/apparmor.d/shiro-bwrap`，只针对 `/usr/bin/bwrap` 所需能力；全局 `kernel.apparmor_restrict_unprivileged_userns=1` 保持，没有增加网络共享或全局关闭 user namespace 限制。profile SHA-256 为 `dfab20a13e6650d6d9d570a15e039be1fb685e71a5cc16755b58d8ab8bd6b81a`，见 [bwrap-profile-installed.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/bwrap-profile-installed.json`）。

05:15 CST，候选源码树 `540ce53f3c455370084e259bf41ff8c71ce0d57f0293a8ff53076c40726f6a24` 以真实服务用户、`NoNewPrivileges`、CPU 50% / MemoryMax 384 MiB 的受限 unit 执行，**37 passed**。其中 runner 的 **13 项**覆盖真实 seccomp、子进程继承与 ABI；这是针对执行面的缓解验证，不是修复宿主内核。准确命令范围、退出码与执行时段取 [linux-qa-isolation-final.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/linux-qa-isolation-final.json`），不把 Windows 跳过项计作已通过。

05:18～05:19 CST，同一 QA 来源用真实 `deepseek-flash` 完成文件写后读、自建 Python 工具开发与调用、记忆写入及两字中文检索、60 秒延迟任务；另一个 synthetic Actor 的隔离检查通过，QQ send 调用为 **0**。收据为 [model-probe.initial.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/model-probe.initial.json`）。这些是合成身份的真实模型 / 工具探针，不是新 Bot 正式部署或 QQ 真人验收；业务合同继续只取 Shiro。

<a id="dependency-security"></a>

## BT 两项依赖补修与精确版本核对

05:21 CST 冷停 BT 后，离线 `--no-deps` 仅将 **dnspython 2.8.0 → 2.9.0、PyMongo 4.18.2 → 4.18.3**；共 85 包，其余包名 / 版本不变。前后包 / 环境 / init 指纹保留，`pip check`、正常 DNS / BSON / JWT / gevent、TLS loopback 根页 404、双站与双 health 200 通过；init 与模板 SHA 仍为上方同一指纹。第一次误用 HTTP 请求 TLS-only 面板得到 curl 56，改用 HTTPS 后回到原 404 基线；该探测失败不记作真实服务故障。准确保全与输出见 [bt-dependencies-updated.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/bt-dependencies-updated.json`）。04:57 的“包版本保持”只描述当时 Python 切换窗口，不覆盖这次两包补修。

[dnspython 项目公告](https://github.com/rthalley/dnspython/security/advisories/GHSA-45c3-73f7-pv4m)针对不可信 DNS wire 解压的 CPU 消耗，修复版本为 2.9.0；[PyMongo 项目公告](https://github.com/mongodb/mongo-python-driver/security/advisories/GHSA-98qm-wvgf-w4cf)针对 C BSON decoder 从 mmap / array 等无 NUL 结尾缓冲区读取畸形 Regex 的崩溃风险，修复版本为 4.18.3。公告排除 bytes / bytearray、驱动自身 transport 与纯 Python decoder，不能把版本命中写成当前互联网 Mongo 链必可触发。

[PyPI dnspython 2.9.0](https://pypi.org/project/dnspython/2.9.0/)要求 Python ≥3.11，默认无强制外部依赖；[PyMongo 4.18.3](https://pypi.org/project/pymongo/4.18.3/)要求 Python ≥3.9，唯一强制依赖仍为 `dnspython>=2.7,<3`，与原 4.18.2 一致；BT 3.13.18 满足要求。optional extras 的门槛变化不等于已启用新功能或全面兼容验收。

补修前四环境实际元数据与 115 个去重 PyPI name/version 的 OSV batch 记录在 `dependency-security/`：OMS 与固定 helper 各 20 个公共包未返回匹配，本地 `oms-ir` 未发送公网；Bot 候选 34 包未返回匹配；BT 的 83 包未返回匹配，另外两包命中上述公告。05:25 CST 对已补修两版本重新查询 OSV 均未返回匹配，见 [postfix 收据 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/osv-postfix-query.json`）。初次查询没有失败或未完成分页；未知范围和 BT API 触达条件未由本次扫描证明。完整 [review-summary.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/review-summary.json`）保留补修前时点，未命中不代表全无漏洞。

<a id="web-dependency-security"></a>

## Web 实际依赖与本地 npm 构建修复

06:24 CST 精确 OSV 查询分别取实际 Composer installed metadata、Homepage 源码及实际构建 lock；不是只拿仓库声明代签服务器。原始范围与结果见 [web-osv-exact.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/web-osv-exact.json`）及[摘要 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/web-osv-summary.json`）。

| 对象 | 精确范围与本轮结果 |
| --- | --- |
| OMS Web 实际 Composer | `/opt/oms-ir/current/web/vendor/composer/installed.json` 的 74 个版本对未返回匹配；metadata SHA-256 `9491693ecc420dff10fb0c35cb7fe3487a4b89cf88ea31799bd0180db4bcbd16` |
| Homepage 源码及实际构建 npm | 各 275 个版本对未返回匹配；两端 lock SHA-256 均为 `99e1588858ebe064e2b55b9a8a877584acdb9eb9c40d3734dc34ea57306751bd` |
| OMS Web 本地 npm 修复前 | 316 个版本对中四包命中七条公告；这是构建依赖版本命中，实际触发条件如下，未证明线上可利用 |
| OMS Web 本地 npm 修复后 | 295 个版本对的 batch 返回 HTTP 200，0 命中、0 未完分页；当前 lock SHA-256 `551b00e2f47463ea211946ee9d7605b9281ec19440c9d93bda504d5206a84038`，没有部署到服务器 |

`fast-uri 3.1.8 → 3.1.9` 覆盖维护者的 [suffix scheme](https://github.com/fastify/fast-uri/security/advisories/GHSA-333x-w4r6-6crp)、[编码 scheme](https://github.com/fastify/fast-uri/security/advisories/GHSA-w74x-v6f9-j3xg)、[host canonicalization](https://github.com/fastify/fast-uri/security/advisories/GHSA-wjr9-j795-jxcr)、[相对路径](https://github.com/fastify/fast-uri/security/advisories/GHSA-xhq7-xmqj-769h)四项修复。当前调用来自 CSS 构建插件的 schema-utils / Ajv URI schema resolver，输入为构建 schema；没有确认不可信网页输入经这些 API 执行 URL 授权 / 路由。suffix 项另要求非默认 `reference:'suffix'`，不能把版本命中等同当前网页 XSS。

`serialize-javascript 7.1.2 → 7.1.4` 保留 7.1.3 的[函数尾部 script escaping 修复](https://github.com/yahoo/serialize-javascript/security/advisories/GHSA-m5mm-p8h7-m29v)，并采用同系列 [7.1.4 方法序列化修正](https://github.com/yahoo/serialize-javascript/releases/tag/v7.1.4)。公告要求攻击者控制序列化函数的 source / `toString()`，再嵌入 script；普通字符串和正常函数不满足条件。当前 CSS 插件只有 worker 分支才序列化该选项，而仓库配置 `parallel:false`，未确认当前入口可触发。

另外两项由重复的 ForkTsChecker 引入。[deepmerge 问题页](https://github.com/TehShrike/deepmerge/issues/273)所述为特定 target shape 下返回对象继承攻击者原型，未修改全局 Object.prototype；维护者有争议，npm 最新仍为 4.3.1，没有找到已发布补丁。当前只合并本地构建配置，未确认 HTTP 输入路径。[minimatch 维护者公告](https://github.com/isaacs/minimatch/security/advisories/GHSA-g3hv-75wg-m249)只列 10.2.6、`optimizationLevel>=2` 的 `firstPhasePreProcess`；OSV 的 `<11.0.1` 范围更宽，实际 3.1.5 不含该逻辑，不能直接提升为已证实的 v3 漏洞。

实际修复仅删 ForkTsChecker 的 devDependency、webpack require 与实例：原 `ts-loader` 已设 `transpileOnly:false`，独立 `typecheck` 亦保持。随插件移除 22 个节点，全部属于其原依赖闭包；无新增节点、无 override，保留包只更新上述两个版本。三个源码文件已在验证后提交并推送为 `7000b906257a68776eec42d8d353ab3e3e50246a`，测试时保留 `e308a4a94f` HEAD / 工作树身份，没有把提交动作伪装成重新验收。

实际环境为 Windows、Node 24.22.1 / npm 11.19.1，F 盘缓存；`npm ci --ignore-scripts --no-audit --no-fund`、`npm run typecheck`、`npm run production` 通过，构建保留三项既有体积 / entrypoint 建议。一次向真实 app 入口临时注入 TS2322 的生产配置负向探针被拒绝，入口 SHA 精确恢复；dotenv 配置调用禁用并阻断文件读取，未读生产配置。`public/assets` 现存 484 个文件前后 SHA 全部相同，未部署网站或改变线上 assets。完整[本地报告](../.dev-cache/npm-security-20261101/report.json)保留源码 SHA、依赖差异、负向恢复与原始日志；版本未匹配不保证不存在漏洞，也不代签 Linux 构建、网页功能或真人验收。

<a id="release-runtime-guards"></a>

## 发布与回退源码防降级

Backend 的 [prepare-release.sh](../../../oms-server/oms-backend/deploy/prepare-release.sh)、[activate-release.sh](../../../oms-server/oms-backend/deploy/activate-release.sh)及 Web [安装器](../scripts/install-production.py)已在本地固定公共 3.12.16 解释器，禁止托管旧版本选择与自动 Python 下载；创建发布目录前和生成 venv 后验证真实 base / Python / OpenSSL / SQLite / certifi，激活与回滚 previous 同样受门槛约束。应用 lock、发布白名单与不可变历史 manifest 保持，没有把固定 helper 改指向 HTTP current。

真实只读验证发现首版 guard 把 OpenSSL 的 `(3,5,0,9,0)` 错当作三元组而误拒 3.5.9；原失败收据保留。修正为严格解析稳定版本字符串后，真实五元组夹具覆盖 3.5.8 拒绝、3.5.9 / 3.6.0 通过、预览及未知后缀拒绝，`-O` 不能绕过。guard 定向为 **Backend 39 passed / Web 20 tests OK**，取代先前 29 / 18 数字；后续含备份与真实 age 的 **108 passed** 组合范围见[当前状态](#current-release-backup)。OMS / helper 实际各执行三条纯 guard，共 **6 passed**，见 [runtime-guards-verified.json 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/dependency-security/runtime-guards-verified.json`）。这只是源码及纯 guard 验证，没有执行真实 uv sync、应用 build / activate 或改写服务器发布脚本。

<a id="remaining-security"></a>

## 上游安全项与尚未验收范围

04:55 CST 的 [只读观察 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/security-observation.json`）显示系统 OpenSSH `1:9.6p1-3ubuntu13.20`、OpenSSL `3.0.13-0ubuntu3.16`、系统 Python `3.12.3-1ubuntu0.17` 与 APT candidate 相同，已安装内核候选为 `6.8.0-147.147`；`reboot-required=true` 的原因和实际重启尚待后续核实。系统发行版有回移修复，不能只拿上游版本号比较来断言漏洞。

2026-11-01 主源核对时，[CVE-2026-115557](https://ubuntu.com/security/CVE-2026-115557) 的 Noble 系统 python3.12 仍为 **Needs evaluation**；应用公共 Python 3.12.16 / 3.13.18 的修复不自动覆盖系统 Python。[CVE-2026-98260](https://ubuntu.com/security/CVE-2026-98260) 早先观察待评估，当前官网 10 月 29 日状态已列 Noble linux 为 **Vulnerable work in progress in 6.8.0-148.148**；不能把现有 6.8.0-147 或一次重启签成该项已修复。两项保留待跟踪，不写“全无漏洞”。

本轮实际内核仍为 6.8.0-147；6.8.0-148.148 尚未进入本机已签名 APT 候选。前述 runner seccomp 是执行面的定向缓解，不把宿主 CVE 标为关闭。系统 Python 继续由 Ubuntu 回移维护，不手工替换 `/usr/bin/python3`；既有 `intel-microcode` / `cloud-init` hold 保持，不为清空待更新列表强行 unhold。生产 Node 22.23.4 已覆盖 [Node.js 10 月 21 日安全发布](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases)对应的 22.x 修复，具体版本取 [22.23.4 官方记录](https://nodejs.org/en/blog/release/v22.23.4/)，没有据此重建或发布网站应用。

04:17 的 [USN 定向比对 的归档入口](../../../Shiro-Agent/doc_md/mainline/legacy-handoff.md#完整-zip)（ZIP 内 `shiro-bot/.pytest_cache/server-agent-20261101/usn-review.json`）只检查 Noble 最新 20 条公告与当时 933 个已安装包，匹配包未见低于公告修复版本；其范围不等于全面漏洞审计。实际 BT Nginx 与系统 nginx 包分别核对；此前 PHP / Nginx 修复继续取 [10 月 22 日记录](php-security-maintenance-20261022.md)，上游跟踪入口为 [Nginx 安全公告](https://nginx.org/en/security_advisories.html) 与 [OpenSSL 公告](https://openssl-library.org/news/vulnerabilities/)。

04:55 仍观察到 root password SSH 允许及若干无监听旧端口放行；后续 key-only、精确 UFW 变更、新 SSH 会话和防锁死回滚验证尚待实际执行收据。自 10 月 22 日读取的 6,012 行 SSH 日志中 accepted password 为 0、failed password 为 446，不能把没有成功口令记录当成不需加固。

05:07 的 SSH / UFW 收据已接续上段 04:55 待办；新 Bot 正式切换、独立快照与同机恢复、新 full plan 全备完成、旧面板退役与维护重启均已取得上方实际收据。当前仍保留本轮云端 age 解密 / 异机启动、真人验收与两项上游 CVE 边界；候选探针、短 startup 样本和版本未匹配均不能代签这些门。

本轮没有发布 Homepage / OMS 页面、改业务库内容、改 TLS 续期或提升 OMS 产品阶段。OMS 继续 **已部署待真人验收**，原账号 / 下载 / 桌面 / P-C 等剩余门只取 [现行真人验收](production-maintenance.md#真人验收)。双站 HTTPS 根页 200 不签实际续期；备份 timer 恢复不签新全备；受控脚本不签 QQ 真人收发。
