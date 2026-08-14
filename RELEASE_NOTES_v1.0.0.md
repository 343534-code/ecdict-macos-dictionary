# ECDICT macOS Dictionary v1.0.0

ECDICT macOS Dictionary 是一款为 Apple 自带“词典”应用制作的大规模离线英汉词典。本版本基于 ECDICT 1.0.28 数据，将词头、音标、词性、中文释义和标签转换为适合 macOS Dictionary.app 的结构化格式。

## 下载内容

- `ECDICT-macOS-Dictionary-v1.0.0.zip`：macOS 自带“词典”应用安装包；
- `ECDICT-MDX-1.0.28.mdx`：上游 MDX 原文件，可用于欧路词典、GoldenDict、MDict 等支持 MDX 的软件。

## 主要特性

- 约 340 万条词条，支持单词、变形、短语和扩展词目；
- 完全离线，无广告、无账号、无常驻进程；
- 结构化显示词头、音标、词性、释义和词频/考试标签；
- 可在 Dictionary.app、右键“查询”和触控板三指轻点中使用。

## 安装

1. 下载并解压 `ECDICT-macOS-Dictionary-v1.0.0.zip`。
2. 将 `ECDICT 简明英汉字典.dictionary` 复制到 `~/Library/Dictionaries/`。
3. 完全退出并重新打开 macOS“词典”。
4. 打开“词典”→“设置…”，勾选“ECDICT 简明英汉字典”。
5. **至少同时勾选一个 macOS 系统自带词典**。某些 macOS 版本只勾选第三方词典时，可能无法正常显示查询结果。
6. 可将 ECDICT 拖到词典列表前部，使其优先显示。

## 更新说明

- 本版本作为项目的正式首发版，版本号从 `1.0.0` 开始；
- 已根据实际使用结果选定当前兼容构建；
- 已补充“需同时启用系统自带词典”的使用说明。

## 来源与许可

词典数据来自 [skywind3000/ECDICT](https://github.com/skywind3000/ECDICT) 1.0.28，按上游 MIT License 发布。本项目为非官方 macOS 转换版，与 Apple Inc. 及 ECDICT 原作者无隶属、合作或背书关系。
