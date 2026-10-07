# OMS Web 本地使用与恢复

本说明适用于 2026-10-07 原版 osu-web 迁移的本地工作区。玩家可以在 [本地网站](http://127.0.0.1:8090/) 验收原 Laravel / Blade / React / Less / Turbo 页面接入 OMS 的效果。本轮没有替换线上网站，线上账号和成绩也没有迁入本地测试库。

本地可运行、软件检查、资源测量、恢复验证和真人认可分别记录。性能及两次空目录恢复的实际结果取 [迁移记录](oms-web-migration-20261007.md)；本文的命令是维护步骤，不能单凭执行示例签收。用户视觉认可、实际下载入库、网页与 OMS 一致性及目标播放器验收仍须真人完成。

## 本地运行范围

| 项目 | 当前位置或范围 |
| --- | --- |
| 网站源码 | `F:/zdamexy-workspace/websites/oms-web`，`main`，保留完整上游历史 |
| 运行环境 | 专用 WSL `oms-web-dev`，Alpine 3.24.2；VHD 位于 `F:/zdamexy-workspace/websites/oms-web/.dev-cache/wsl` |
| 工具版本 | PHP 8.5.11、WSL Node 24.18.1、Python 3.14.8、Nginx 1.30.4、SQLite 3.53.4；变更后须重新恢复验证 |
| 玩家网页 | Nginx `127.0.0.1:8090`；PHP-FPM 只监听 `127.0.0.1:9070` |
| 本地 API / 目录 worker | `127.0.0.1:8081` / `127.0.0.1:8082`，只使用本任务测试库 |
| 活跃测试数据 | 网站 `.dev-cache/local-runtime/live.db`；账号、OMS UUID 记录、外部最佳状态与社区写入都在此库 |
| 公开历史 | 固定只读引用 `F:/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db` |
| 日志 / 检查证据 | 网站 `artifacts/`；临时状态和缓存在 `.dev-cache/` |

本地环境不访问 LR2IR 母库或其他私有数据库；只挂载已授权的完整公开投影。恢复包不复制该投影，恢复时仍需要原固定文件。读取范围和投影完整性由实际检查报告证明，不能用样例成绩或旧十万条合成容量结果代替。

游戏仍默认离线，只有玩家主动使用 IR 或浏览下载时按需请求。本地新站没有聊天、presence、多人、谱包/回放托管、PP 或地力功能。当前本地 Node 使用 24；不能据此声称上游 Node 22 或生产主机已经通过。

## 启动、停止与维护

每个新 PowerShell 的开发命令先执行绝对路径存储入口。以下命令在 Windows PowerShell 中运行：

```powershell
. F:/zdamexy-workspace/websites/oms-web/UseDevelopmentStorage.ps1
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web -- bash scripts/local-runtime.sh start
```

启动入口是 [local-runtime.sh](../scripts/local-runtime.sh)。它使用本地测试库和既有公开投影，生成本工作区的 Nginx / PHP-FPM 配置，启动自身的四个服务。已有活跃进程时会拒绝重复启动；缺少真实资源 manifest、Python 环境或公开投影时也会失败。启动错误会尝试停止本次自己的进程，不能把部分启动当作网站可用。

每次启动先清除并重新编译当前目录的 Blade 与配置缓存，随后进行一次实际本地页面和适配器检查，全部通过才显示 ready。报告位于 `artifacts/startup-warm-*.json`，不轮询、不请求第三方。运行时关闭 PHP / Blade 的逐请求文件时间检查；修改 PHP、模板或配置后须停止并重新启动。修改前端后先重新构建再重启，普通浏览器刷新不能替代这些步骤。HTML 始终要求重新验证，带内容 hash 的资源可以长期缓存。

```powershell
. F:/zdamexy-workspace/websites/oms-web/UseDevelopmentStorage.ps1
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web -- bash scripts/local-runtime.sh stop
```

停止入口按工作区 PID 文件及进程命令行核对归属，发送 SIGTERM 并等待自己的进程退出。它不删除测试库或缓存，也不停止其他 WSL 分发或服务。停止失败先保留日志与数据诊断，不用全局 `killall` 或 `wsl --shutdown` 代替本任务的停止。

Nginx / PHP-FPM 正常退出会自行移除 PID 文件，不能把停止后的缺失文件判成服务故障。收尾需核对运行实例的实际归属和已停止目录没有残留进程，不凭 PID 文件单独推定存活。

主要日志为 `artifacts/nginx-error.log`、`php-fpm.log`、`php-errors.log`、`local-backend.log`、`local-catalog.log` 及 `storage/logs/laravel.log`。记录失败的页面、操作、发生时间和日志位置；不要把密码、cookie 或一次显示的接入秘密放入公开反馈。

构建、类型检查、安装和格式化由主执行者串行安排，检查期间冻结对应源码。恢复包包含当次 `vendor`、实际 `public/assets`、后端 venv 与适配器资源，恢复本身不重新安装依赖、不生成假 manifest。若必须重建，按 `composer.lock` / `package-lock.json` 与后端锁定依赖重建并重新检查；不能使用旧资源证明新源码，也不以 `--ignore-platform-reqs`、`--force`、忽略类型错误或临时换版本绕过失败。

现存 WSL 中的网页依赖重建入口是 `bash build.sh`，串行执行 Composer 无 dev 安装、npm ci、类型检查、生产资源与 Blade 编译；随后重新启动运行入口。需要 PHP 8.5 及其 intl、mbstring、curl、dom、fileinfo、iconv、openssl、pdo、phar、session、tokenizer、xml、xmlwriter、zip 扩展，Composer 2、Node 24 / npm、Nginx、Bash 与 Git。当前已有 Alpine 官方包提供这些工具，不需要上游 MySQL、Redis、ES 或 Docker。

后端不安装为另一份产品，运行入口通过相邻目录的 PYTHONPATH 使用源码。其依赖从相邻后端 `uv.lock` 导出带 hash 的 requirements，再在 F-backed Alpine 的本工作区 venv 中安装。下面是环境缺失时的重建方法，不是已执行的新系统恢复证明；需先保全运行数据、停止本地服务并安排串行检查：

```powershell
. F:/zdamexy-workspace/websites/oms-web/UseDevelopmentStorage.ps1
$env:UV_CACHE_DIR = 'F:/zdamexy-workspace/websites/oms-web/.dev-cache/uv'
uv export --project F:/zdamexy-workspace/oms-server/oms-backend --frozen --no-dev --extra test --no-emit-project --output-file F:/zdamexy-workspace/websites/oms-web/.dev-cache/temp/backend-requirements.txt
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web --exec env TMPDIR=/mnt/f/zdamexy-workspace/websites/oms-web/.dev-cache/temp PYTHONDONTWRITEBYTECODE=1 python3 -m venv .dev-cache/backend-venv
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web --exec env TMPDIR=/mnt/f/zdamexy-workspace/websites/oms-web/.dev-cache/temp PYTHONDONTWRITEBYTECODE=1 .dev-cache/backend-venv/bin/python -m pip install --require-hashes --cache-dir .dev-cache/pip -r .dev-cache/temp/backend-requirements.txt
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web -- bash build.sh
```

新 Git checkout 不含运行库、公开投影或适配器二进制，不能只 clone 后声称可启动。当前完整运行资源由 F 盘快照保全；重新取得适配器时，只放入 `versions.json` 指定的八个实际文件，核对来源、许可和 SHA，不换宿主版本。新系统环境、依赖更新或固定公开投影路径变化另行建恢复批次与证据，不复用旧成功标志。

运行环境或工具版本变更会使当前“同一现存 WSL”恢复不再成立，须重新建立并验证恢复方案。现脚本不负责安装 Alpine、PHP、Node、Python、Nginx 或系统库，也不是 Windows / WSL 重装备份。

## 真人验收路径

使用本地注册的账号与本地接入密钥。测试账号、上传和帖子不会同步到生产；公开 LR2IR 历史只读。桌面和窄屏均应走下列路径，并记录失败步骤与反馈：

| 入口 | 玩家实际检查 |
| --- | --- |
| `/`、`/news`、新闻固定地址 | 首页有真实新闻与实际入口；文章、返回首页、导航和窄屏菜单正常；普通刷新能取得新页面 |
| `/download`、`/help` | 公开发行、启动/添加谱库步骤与开发状态准确；旧 `/#download` 能到独立下载页 |
| `/beatmapsets?ruleset=bms` | 分别搜索 Ginger Rush 与 616；打开实际 MD5 详情，检查来源资格与未知信息，主动下载由原站提供的包，在 OMS 添加谱库后确认实际谱面 |
| `/beatmapsets?ruleset=mania` | 使用 Sayobot 查询真实 mania 集合、详情和实际下载；混合包只导入原生 mania，缺失原 `.osu` MD5 时不伪关联榜单 |
| `/ir`、`/ir?md5=实际MD5` | 搜索标题/作者/MD5、首末页及无结果；历史详情能独立打开，不因 Ginger/616 失败而丢失榜单；人数和总量来自完整公开范围 |
| 谱面内参考混榜与同条件 | 一个、多个、全部、空来源选择分别影响最佳分、独立灯、人数、排名和分页；切到服务已证明的条件后仍按全范围排名，未知来源/条件/原灯与 LR2IR 旧身份如实展示 |
| `/users/实际OMS账号ID` | 登录自己的新账号、查看他人公开页；BMS/mania、来源、条件、公开最佳和近期最佳更新语义准确；不按同名合并历史身份，不显示虚构 PP、等级或逐局历史 |
| 本人个人页 `?section=history` | “我的完整记录”只向本人开放，逐局显示 OMS BMS / mania 的真实 UUID、游玩/接收时间与完整原条件；包括非公开记录，不受公开来源/键型/条件筛选影响，不混入外部状态和历史摘要 |
| `/account` | 原登录弹窗、注册、退出、换账号及跨标签切换；创建来源密钥仅显示一次秘密，原账号归属保留，撤销后真实交分被拒绝；迟到回应不泄露旧私有记录/秘密 |
| `/community`、新帖与实际帖子地址 | 发表/回复/编辑/删除自己的纯文本内容，安全链接及换行正常；重试保留原 UUID 与账号，换号后明确处理草稿归属；他人的管理入口不可用 |
| `/rankings`、`/credits` | 玩家榜仅提供现有真实来源/范围及指标，条件选择、分页、本人的位置准确；许可和修改源码入口可达 |

旧 `/ir/#history` 进入本人完整记录；未登录先到 `/account?section=history`，登录后使用“我的完整记录”链接。旧 `/ir/#keys` 进入账号页。当前没有成绩删除接口，网站不提供虚构的删除记录操作。

网页验证须与真实 OMS 上传和读榜核对。同一 MD5、来源、条件、页码下，两端应显示一致的参考榜和同条件榜；账号切换不能接管旧待交内容或改变保存后的 UUID。客户端日常验收仍由用户通过 VS Code 非调试启动当前 `F:/oms`，主动使用已有按需 IR 设置；默认 endpoint 不改。本任务无需生成 Windows 发行包、`publish` 或额外安装副本。外部宿主真实交分与原生读榜及 P/C 其他真人门沿原专项继续记录，不能用网页或接口检查代签。

## 本地快照与两次空目录恢复

恢复脚本仅处理本任务的测试数据。源码、运行依赖、测试库一致快照和测试登录状态有不同用途：

- Git 保存可公开的修改源码与许可；不保存运行数据库、恢复 tar、个人行或秘密。
- [snapshot-local.py](../scripts/snapshot-local.py) 只从明确源码清单和运行目录取文件，使用 SQLite 一致备份 API 生成独立 `live.db`，保全已提交到 WAL 的状态，不直接复制运行中主库冒充备份。要求 SQLite 至少 3.51.3、当前 schema 3、至少两个实际本地测试账号与齐全运行目录。
- 输出固定在网站 `artifacts/local-recovery/`，每轮保留 `r1` / `r2` 的 `local-runtime.tar`、`source-manifest.json` 和数据库快照。manifest 记录实际工作区字节、文件 SHA、工具版本和捕获方法；其 Git HEAD 只是来源信息，不表示未提交字节已提交。
- 本地验收状态含测试密码和撤销密钥的秘密，单独保留在 F 盘受保护文件；不进入 tar、Git 或公开报告。每轮状态须对应当次快照，不能用另一轮状态补签。
- 快照不含 Git 元数据、`.env` 凭据、`node_modules`、日志/PID/生成服务配置、其他数据库、投影字节或母库。Git 全历史另由当前仓库及 Git 归档保全。

在 Windows 创建状态或归档前，实际 NTFS 权限必须只允许当前所有者和 SYSTEM，不能用 WSL 的 chmod 代替。当前 `.dev-cache/local-runtime`、`artifacts/local-recovery` 以及两恢复目标的专用父目录均已设置此边界，子文件继承，实际证据为 `artifacts/recovery-acl*.json`。新批次先在明确的 F 盘位置创建专用空父目录并限制权限，再把不存在的恢复目标放在其内；不复用混有其他数据的父目录或扩宽权限。

以下是主执行者在尚未存在 `r1` 的新恢复批次使用的流程。若已有结果，先读取并沿用实际证据；脚本拒绝覆盖已存在的轮次或目标，包括失败的半成品。示例中的新目标父目录须已存在、直接位于 F、无符号链接，目标自身须不存在。

先完成实际 `verify-local.py` 检查，得到隔离账号对应的 `acceptance-state.json`。停止其他测试写入、冻结源码，再使用 [prepare-recovery.py](../scripts/prepare-recovery.py)：它以实际浏览器 API 创建并撤销新的 ED 接入密钥，通过现有维护 CLI 隐藏独立测试帖子，保全一次秘密及每轮状态，然后调用 SQLite 快照入口。没有预备账号或已有相同轮次时会失败，不自动清空。

```powershell
. F:/zdamexy-workspace/websites/oms-web/UseDevelopmentStorage.ps1
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web -- .dev-cache/backend-venv/bin/python scripts/prepare-recovery.py --round r1 --with-reply
```

r1 捕获已提交的策略；r2 先核实实际 checkpoint 为 `(0,0,0)`，固定撤销前 / 隐藏前的读事务，并保持到快照子进程结束。随后要求快照入口实际证明主文件仍为旧状态、WAL 为新状态，备份中包含新撤销 / 隐藏。不能只添加 `--require-wal-policy-delta` 参数来代替这些证据。每轮状态是 `.dev-cache/local-runtime/recovery-state-r1.json` 或 `recovery-state-r2.json`，与原验收状态分别保存。

每次 snapshot 会把最新一轮的 manifest / tar 以同盘硬链接发布到固定 `artifacts/local-recovery/` 基目录，保留 `r1` / `r2` 原件。`restore-local.mjs` 只接受此基目录，不能传 `.../r1` 或 `.../r2`；因此先完成 r1 的恢复与验证，再捕获 r2。不要把当前指向 r2 的输入标记为 r1。

```powershell
. F:/zdamexy-workspace/websites/oms-web/UseDevelopmentStorage.ps1
$OmsRecoveryBackup = '/mnt/f/zdamexy-workspace/websites/oms-web/artifacts/local-recovery'
$OmsFreshRecovery = '/mnt/f/oms/artifacts/oms-web-migration-20261007/local-native-restores/local-restore-r1-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web -- node scripts/restore-local.mjs $OmsRecoveryBackup $OmsFreshRecovery
```

[restore-local.mjs](../scripts/restore-local.mjs) 检查完整归档 SHA、路径与文件集合，保留并核对允许的符号链接，逐文件核 SHA，检查资源 manifest 和 SQLite 完整性。Alpine / PHP / Python / Node / Nginx 版本须匹配快照；后续 HTTP 门还核 SQLite 精确版本。恢复输出保持 `websites/oms-web` 与 `oms-server/oms-backend` 的相邻目录关系，并生成 `restoration-report.json`。

恢复脚本不会启动 HTTP。文件/SQLite 报告成功后，先停止原工作区的本地运行，再启动新目标；这些实例共用 loopback 端口，不能同时运行：

```powershell
. F:/zdamexy-workspace/websites/oms-web/UseDevelopmentStorage.ps1
# 同一 shell 沿用上面已确定的新目标；新 shell 须填入该实际绝对路径。
wsl -d oms-web-dev --cd /mnt/f/zdamexy-workspace/websites/oms-web -- bash scripts/local-runtime.sh stop
wsl -d oms-web-dev --cd ($OmsFreshRecovery + '/websites/oms-web') -- bash scripts/local-runtime.sh start
wsl -d oms-web-dev --cd ($OmsFreshRecovery + '/websites/oms-web') -- .dev-cache/backend-venv/bin/python scripts/verify-restored.py --restore-root $OmsFreshRecovery --acceptance-state /mnt/f/zdamexy-workspace/websites/oms-web/.dev-cache/local-runtime/recovery-state-r1.json --round r1
```

[verify-restored.py](../scripts/verify-restored.py) 对实际恢复实例核验进程归属、账号权限、完整私人 UUID 记录、公开投影与全范围混榜、独立灯/条件、密钥撤销和帖子隐藏，以及页面/资源/适配器的实际 HTTP 字节。它使用本地测试账号登录、重交已有 UUID 并退出，会改变测试会话，不能指向生产。默认报告为新目标的 `artifacts/recovery-http-r1.json`，已存在的报告不会覆盖；进入验证后的失败也保存报告。入口预检查失败可能尚未生成报告，保留错误输出并诊断，不能据缺少报告推定成功。

随后用新目标自己的 `local-runtime.sh stop` 停止该实例。若继续 r2，恢复原任务实例，运行 `prepare-recovery.py --round r2 --with-reply`，选择另一个新空目标，再按同样顺序启动并用 `--round r2` 与 `recovery-state-r2.json` 验证。每轮均须有文件/SQLite 与实际 HTTP 证据；成功标志、时间、SHA 和未完成项由主执行者填入迁移记录。两个目标都在同一个已安装 Alpine WSL 中，不能描述为两次 OS 重装或断网重装成功。

任何失败均保留原快照、受保护状态、恢复目标与报告；不清空后重试、不重新标记旧失败为成功。需要下一批验证时由主执行者明确建立新批次范围并调整入口，避免覆盖固定 r1/r2 证据。

## 旧设计保全与后续回退

旧设计存档位于 `F:/oms/artifacts/oms-web-migration-20261007/legacy-r3`，没有在资源受限的服务器上另建备份。组成包括 `legacy.bundle` 全历史、当前工作区实际字节与差异/状态、原介绍页/已发布源码/捕获 HEAD 的独立归档、原发布运行包，以及相应 SHA 和恢复报告。原介绍页的历史取证提交不代表当前源码或生产版本。

原 Google Fonts 是外部资源，另存 `offline-fonts/` 的公开字体、许可、CSS 和取得时间；离线旧介绍页在 `restore-original-offline/`。这是当次重新取得的公开字体，不证明历史上线时字节完全相同。原存档不改写，字体及离线版的证据见各自报告；文件核对不代签实际视觉效果。

用户已通过“效果很好，那部署？”授权替换生产。切换前继续保全原设计与当前发布版本于 F 盘，并从新空目录恢复；核对实际共享主机预算、完整范围查询和回退路径。实际切换状态以[生产记录](production-deployment-20261007.md)为准，本地脚本的成功不代表上线。

设计回退只替换网站与已确认兼容的服务资源，继续使用同一个当前账号、成绩、来源资格、隐藏/撤销状态与社区权威库。数据备份/灾难恢复另行处理；不得把本文的测试 snapshot 或旧生产数据库覆盖后来新增的用户数据。备份与秘密存放在受保护的 F 盘范围，公开仓仅保留源码、说明和脱敏结果。
