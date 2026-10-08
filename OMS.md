# OMS Web

本仓是从 [ppy/osu-web](https://github.com/ppy/osu-web) 原项目接续的 OMS 玩家网站。原说明逐字节保留在 [UPSTREAM_README.md](UPSTREAM_README.md)，上游历史和许可保留；OMS 适配在原页面与构建组织中进行。

2026-10-07 用户提供 `https://github.com/ZDaMexy/oms-web.git` 并确认开始本地实施，暂不部署。初始基线 `2c596022a1345fbed288978e7fa5304df0359f50`；在线上游 master 当次为 `a09a1750e9a1fc47e0f3e266edbcda9de3f29ed1`，不因取得新 HEAD 自动同步未经审查改动。

当前为**已部署待验收**。用户随后反馈“效果很好，那部署？”，确认本地视觉并授权部署；2026-10-08实际最终切入原版包 `b879e4233818-b0feceae22e4`。玩家可在[官网](https://oms.zdamexy.work/)浏览新闻和BMS / mania目录、查完整历史参考混榜并筛选来源、使用同一套OMS账号的个人页与社区。没有伪造PP、地力、逐局历史或在线人数。

本地入口为 [127.0.0.1:8090](http://127.0.0.1:8090/)。这是隔离测试库，线上账号和成绩未迁入；只读历史来自已批准的完整公开投影，母库不访问。实际浏览器、软件检查、持续资源测量与两轮恢复分别取 [迁移记录](doc_md/oms-web-migration-20261007.md)。启动停止与真人路径见 [本地说明](doc_md/local-use-and-recovery.md)。

本地视觉已获用户认可，实际下载入库、真实账号 / 密钥、OMS对照和固定播放器P/C仍待验收。此前静态 `oms-frontend` 原设计及完整历史只作保全 / 回退来源；本次正式运行、完整恢复、容量、正式备份与公网上线另有实际证据，取[生产记录](doc_md/production-deployment-20261007.md#正式发布与收尾)，运维和验收取[维护说明](doc_md/production-maintenance.md)。本地证据保留原日期与范围，不提升为生产通过。
