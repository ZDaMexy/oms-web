# OMS Web

本仓是从 [ppy/osu-web](https://github.com/ppy/osu-web) 原项目接续的 OMS 玩家网站。原说明逐字节保留在 [UPSTREAM_README.md](UPSTREAM_README.md)，上游历史和许可保留；OMS 适配在原页面与构建组织中进行。

初始上游固定为 `2c596022a1345fbed288978e7fa5304df0359f50`；2026-10-07 授权、开工水位与当次在线查询见[迁移记录](doc_md/oms-web-migration-20261007.md#决定来源与当前状态)，不盲目同步上游。

2026-10-08 原版网站已上线，当前为**已部署待验收**。玩家可在[官网](https://oms.zdamexy.work/)浏览新闻和 BMS / mania 目录、查完整历史参考混榜并筛选来源、使用同一套 OMS 账号的个人页与社区。没有 PP、地力、在线人数、聊天或谱包托管；外部最佳状态与历史摘要不称逐局历史。

本地入口为 [127.0.0.1:8090](http://127.0.0.1:8090/)。这是隔离测试库，线上账号和成绩未迁入；只读历史来自已批准的完整公开投影，母库不访问。实际浏览器、软件检查、持续资源测量与两轮恢复分别取 [迁移记录](doc_md/oms-web-migration-20261007.md)。启动停止与真人路径见 [本地说明](doc_md/local-use-and-recovery.md)。

本地视觉已获用户认可；线上普通浏览器刷新、实际下载入库、真实账号 / 密钥、OMS 对照和固定播放器 P/C 仍待真人验收，具体路径取[维护说明](doc_md/production-maintenance.md#真人验收)。

当前运行、固定维护与同库回退的准确来源只取[维护说明](doc_md/production-maintenance.md#当前来源与运行位置)，实际发布、资源、恢复和备份证据取[生产记录](doc_md/production-deployment-20261007.md#正式发布与收尾)。旧静态 `oms-frontend` 设计及完整历史只作保全 / 回退来源；本地证据保留原日期与范围，不提升为生产通过。
