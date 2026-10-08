# OMS Web

OMS 的 BMS / mania 玩家网站，从 [ppy/osu-web](https://github.com/ppy/osu-web) 原项目接续，保留上游历史和 Laravel / Blade / React / Less / Turbo 页面组织。现 OMS 服务继续维护账号、成绩、目录与社区。

2026-10-08 原版[官网](https://oms.zdamexy.work/)已上线，当前为**已部署待验收**。本地视觉已获认可；玩家范围取 [OMS.md](OMS.md)，线上真人验收、准确运行来源与维护取[生产维护](doc_md/production-maintenance.md)。

- [来源与状态](OMS.md)
- [本地启动、验收与恢复](doc_md/local-use-and-recovery.md)
- [线上维护、备份、回退与真人验收](doc_md/production-maintenance.md)
- [新闻维护](doc_md/production-maintenance.md#新闻与内容维护)
- [迁移与实际证据](doc_md/oms-web-migration-20261007.md)
- [协作入口](AGENTS.md)

开发和恢复使用 F 盘专用 Alpine WSL。每个开发 shell 先执行 `UseDevelopmentStorage.ps1`；不使用上游的数据库迁移、部署或全套后台启动步骤。依赖和实际启动命令见本地说明。

初始上游为 `2c596022a1345fbed288978e7fa5304df0359f50`。原上游说明逐字节保存于 [UPSTREAM_README.md](UPSTREAM_README.md)，仅作原项目来源；其安装及部署步骤不适用于本裁剪版本。

源码沿 [GNU AGPL v3](LICENCE) 提供，保留原作者归属。当前字体为 Inter 与 Font Awesome；实际依赖、许可和修改说明见[源码与许可页](https://oms.zdamexy.work/credits)。本项目与 osu! / ppy 的官方服务无隶属关系。
