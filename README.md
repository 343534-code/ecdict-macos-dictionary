# ECDICT macOS Dictionary

将 [skywind3000/ECDICT](https://github.com/skywind3000/ECDICT) 的“简明英汉字典增强版”转换为可供 macOS `Dictionary.app` 使用的离线 `.dictionary` 词典。

## 下载与安装

1. 在本仓库的 [Releases](../../releases) 下载 `ECDICT-macOS-Structured-High-Contrast-v2.0.zip`。
2. 解压后，将 `.dictionary` 文件夹复制到 `~/Library/Dictionaries/`。
3. 打开 macOS“词典”→“设置”，勾选“ECDICT 简明英汉字典（结构化高对比版）”。
4. 如未立即出现，请退出并重新打开“词典”。

Release 同时附带上游官方发布的 `简明英汉字典增强版.mdx`，便于在 GoldenDict、MDict、欧路词典等兼容软件中使用。

## 特点

- 约 340 万条词条，完全离线。
- 针对 macOS Dictionary 重新组织词头、音标、词性、释义和元数据。
- 提供深色界面的高对比样式。
- 保留可复现的导出脚本、CSS、XSL、Info.plist 与 Makefile。

## 构建

构建需要 Apple Dictionary Development Kit。先用 `scripts/export_ecdict_styled.py` 将 MDX 导出为 Dictionary XML，再在 `dictionary-source` 目录中使用 Makefile 编译。

Apple 已不再面向普通用户维护该开发工具，因此不同 macOS 版本的兼容性可能有所差异。

## 来源与许可证

词典数据和上游 MDX 来自 [ECDICT 1.0.28](https://github.com/skywind3000/ECDICT/releases/tag/1.0.28)。ECDICT 以 MIT License 发布；本仓库保留其许可声明与来源说明。

本项目是非官方转换版本，与 Apple Inc. 及 ECDICT 原作者均无隶属或背书关系。Apple Dictionary Development Kit 不包含在本仓库中。

## 已知限制

macOS 的三指“查询”浮窗可能覆盖第三方词典的部分 CSS 颜色。完整词条排版建议在 Dictionary.app 中查看。

