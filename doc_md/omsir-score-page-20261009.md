# OMSIR 成绩页与客户端选项（2026-10-09）

## 实施与来源

2026-10-09 22:17:27 CST，生产切入 `a85aee3e3c45-b17354d27c6b`：Backend `a85aee3e3c45d2358feef986f04beff00ed6ad8f` / Web `b17354d27c6b5c50170a88aa35497592fdf6d502`。状态仍为已部署待验收；本轮完成软件、本地浏览器与公开 HTTP，没有签收真实客户端游玩、账号切换、两端对照或 P/C，也没有生成 Windows 发行物。

用户要求从旧 LR2IR 继承基底成绩，统一作为 OMSIR 榜单呈现。网页显示实际客户端；已知 LR2 与其他客户端并列，旧摘要仅在玩家名旁附低调「旧库」。SBMP / 空客户端标记收在展开项，默认仍包括原完整范围；原八个 API source、空选、原子链接和全选 / 清空语义不变。经典 LR2 当前没有实时上传插件；LR2oraja / OpenLR2 是独立客户端，不能把旧库 LR2 写成已实现的实时接入。

未确认 SBMP 的客户端身份，没有删除或隔离这些原记录。归档[固定解析源码](https://github.com/zkldi/lr2ir-dataset/blob/2cabd8972ebe072bcd7c420af1c9b653e8628e08/archive_parser/src/parsers/mod.rs#L195)只是读取最后单元格的 client 文本，不能据此证明对应可执行文件。旧全量来源计数保留原记录日期，本轮没有重读母库或改公开投影。

## 成绩显示

谱面 BMS / mania 榜采用榜首与本人摘要、紧凑成绩行：EX SCORE（mania 为总分）、ACC、玩家 / 客户端、最大连击、六类判定、时间、Mod / Option 与原位置详情。BMS ACC 为 EX / 最大 EX，原 OMS Accuracy 独立保留；未知 EP、连击或时间显示「—」，不补零。mania 使用实际总分 / Accuracy 与 Perfect、Great、Good、OK、MEH、MISS。

Backend 只为胜出分数增加展示字段，统计、选项来自同一最高 EX 观察；独立最佳灯仍单独查询，不能与最佳 EX 的判定拼成同一局。原身份、完整范围 RANK、分页、人数、条件、cookie、私有历史与公开隐藏不改。PG / GR / GD / BD / PR / EP 的各源语义、空 POOR 差异和稀疏 OMS 映射取[正式合同](../../../oms-server/dev_bridge_md/doc_md/subline/oms-ir/multisource-contract.md#成绩展示字段2026-10-09)。

共同视觉使用 MR、RD、R-RD、S-RD、左右侧、FLIP 和血条标签，保留实际原值 / 提示。Java option=1P+10×2P+100×FLIP；Java 3 为 R-RANDOM，OpenLR2 3 为 S-RANDOM。未知旧 OP 保留原文本与槽位，只对有依据的词作别名；不从位置推导血条、随机或资格。显示归一不证明判定 / 血条数值等价，也不扩张 OMS 后端当前受理的 Mod。

帮助 / 下载页提供三份 Java JAR、OpenLR2 x64 / x86 DLL、专用密钥与详细设置。OpenLR2 须关闭程序、保全现有配置并选择 `network/display_ir=OMS IR (OpenLR2 v260915)`；模板为 `/omsir-openlr2.example.json`，无需额外 zlib DLL。接口与五个实际插件文件已提供，固定版本真实宿主仍待；完整来源链为[新来源快照](../../../oms-server/oms_client_bridge_md/doc_md/other/oms-ir-score-display-snapshot-20261009.md) → Client Bridge 事实登记 → Dev Bridge 合同 → 本仓与 Backend。

共享客户端筛选同时作用于个人成绩等实际消费者；此前 Zris 56 表 / 表内等级 / 曲名排序、玩家榜、谱面头部与其他已授权审改保留。

## 本轮验证

- Backend `tests/test_multisource.py`：19/19，通过最高 EX 与独立灯、稀疏判定、原 Accuracy / EX rate、缺失档案值等行为用例；既有 httpx 弃用警告保留。
- 前端类型检查、真实生产 webpack 编译通过，15 个选项用例通过；编译输入绑定 `e72d5df04808978d8b563a3cd64104bef6317abd`，后续模板 / 安装器提交未改变 214 项编译输入。480 件编译资源指纹留 F；三项上游资源大小提示保留。
- 本地实际 API 68 项与页面 / 资源 / 插件 / 模板 32 项通过。实际浏览器检查 BMS、mania、本人、原位置展开、空选 / 全选；1280 桌面和 390 窄屏截图留 F。390 视口下 document 375px、容器 355px、表自身滚动 900px，页面未撑宽。
- 生产发布前31项 / 发布后39项成绩检查通过，去除新增展示字段与读取时间后，所有实际来源范围、653人、原名 / ID、EX / 灯 / 原选项 / 名次 / 分页与发布前完全一致。生产完整页面、全部资源指纹、八件批准插件 / 许可、对应源码逐文件、配置模板和双站 TLS 共34项通过。没有在生产创建测试账号或成绩。
- 生产浏览器单次25秒取景超时，未获得本轮线上视觉截图；本地截图不是生产真人证明。本轮有限资源窗仅12次公开读取、最多两个并行 reader，时长 0.568 秒，不刷新2026-10-08持续运行 / 压力 / 恢复证据。

## 发布、配置、备份与回退

完整发布包74,324,070 B，SHA256 `34d87e6cf49569ef3900da4f72d6db5158f73a4e18eb1a56d808e26331594715`，保全在本仓 F 盘 ignored `artifacts/score-page-normalization-20261009/package/`。依赖、五插件 / 许可、schema3、22表与公开投影不变；Backend 应用仅 `multisource.py` 变动，另将已提交的维护查询 `multisource_probe.py` 随包带入。所有既有未提交工作未打入生产。

安装在128MiB / CPU50% / swap0限额中完成。精确同 SHA / regular / 0644 的旧不可变文件以硬链接复用100,266,758 B；变化文件29,750,769 B为独立新 inode，venv独立生成。实际安装循环已在独立fixture检查新旧 inode、字节与权限；未写穿旧发布。

前后12件完整配置在 `production-private/before` 与 `after`。IR unit 从相对 current 改为新不可变包的精确路径后重启，实际新 PID `3509802` / 原限制500MiB、CPU150%；catalog原PID `1862556` 不重启。两Web unit换新包 / 独立正式缓存，OMS include换对应资源目录；实际CLI缓存、FPM及BT Nginx检查 / 重载通过。其余配置与共享 Homepage 绑定保持字节不变。

初次激活在任何写配置前因 IR unit 原来使用 `/opt/oms-ir/current` 而非固定 B0 字符串被断言阻止，原失败保留；改为显式绑定新包后成功。公网检查随后发现模板404，单独增加 exact-location JSON 路由、重新BT检查 / 重载与全件HTTP验证。仓内配置生成器同步此路由；它是运维生成器增量，当前应用不可变包与对应源码仍绑定上述 b173 / a85，不能据文档或后续HEAD重标运行提交。

发布前后各一次固定 D1/22b helper新鲜完整gzip / 完成sidecar，F外取后全部解压，完整指纹、22表 /18索引 /8触发器、FK /完整性 /schema核对通过。原业务DB dev=64771、inode=265517保持；没有迁移、恢复覆盖或母库修改。维护timer恢复 enabled / active / waiting；收尾下一触发 `2026-10-10 04:18:19 CST`，终态不可读的缓存 / 备份峰保留null。

有限窗内可用内存最低 822,222,848 B，swap0；FPM采样最大 50,405,376 B / cgroup实际峰 74,440,704 B，IR采样最大 62,836,736 B / 实际峰 111,927,296 B，原预算未增加，两服务无重启或OOM。catalog保持96MiB / CPU25%，缓存 / 备份128MiB / CPU50%。

完整F包与远端SHA复核后，仅移除本任务incoming重复gzip。收尾空闲 4,545,056,768 B，沿2026-10-08最大raw＋八对备份＋额外2GiB保守预留 4,402,384,384 B，余 142,672,384 B。当前、479直接回退、FFF、更早B0与D1固定维护 / 旧设计均保留，没有为本轮删除运行包或玩家数据。

当前同库直接回退为 `b879e4233818-479987991a9b / production-r1`：先新鲜备份与完整配置保全，再恢复本轮before的两Web unit、IR unit与OMS include，切current到479、daemon-reload、BT检查 / 重载、生成旧正式缓存并重启IR / FPM，核公开范围 / 双站 / 预算。保留当下数据库和新内容，不能回灌旧raw；本轮没有实际往返验证。精确步骤取[维护说明](production-maintenance.md)，共享配置同步[Homepage](../../homepage-website/doc_md/other/oms-score-display-20261009.md)和[旧Website](../../oms-website/doc_md/other/oms-score-display-20261009.md)。
