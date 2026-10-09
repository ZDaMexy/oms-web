# 2026-10-09 LR2IR 作为普通排行榜来源

用户进一步明确：提前收录的 LR2IR 成绩是排行榜的基底，网页不必按历史客户端特殊分区。本轮接续[17:24 排行榜审改](rankings-layout-review-20261009.md)，将 LR2IR 和 OMS、beatoraja、LR2oraja、Endless Dream、OpenLR2 并列为六个普通选项；去掉原来的两组标题及 LR2 / SBMP / 未知客户端三个按钮。当前产品仍为已部署待验收；真人账号、下载入库、OMS 对照与固定宿主 P/C 门保持原范围。

默认页改名「排行榜」，缩短默认说明；行内来源与榜首只显示 LR2IR，账号编号、记录类型、原客户端标记仍在成绩详情。收录信息按显示名称去重，帮助解释跨播放器参考性质。同条件比较规则不变，旧身份不合并，也不捏造游玩时间。原记录与稳定 API 均不改写，网页采用边界见[正式合同](../../../oms-server/dev_bridge_md/doc_md/subline/oms-ir/multisource-contract.md)。

点击 LR2IR 显式选择三个可用代码 `lr2ir.v3.lr2,lr2ir.v3.sbmp,lr2ir.v3.unknown`，再次点击移除三个代码。旧链接只选原子来源时保持原范围，按钮显示部分选择；点击才补齐选择。清空仍为 `sources=` / 0 人，默认省略仍为全部可用。移除未使用的单选参数，不增加第二套筛选或排名计算。

TypeScript 检查通过；从已提交源码 `479987991a9ba349d45675c388b67c69ea95c847` 冻结输入完成真实生产编译，213 件输入与 477 件累计散列资源记录完整，webpack 保留三条上游体积警告。本地真实 HTTP 成绩 / 权限 / mania / 同条件核对 65 项及页面 / 完整资源 / 插件 31 项通过，没有创建账号或新成绩。

本地浏览器实际验证六个并列来源、清空 / 单选 LR2IR / 移除、旧链接的 `aria-pressed=mixed` 与点击补齐、全部选择及展开原客户端详情；实际视口 1280×720，内容宽1265，没有页面横向溢出。`final-desktop.jpg` 和 `detail-desktop.jpg` 是本地实际页面。本轮线上新建页取景及绑定已存在页各约30秒超时，没有取得生产 DOM / 截图，不能以本地图片代签线上真人视觉。

2026-10-09 20:12:43 CST 已切入 `/opt/oms-ir/releases/b879e4233818-479987991a9b`，Web 运行源码为上述 `479987991a9ba349d45675c388b67c69ea95c847`，Backend 仍 `b879e42338183bed3a5b7de057817152a23de46c`。完整包 73,535,613 B / SHA256 `7e053d3e8fd09a499150ea357dd34986bccf7632813c964a510591268b3a47b6`；Backend / vendor / 八插件 / PHP环境保持原字节，schema3 / 22表及库 dev64771 / inode265517 保持。主 IR PID2936181 与 catalog PID1862556 未重启；FPM PID3463348，缓存独立 `production-r1`。

两 Web unit 与 OMS include 只换 fff→479 版本 / 缓存绑定，前后12件完整配置与manifest原件保全；其他配对站点 / 固定维护 / TLS / ACME配置保持。真实命名空间缓存、FPM与宝塔Nginx核验通过；原 / 新静态unit诊断同为1且相同，不称静态lint返回0。实际就绪尝试保留在 `activation.json`。发布前 31 项与发布后 36 项公开成绩核对通过，省略 / 单一原子来源 / LR2IR全组 / 排除LR2IR / 空选 / 第二页等完整响应一致，仍653位玩家、原EX / 满分、原灯和全局并列名次。公开页面 / 全件资源 / 对应源码下载 / 双站HTTPS另 33 项通过。

固定 D1/22 helper 的新鲜前后备份均完整外取到受保护 F 目录，以 InvocationID / running release 绑定 fff 与479；gzip分别9,051 / 9,071 B，private raw各241,664 B，完整 EOF / CRC / SHA / schema / integrity / FK / 22表核验通过。不可读的终态备份 / 缓存峰保留null；timer恢复enabled / active / waiting，准确当次下一触发保留在最终收据，不承诺之后的秒数。

安装前，已无进程 / 配置 / cron引用的上一轮6fb包完整F归档，11,533件文件 / 目录 / 链接的全部字节、权限、uid / gid、mtime与目标核对；新鲜备份后再次核引用及归档SHA，才退役服务器准确6fb目录。当前直接同库网页回退为 fff，主IR所用B0、固定维护D1/22、旧设计D1/e6与日备份保留。新版本安装后只在完整F包 / 远端SHA核对后退役本任务incoming重复gzip。

两读取者12个真实请求的 0.506 秒有限窗口：最低MemAvailable 823,922,688 B，最高PHP采样 43,720,704 B，实际cgroup峰 67,706,880 B；swap / OOM / max / 重启零，原200MiB / high160 / CPU50%预算不改。最终空闲 4,591,403,008 B，比沿2026-10-08最大main＋WAL / 八对 / 额外2GiB保守预留 4,402,384,384 B高 189,018,624 B。本轮不重标旧1,800秒压力或两次空恢复。

完整原始证据在 `F:\zdamexy-workspace\websites\oms-web\artifacts\lr2ir-source-presentation-20261009`；private恢复数据不入Git。准确当前来源、同库回退与真人门取[维护说明](production-maintenance.md)，共享配置投影同步[Homepage镜像](../../homepage-website/doc_md/other/oms-lr2ir-source-20261009.md)和[旧Website镜像](../../oms-website/doc_md/other/oms-lr2ir-source-20261009.md)。选择性文档提交与运行源码分别记录，既有其他项目差异保全；未发布Homepage内容或修改客户端。
