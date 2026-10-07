# OMS Web

OMS 的 BMS / mania 玩家网站，从 [ppy/osu-web](https://github.com/ppy/osu-web) 原项目接续，保留上游历史和 Laravel / Blade / React / Less / Turbo 页面组织。现 OMS 服务继续维护账号、成绩、目录与社区。

2026-10-07 当前为**本地视觉已确认，生产部署进行中**。用户反馈“效果很好，那部署？”，认可本地效果并授权部署；新站生产切换及运行、资源、恢复与公开核验尚未记录完成。玩家可在 [本地入口](http://127.0.0.1:8090/) 查看新闻、浏览谱面、筛选跨来源榜、登录查看个人记录并使用社区。真实下载入库、账号 / 客户端及指定播放器 P/C 仍待验收。没有 PP、地力、聊天、在线状态、支付或谱包托管。

- [来源与状态](OMS.md)
- [本地启动、验收与恢复](doc_md/local-use-and-recovery.md)
- [迁移与实际证据](doc_md/oms-web-migration-20261007.md)
- [协作入口](AGENTS.md)

开发和恢复使用 F 盘专用 Alpine WSL。每个开发 shell 先执行 `UseDevelopmentStorage.ps1`；不使用上游的数据库迁移、部署或全套后台启动步骤。依赖和实际启动命令见本地说明。

初始上游为 `2c596022a1345fbed288978e7fa5304df0359f50`。原上游说明逐字节保存于 [UPSTREAM_README.md](UPSTREAM_README.md)，仅作原项目来源；其安装及部署步骤不适用于本裁剪版本。

源码沿 [GNU AGPL v3](LICENCE) 提供，保留原作者归属。当前字体为 Inter 与 Font Awesome；实际依赖、许可和修改说明见 [源码与许可页](http://127.0.0.1:8090/credits)。本项目与 osu! / ppy 的官方服务无隶属关系。
