# 2026-10-09 谱面榜表内难度筛选

用户补充要求：选完难度表，还能选择该表的具体难度。2026-10-09 15:03:58 CST 已发布，产品继续为 **已部署待验收**；真人账号、下载入库、OMS对照与P/C没有因此签收。

## 页面与元数据

`/ir` 保留先选表的入口，在原表选择器后加入“难度”。选项来自当前整张表的真实标签和条目数，不随关键词、字母或页码缩短；数值等级按数值顺序排列，其他标签按自然顺序，未标注放最后。条目数不等于成绩人数或唯一MD5数。

通常表有☆1～☆13与X，发狂表有★1～★25与???，DPBMSと諸感保留10強等原标签；Hex的0不当作空值。Turbow的22条空字符串等级归入“未标注”，原条目字段和外部标签完整保留，没有改写成虚构等级。56个来源选项、149,943条冻结导航元数据继续取[上一轮来源记录](bms-difficulty-tables-20261009.md)，未重新抓取、增加后台worker或改客户端事实。

换表清除旧等级、字母、关键词并回到第一页；换难度回到第一页，保留当前字母和关键词。先按难度与搜索过滤，再算字母可选范围、应用字母和分页，曲名顺序继续来自完整表。单曲链接携带选中等级，返回该表时保留等级；同一MD5跨等级重复时，页面采用所选等级元数据。空结果给出调整难度、字母或关键词的提示。

查询语义、`levels`字段和错误状态只在[共同采用合同](../../../oms-server/dev_bridge_md/doc_md/subline/oms-player-site/catalog-api.md#表内难度筛选2026-10-09)完整维护。Backend账号、成绩、目录接口与schema3未改，成绩仍按原真实范围读取。

## 本轮验证与限制

- 最终运行代码为Web `6fbf7fd157d2f73cfff61093677a0a8d52bc66ea`。TypeScript、两件PHP语法检查与最终webpack构建通过；212件编译输入绑定462件实际输出，保留上游性能警告。早期47f构建和PHP修正后的输入重绑均保留原回执，最后未标注修正实际重新构建到6fb。
- 本地与公网各309项检查通过，分别覆盖全部56张表的完整等级选项、原表条目对照、等级先过滤再排序分页、通常表11的跨页与A组合、零结果、X / ??? / 10強 / 0 / 未标注、非法参数、SSR、单曲等级范围与重复MD5，以及当前散列资源。另33项公网原页面、插件 / 许可、全件对应源码、缓存与双站回归通过。
- 本地浏览器真实选择通常表☆11得到147项，下一页为2/3，换☆1回到1/1；A筛选得到2项，换☆11保留A得到7项。换发狂表清除旧等级和字母，选★???得到5项，普通刷新保留选中值。桌面截图为`artifacts/bms-levels-20261009/level-desktop.jpg`及`level-special-desktop.jpg`，只属于本地。
- 浏览器视口设置390×844后，旧页、刷新与新页实际仍为1280×720；本轮没有取得窄屏验证，误命名的mobile截图已改为special-desktop。线上现有tab绑定40秒超时，无本轮生产DOM / 截图。工具失败不等于HTTP失败，不用桌面或历史截图代签手机 / 生产真人验收。
- 协作文档验收通过：148件文档、1,358条链接、10件来源、24件事实登记；私有数据未读取。提交前逐文件还原本轮块后，与开工的已有diff完全相同；Backend、Client Bridge与客户端本轮未改。
- 初次HTTP在本地服务重启未完成时发生ConnectionRefused；等待实际退出0后继续。实际零结果检查发现`initial_counts`输出JSON数组，修成始终对象；随后发现Turbow等级为空字符串，修正未标注选项与精确匹配并重建。浏览器等待曾误写8项，实际A＋☆11为7项；原页面回归脚本第一次漏传参数，补足后通过。这些失败未记成通过。

## 发布与配置保全

实际HTTP包为`b879e4233818-6fbf7fd157d2`，Backend仍为`b879e42338183bed3a5b7de057817152a23de46c`，对应公开源码完整绑定运行提交；后续文档HEAD另记，不提升为生产来源。

73,083,160 B发布包SHA256为`6d3826a8f948504f052315437b9a5249a19370134f25cc72450800e5a42dcc65`，以已核验747发布包生成。Backend、vendor、八个批准插件、PHP环境与schema3字节保持；老散列资源保留。安装在128 MiB / CPU50% / swap0维护unit内完成，`.ready`、全件SHA、公开投影和运行环境身份实际核验后才切入。

发布前后各12件配置与manifest完整原件在`F:\zdamexy-workspace\websites\oms-web\artifacts\bms-levels-20261009\production-private`的`before / after`。两个Web unit及OMS include只换6fb版本与独立`production-r1`缓存绑定，真实正式缓存生成与FPM启动通过。静态unit verifier对旧 / 新均返回1、诊断逐字相同：检查器在RootDirectory外检查PHP及宿主已有告警；不冒充静态lint通过。真实BT Nginx检查、重载、HTTPS新CSS字节、下载与四项表读取通过；首个CSS404和启动502保留实际尝试，有界等待后200。主IR PID2936181、catalog PID1862556未重启；FPM从3324222更新为3346955。

同一业务库dev64771 / inode265517保持。OMS配对根站点、Homepage、固定维护unit / timer、TLS / ACME规则保留原字节；两个公开域名HTTPS200。没有发布Homepage本地内容，没有生成Windows客户端发行。

## 新增读取预算与盘账

在原200 MiB / high160 MiB / CPU50% / swap0 FPM限制下，两路同时读取Hex等级0和DP10強，共12次真实分页，各50条，分别3,214 / 777项。有限测量2.054秒；最低MemAvailable753,807,360 B，最高PHP采样108,056,576 B，实际cgroup峰111,284,224 B；max / OOM / oom_kill和自动重启均为0，swap0。该窗口只覆盖新增操作；2026-10-08的1,800秒、最大main＋WAL与两次空恢复继续保留原证据日期，没有重跑或提升状态。

更新后仅退役本任务刚上传且已与完整F包重新核对bytes / SHA的incoming传输gzip。实际运行 / 维护 / 747直接回退目录、日备份与完整F副本均保留。收尾磁盘空闲4,493,045,760 B；继续使用2026-10-08冻结最大main＋WAL1,422,161,928 B，加八对 / sidecar与额外2 GiB底线2,980,222,456 B，保守所需合计4,402,384,384 B，余量90,661,376 B。增长或再装新版本必须重算盘账，不把当前余量当无限空间。

## 两对完整备份与回退

固定helper仍直接取D1/22b，发布前InvocationID `1a519d9b93da4ac98ff9911400f6a8c3`对应`daily-20261009T065512Z.db.gz` / sidecar，运行747；发布后`2a50e8a915cc4dbaa6c427d923045a40`对应`daily-20261009T070609Z.db.gz` / sidecar，运行6fb。gzip分别9,070 / 9,054 B，raw均241,664 B；完整EOF / CRC、SHA、来源绑定、integrity / FK、schema3、22表 / 18索引 / 8trigger / 空sequence均通过，原件和private raw在本轮`backup-pre / backup-post`。

两个worker关闭、退出0 / Result success；备份与缓存终态MemoryPeak不可读，保持null，不填0。timer恢复enabled / active / waiting，收尾当次下一触发2026-10-10 04:18:11 CST。

本轮直接网页回退目标747 / production-r2，必须保留当前库并先取得当次新备份 / 配置原件，再原子恢复两个Web unit与OMS include，检查BT Nginx、切回current、重载和生成旧版正式缓存 / 重启FPM，检查启动就绪、双站和资源。本轮未执行往返；旧设计D1/e6与更早失败范围保持原日期，具体步骤取[现行维护](production-maintenance.md)。共享事实镜像在[Homepage](../../homepage-website/doc_md/other/oms-table-levels-20261009.md)和[旧Website](../../oms-website/doc_md/other/oms-table-levels-20261009.md)。
