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

开发候选尚未发布；运行源码仍取[生产维护](production-maintenance.md#当前来源与运行位置)。本页不以文档 HEAD 表示已上线。

本机真实 FastAPI / 合成账号串通了用户名→单曲→两人对照→整榜 player；实际 worker 输出两模式单人 / 对照、谱面与表内曲目图。Web 本机 Linux typecheck / 生产构建及 56 项 HTTP 检查通过，覆盖原登录、个人页、目录 / 榜、社区与内容入口；这些不代替普通浏览器交互或真人 QQ 使用。

原生 mania 公开网络样本 BID `3938188` / SID `1908399`（FREEDOM DiVE，4K）读取原 `.osu` 得到 MD5 `557247da54c661e876d501b688201417`、SHA256 `d516b56947c35207c2951305599e9328a8043b550230873bc326381dc25f0d41`。这是一个公开文件身份样本，不是全部目录验证或玩家成绩。

真实模型也使用合成账号 / 公开模型 API：最初暴露等级目标猜数和两模式判定混用，已通过功能模块的等级目标参数、明确标注的判定 / 差值修复。模型、资源、正式包与 QQ 边界的最新结果取[Shiro 进度](../../../Shiro-Agent/doc_md/mainline/progress.md)，Backend 最终软件结果取[其进度](../../../oms-server/oms-backend/doc_md/mainline/dev-progress.md)。
