# Bootstrap 3 样式来源

此目录仅保留 Bootstrap 3.4.1 的原始 `less/`、字体与 MIT 许可，用于维持既有页面样式。来源为 npm 官方包 `bootstrap@3.4.1`；导入文件保持原字节，仍从 `resources/css/app.less` 编译。

未包含 Bootstrap 的 JavaScript 插件。OMS 没有加载这些插件，已移除整包 npm 依赖及其全局类型，避免构建环境保留已知存在 XSS 问题的未使用脚本。这里的样式仍受原 MIT 许可约束，版权见 [LICENSE](LICENSE)。
