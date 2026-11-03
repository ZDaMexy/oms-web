# OMS 玩家服务：从查询到成绩与谱面

## 解决的问题

2026-11-04 接续用户对 Shiro 服务的复核要求。上版主要扩充图卡外观，玩家仍须知道数字 ID / MD5，个人成绩缺判定 / 连击，无法方便地选单曲、定位整榜名次或比较两人；mania 目录选难度后也没有原谱内容身份接到榜。单纯增加卡片不能解决这些路径。

本轮同时修改 Backend、当前 Web 和 Shiro；客户端保存字段已足够，静态来源为 master `ab58abd2135d540b445e2854ef933462d4ce8cb2`。采用 `client-ir-saved-result-details` / `client-bms-dj-level`，来源与限度见[Client Bridge 快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-player-service-fields-snapshot-20261104.md)。没有改动客户端源码、生成 Windows 包或提升旧真人门。

## 玩家现在能做什么

| 使用意图 | 数据与处理 | 入口 |
| --- | --- | --- |
| 找一个玩家 | 按 OMS 用户名字面搜索，沿原公开资格，候选有真实姓名和 ID | `/users`，Shiro 自然语言 |
| 找自己某首成绩 | 曲名 / 作者 / 难度、实际 MD5、条件筛选，按更新时间 / 分数 / BMS EX率排序，保留翻页 | 个人页最佳 / 最近更新，`oms_player` / `oms_score` |
| 看懂一次最佳 | 真实六类判定、连击、EX / 最大EX / EX率、DJ LEVEL 与目标差值，mania 总分 / accuracy / MAX:300 | 个人页直接显示要点，Shiro 单人成绩图 |
| 比较同一谱 | 同 MD5、规则、物量的两人原成绩与逐项判定差值；原分数灯和独立最佳灯分别保留 | Shiro 同谱对照图；可打开原榜 |
| 知道整榜位置 | Backend 完整候选先排名，`player` 定位独立于当前页，原 `me` 不改 | Shiro 指定玩家定位，网页原完整榜 |
| 从难度表找谱 | 真实表名 / 原等级 / 曲名检索，网页与 Bot 共用同一只读 manifest / 表数据 | `/ir`、`/ir/tables`、`oms_tables` |
| 找包后选难度再查榜 | Sayobot SID/BID 与原始 `.osu` 内容散列校验后，真实 MD5 接到 IR | mania 详情可切换具体难度；`oms_map` |
| 了解与取得谱面 | 实际键数、BPM、长度、音符 / 星数、来源和封面；原站下载链接 | 原详情 / 下载路径，Shiro 谱面图与原站入口 |

精确接口、资格与未知项只维护于[玩家 API](../../../oms-server/dev_bridge_md/doc_md/subline/oms-player-site/player-api.md#玩家查找与成绩详情2026-11-04)和[谱面 API](../../../oms-server/dev_bridge_md/doc_md/subline/oms-player-site/catalog-api.md#mania-原谱身份与共享难度表2026-11-04)。Backend 负责统计 / 排名 / 等级，Web 负责已有框架内的页面，Shiro 负责意图与表达，功能模块负责查询 / 对照 / 绘图。没有平行账号库、PP 算法或表数据副本。

## 从公开参考取舍

[雨沐固定来源 ad1c3d1](https://github.com/yumu-bot/yumu-image/tree/ad1c3d1c20f338cefe5cab94c91591f7b46e185f) 的 E5 单成绩、D3 玩家、J2 分析展示了成绩要服务于“看懂表现”，不是装饰数值。[osubot 固定来源 91015f6](https://github.com/yaowan233/nonebot-plugin-osubot/tree/91015f60f5a743344ed1459433856241011f9d54) 的公开 Agent 工具覆盖用户名解析、成绩 / 单谱、筛选、地图详情等实际路径；本轮据此补全查找、筛选、单曲与同谱对照的处理链。

OMS 没有已采用的 BMS PP / 地力规则、逐物件时间线或公开全部游玩历史。本轮使用实际已有数据完成成绩服务；不将公开最佳积累称作 BP/PP，不用最高 EX 记录的灯覆盖独立最佳灯，也不从 EX 差值编造具体技术病因。完整 UUID 历史仍需原本人认证，QQ 人物关系不能代替 OMS 认证。旧 LR2IR 身份只在原榜的 namespace 内，不按同名合并为 OMS 玩家。

设计由指定的 Local Codex / GPT-6.1 Sol / max 处理实际玩家流程，源稿与原生出图见[Shiro 设计](../../../Shiro-Agent/design/oms-player-services/README.md)。生产沿已有 Sharp / Pango / 固定字体，没有新增浏览器绘图服务。设计稿的合成玩家 / 成绩不进入生产数据。

## 本机证据与发布边界

实际运行来源与切换收据见下方[生产发布](#生产发布)，文档后续提交不重复部署代码。

本机真实 FastAPI / 合成账号串通了用户名→单曲→两人对照→整榜 player；实际 worker 输出两模式单人 / 对照、谱面与表内曲目图。Web 本机 Linux typecheck / 生产构建及 56 项 HTTP 检查通过，覆盖原登录、个人页、目录 / 榜、社区与内容入口；这些不代替普通浏览器交互或真人 QQ 使用。

原生 mania 公开网络样本 BID `3938188` / SID `1908399`（FREEDOM DiVE，4K）读取原 `.osu` 得到 MD5 `557247da54c661e876d501b688201417`、SHA256 `d516b56947c35207c2951305599e9328a8043b550230873bc326381dc25f0d41`。这是一个公开文件身份样本，不是全部目录验证或玩家成绩。

真实模型也使用合成账号 / 公开模型 API：最初暴露等级目标猜数和两模式判定混用，已通过功能模块的等级目标参数、明确标注的判定 / 差值修复。模型、资源、正式包与 QQ 边界的最新结果取[Shiro 进度](../../../Shiro-Agent/doc_md/mainline/progress.md)，Backend 最终软件结果取[其进度](../../../oms-server/oms-backend/doc_md/mainline/dev-progress.md)。

## 生产发布

**2026-11-04 05:18:59.648 CST**，OMS 切入 `fb2493cd7027-6dddd07312e4`：Backend `fb2493cd7027715f61c619ebb08e8b4c5d57f5c2`、Web `6dddd07312e4554269408318bb112e41dfd59090`，客户端字段来源仍为 ab58abd。原 `824de121a686-494932756b74` 保留为这次同 schema 回退，固定 D1/22b 日备份 helper 保持。数据库 device64771 / inode265517、schema3 / 22 表与结构指纹切前切后相同。主 IR / catalog / FPM 新 PID 92811 / 92810 / 92901，NRestarts=0；原受修复 Python / PHP、权限与安全配置保持。

正式包 74,023,644 B，SHA256 `474cd534460de01254a38f2560dd3cbeaabef3ef62c5b7e5af5a95bced96cb4b`，完整核对 9,688 项运行文件，运行目录已移除 web/scripts 工程脚本；对应源码压缩包按 AGPL 保留。491 编译文件与 294 份已提交构建输入绑定；曾因第三方 LICENSE 的 CRLF / LF 差异拒绝签收，还原提交原字节后重新构建通过，没有修改许可正文。

安装准备曾因服务器缓存缺当前锁定依赖而停止，业务未切换。本机按 uv.lock 下载并核 hash 的 Linux 生产 wheels 共20包 / 3,879,005 B；原生 Ubuntu 独立 Backend venv 的完整结果为 **486 passed / 16 skipped / 1 条既有提示**，应用运行文件与 fb2493c 相同，测试夹具补丁为 `37747bf`，仅将应私有的两个测试目录明确创建为0700。Windows完整结果487 passed / 15 skipped；两边 skip 与既有 age / 平台条件分别保留。解释器为公开固定3.12.16下载包的只读引用，不借 Shiro 的依赖环境。Web本机56项真实HTTP、typecheck / 生产构建、浏览器玩家查找 / 成绩布局与真实 mania 详情分别通过；发布器 Python 运行时9项通过，保留既有资源警告。

服务用已核验发布目录直接 `python -m oms_ir` 运行，安装 / 恢复只同步锁定生产依赖（`uv sync --frozen --no-dev --no-install-project`，离线时预备批准 wheels），不在服务器构建项目或安装 setuptools。该维护修正随后回写两个正式准备入口，不改变上述已部署应用文件。服务器新环境实测 Python3.12.16 / OpenSSL3.5.9 / SQLite3.53.1 / FastAPI0.139.2 / certifi2026.10.19。

公网只读复核：名字查找、表 manifest、通常表 ☆1 每页5条 / 总14条、真实 mania BID3938188 的 file-content MD5 和 client-content 均200；CSS完整SHA匹配新包，Homepage200且主PID保持。希洛随后于05:21:40.859 CST切入7c04a1d，准确产物 / 保持项取[其生产记录](../../../Shiro-Agent/doc_md/mainline/production.md#2026-11-04-oms-玩家服务发布)。没有以这些核对签收普通玩家账号、真实游玩或QQ自然聊天体验。

固定 helper 的前 / 后新鲜一致备份 Invocation 为 `f27faea95e8343d3955a840d5d394df7` / `e6198a500cd744d381c6a30c3a03da62`；gzip9,075 / 9,094 B，raw均241,664 B，F私有目录完整CRC / SHA / integrity / FK / schema / 22表核验通过。配置与激活收据为 `/var/backups/oms-maintenance/oms-player-services-20261104/`，本机操作 / 包证据在忽略的 `artifacts/oms-player-services-20261104/`；没有将生产资料用于QA。

单独回退希洛可消费当前OMS的兼容旧接口；若OMS退到824/494，先在空闲点将希洛退至5a3b109，再按本次配置原件成对回退四个OMS单元与Nginx路径，保留已修复Python/PHP及当前同一数据库。旧OMS没有新查人 / 详情接口，不能让7c04工具继续调用它；不回灌旧认知或数据库。

维护入口修正的补充验证：Backend发布来源 / 运行时39项及准备脚本bash语法通过，Web Python发布guard9项通过；应用文件和上述已发布来源保持。


### 云备份与发布清理

05:32:47.073 CST 全量云备份成功：46对象，新增密文212,201,925 B，上传后完整回读校验。目录密文SHA256为 `75985330e633a0b8cd5051e58e0f30f74d45653d820ea16ead777b60b054754c`，位于百度网盘 `/apps/OMS服务器备份/恢复目录/2026/11/04/oms-full-catalog-75985330e633a0b8cd5051e58e0f30f7.tar.gz.age`。新OMS代码对象源指纹为 `8b77c928e0d9f92196ec5992f6333c6ead6f962e6646cdaed9c2d495b2d82800`；Shiro新代码对象和必要配置亦已核验。认知 / 工作区目录仍不进入该历史备份，没有新增云端解密或异机重建验收。

05:34 在备份worker关闭后，核实旧Shiro6db6ca9的云对象、完整文件清单及进程 / FD / mmap无引用，退役其本机副本，保留7c04当前与5a3回退；旧代码仍可按原云对象恢复。OMS临时传输包、运行时压缩包、wheels及安装器一并移除；新OMS当前、824/494回退及固定D1/22b维护仍在。该次可用空间增加347,979,776 B；05:36只读复核根盘可用9,955,516,416 B，四业务服务PID保持、NRestarts=0，三backup timer active/waiting。

操作与云端脱敏收据保存在本机忽略目录，退休收据为服务器 `/var/backups/oms-maintenance/shiro-oms-player-20261104/retirement.json`。文档及维护入口后续提交不再次部署代码。
