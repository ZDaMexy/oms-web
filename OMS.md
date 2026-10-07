# OMS Web

本仓是从 [ppy/osu-web](https://github.com/ppy/osu-web) 原项目接续的 OMS 玩家网站。原说明逐字节保留在 [UPSTREAM_README.md](UPSTREAM_README.md)，上游历史和许可保留；OMS 适配在原页面与构建组织中进行。

2026-10-07 用户提供 `https://github.com/ZDaMexy/oms-web.git` 并确认开始本地实施，暂不部署。初始基线 `2c596022a1345fbed288978e7fa5304df0359f50`；在线上游 master 当次为 `a09a1750e9a1fc47e0f3e266edbcda9de3f29ed1`，不因取得新 HEAD 自动同步未经审查改动。

当前为**本地运行待验收，未部署**。玩家已能浏览新闻和 BMS / mania 目录、查完整历史混榜并筛选来源、使用同一套 OMS 账号的个人页与社区。没有伪造 PP、地力、逐局历史或在线人数。

本地入口为 [127.0.0.1:8090](http://127.0.0.1:8090/)。这是隔离测试库，线上账号和成绩未迁入；只读历史来自已批准的完整公开投影，母库不访问。实际浏览器、软件检查、持续资源测量与两轮恢复分别取 [迁移记录](doc_md/oms-web-migration-20261007.md)。启动停止与真人路径见 [本地说明](doc_md/local-use-and-recovery.md)。

用户视觉认可、实际下载入库、真实账号 / 密钥、OMS 对照和固定播放器 P/C 仍待验收；现有官网仍由独立 `oms-frontend` 提供，先前生产“已部署待验收”与本地新仓不是同一版本。本轮不会替换线上。
