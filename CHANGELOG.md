# Changelog

本文件汇总 ECDICT macOS Dictionary 各发布版本的主要变更。各版本的完整发布说明、安装指引与 SHA-256 校验值见 [`docs/releases/`](docs/releases/)。

## [v1.2.1] - 2026-09-25

完整发布说明：[RELEASE_NOTES_v1.2.1.md](docs/releases/RELEASE_NOTES_v1.2.1.md)

### 改进
- 优化系统 Look Up 首屏预览，优先展示各词性的第一条原始释义，点击“更多”可展开完整详情。
- 修复精简预览导致详情无法展开的问题，完整保留剩余释义、计算机领域说明、词形变化、考试标签与词频。
- Dictionary.app 完整页面按词性组织释义，重复词性下的原始释义行编号展示。
- 规范 IPA 重音、长音符号及中文分隔符，支持词形变化点击查询。
- 更新 README、最新查询预览与界面示意 GIF。

## [v1.1.1] - 2026-08-14

完整发布说明：[RELEASE_NOTES_v1.1.1.md](docs/releases/RELEASE_NOTES_v1.1.1.md)

### 新增
- 新增一行终端命令安装脚本（`install.sh`），支持自动下载、SHA-256 校验与旧版备份。
- 新增 macOS PKG 系统级图形化安装包，将词典安装到 `/Library/Dictionaries/`。
- 新增 `SHA256SUMS.txt`，供脚本与手动校验所有 Release 附件。

### 说明
- 词典正文、索引与排版与 v1.1.0 保持一致。

## [v1.1.0] - 2026-08-14

完整发布说明：[RELEASE_NOTES_v1.1.0.md](docs/releases/RELEASE_NOTES_v1.1.0.md)

### 改进
- 采用 macOS 自适应文字与链接颜色，改善浅色、深色模式及快速查询面板中的对比度。
- 提升音标、词头与释义可读性，修复灰色音标不清晰的问题。
- 将原始 Collins 词频标记转换为 `Collins 1★`–`Collins 5★` 标签，将 Oxford 3000 标记显示为直观标签。
- 优化词头、音标、词性、释义与补充信息的视觉层级。
- 将 XSL、偏好设置页面与图像资源纳入可复现构建流程，并补充词频标签转换自动测试与真实查询效果图。

## [v1.0.1] - 2026-08-14

完整发布说明：[RELEASE_NOTES_v1.0.1.md](docs/releases/RELEASE_NOTES_v1.0.1.md)

### 修复与改进
- 补全访达安装步骤、隐藏目录进入方法、旧测试版清理说明及需同时启用系统自带词典的提示。
- 将源码构建名称统一为“ECDICT 简明英汉字典”。
- 锁定 `readmdict==0.1.1` 与 `python-lzo==1.15` 构建依赖。
- 统一 ECDICT 1.0.28 的 MIT License 来源声明，并清理 ZIP 中的 AppleDouble 和隔离属性元数据。

## [v1.0.0] - 2026-08-14

完整发布说明：[RELEASE_NOTES_v1.0.0.md](docs/releases/RELEASE_NOTES_v1.0.0.md)

### 新增
- 正式首发，基于 ECDICT 1.0.28 数据转换约 340 万条离线英汉词条。
- 支持在 macOS Dictionary.app、右键“查询”与触控板三指轻点中使用。
- 结构化展示词头、音标、词性、中文释义及词频/考试标签，同时提供上游 MDX 文件下载。

[v1.2.1]: https://github.com/343534-code/ecdict-macos-dictionary/releases/tag/v1.2.1
[v1.1.1]: https://github.com/343534-code/ecdict-macos-dictionary/releases/tag/v1.1.1
[v1.1.0]: https://github.com/343534-code/ecdict-macos-dictionary/releases/tag/v1.1.0
[v1.0.1]: https://github.com/343534-code/ecdict-macos-dictionary/releases/tag/v1.0.1
[v1.0.0]: https://github.com/343534-code/ecdict-macos-dictionary/releases/tag/v1.0.0
