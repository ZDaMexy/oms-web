# AGENTS.md — OMS Web

本仓从 ppy/osu-web 原项目接续，固定初始上游为 `2c596022a1345fbed288978e7fa5304df0359f50`。保留上游历史和 Laravel / Blade / React / Less / Turbo 页面组织，在原文件裁剪不适用功能并接现有 OMS 服务，不抽取组件重建门户。

## 当前授权与入口

- 用户先授权 2026-10-07 本地实施，后确认本地视觉并授权生产部署；2026-10-08 原版网站已上线，当前为 **已部署待验收**。玩家范围取 [OMS.md](OMS.md)，实际发布与历史失败取[生产记录](doc_md/production-deployment-20261007.md)，当前来源、维护和未完成真人门取[维护说明](doc_md/production-maintenance.md)。
- 先读 [README](README.md)、[OMS.md](OMS.md) 与 [文档索引](doc_md/README.md)，追溯本地实施时读[迁移记录](doc_md/oms-web-migration-20261007.md)。跨边界合同仍由相邻 `oms-server/dev_bridge_md` 维护，现有账号、成绩、目录和社区权威在 `oms-server/oms-backend`。
- 开始先核对 status、HEAD 和在线跟踪；保全已有工作。现分支为 main，选择性提交；用户已授权及时 commit / push 及生产部署，实际运行、资源、恢复与公开核验通过后才记录部署结果，不提前声明成功。

## 产品和实现边界

- 保留原页面结构、样式和交互；删除无真实能力的功能、路由、全局初始化及后台任务。只显示真实 OMS 字段，不制造原 osu! 用户统计、PP、等级、在线状态或游玩历史。
- 只提供 BMS 与 mania。默认离线、按需请求；不扩展聊天、presence、多人、支付、谱包或回放托管。
- 现 OMS 账号是唯一权威；网页 cookie 保留 `/api/ir/v1` 范围、HttpOnly、同源写请求，网页与客户端分别认证。不得新增第二套密码库或扩大 cookie 范围以方便服务端页面渲染。
- 来源、条件、未知灯、旧 namespace / ID 和三类记录语义沿正式合同；混榜由服务按完整范围计算，不拼 TopN、不按本页计算名次。
- 谱包解析与原站下载使用 BMS Ginger / 616、mania Sayobot；网站难度表导航使用用户批准的 [Zris 静态元数据](doc_md/bms-difficulty-tables-20261009.md)，实际单曲 MD5 接已有榜。网站新增来源不等于客户端新增支持。不读取母库或其他私有数据，不将凭据、个人原始行和恢复数据放入 Git。
- 保留 AGPL、作者归属与准确修改源码；osu! / ppy 品牌替换为 OMS，商业 Torus 字体不在新站启用，不自行购买资源。

## 存储、验证与协作

- 每个开发 shell 先 `. .\UseDevelopmentStorage.ps1`；源码、缓存、临时文件、运行数据和证据放 F 盘。WSL 或容器的实际数据盘也须在 F，不能只把源代码放 F。
- build / test / formatter 由主执行者串行调度；并行修改明确文件归属，检查期间冻结相关源文件。
- 旧设计完整备份只放 F 盘，包含实际资源、Git 历史及未提交差异，并从新空目录恢复。设计回退保留当前数据；现成绩库日备份安全门另行保留。
- 状态记录区分源码、软件检查、实际本地 HTTP、浏览器、性能、恢复、用户验收和生产。没有实际证据不提升状态，不用 fixtures 或旧截图代签。
- 客户端由用户通过 VS Code 非调试启动；本仓任务不生成 Windows 客户端发行包、publish 或安装副本。
