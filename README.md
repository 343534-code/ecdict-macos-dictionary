# ECDICT macOS Dictionary

面向 macOS 系统词典的超大规模、完全离线英汉词典。本项目将 [skywind3000/ECDICT](https://github.com/skywind3000/ECDICT) 的“简明英汉字典增强版”转换为 Apple `Dictionary.app` 可直接使用的 `.dictionary` 格式，并提供适合系统深色界面的结构化排版。

## 产品介绍

ECDICT macOS Dictionary 适合希望在阅读、写作、编程和学习过程中快速查词，同时不希望依赖浏览器、广告或网络服务的用户。

安装后可通过以下入口查询：

- macOS 自带“词典”应用；
- 在支持的应用中选中单词后使用“查询”；
- 触控板三指轻点查询；
- 右键菜单中的“查询”；
- Spotlight 和部分系统级文本服务。

### 主要特点

- 约 340 万条词条，包含单词、变形、短语、专有名词和大量扩展词目；
- 数据完全保存在本机，查询不需要联网；
- 独立显示词头、音标、词性、中文释义和词频/考试标签；
- 针对 macOS 深色外观提供高对比样式；
- 不安装常驻进程，不收集数据，也不需要注册账号；
- 同时提供原始 MDX 文件，可用于欧路词典、GoldenDict、MDict 等软件；
- 提供转换脚本和构建配置，便于审查、修改和复现。

## 系统要求

- macOS 10.11 或更高版本；
- 约 500 MB 可用磁盘空间；
- 安装过程不需要管理员密码。

## 下载文件说明

请前往仓库的 [Releases](../../releases) 页面：

| 文件 | 用途 |
| --- | --- |
| `ECDICT-macOS-Structured-High-Contrast-v2.0.zip` | macOS Dictionary.app 使用的结构化高对比版 |
| `简明英汉字典增强版-ECDICT-1.0.28.mdx` | 上游官方 MDX，适用于欧路词典、GoldenDict、MDict 等 |

## macOS 安装流程

### 方法一：通过访达安装

1. 下载 `ECDICT-macOS-Structured-High-Contrast-v2.0.zip`。
2. 双击 ZIP 文件解压，得到 `ECDICT 简明英汉字典（结构化高对比版）.dictionary`。
3. 在访达菜单中选择“前往”→“前往文件夹…”。
4. 输入 `~/Library/Dictionaries/` 并按回车。
5. 如果 `Dictionaries` 文件夹不存在，请在 `~/Library/` 中新建该文件夹。
6. 将整个 `.dictionary` 文件夹复制到 `~/Library/Dictionaries/`，不要只复制其中的 `Contents`。
7. 完全退出并重新打开 macOS“词典”应用。
8. 打开“词典”→“设置…”。
9. 在列表底部找到并勾选“ECDICT 简明英汉字典（结构化高对比版）”。
10. 可将它拖到列表前部，使系统查询优先显示本词典。

### 方法二：终端安装

解压后执行：

```bash
mkdir -p "$HOME/Library/Dictionaries"
ditto "ECDICT 简明英汉字典（结构化高对比版）.dictionary" \
  "$HOME/Library/Dictionaries/ECDICT 简明英汉字典（结构化高对比版）.dictionary"
killall Dictionary DictionaryServiceHelper 2>/dev/null || true
```

随后打开“词典”→“设置…”，勾选该词典。

## 启用三指查询

1. 打开“系统设置”。
2. 进入“触控板”→“光标与点按”。
3. 开启“查询与数据检测器”。
4. 将操作方式设置为“三指轻点”。
5. 在 Safari、备忘录、TextEdit 或其他支持系统查询的应用中，把指针移到英文单词上并用三指轻点。

若查询浮窗没有显示本词典，请先确认它已在“词典”设置中勾选，并尝试将其拖到其他词典之前。

## 在欧路词典等软件中使用 MDX

1. 下载 `简明英汉字典增强版-ECDICT-1.0.28.mdx`。
2. 在目标软件中打开“词典管理”或“导入词典”。
3. 选择下载的 `.mdx` 文件。
4. 启用词典并根据需要调整查询优先级。

不同软件的菜单名称可能不同，请参考对应软件的导入说明。

## 更新版本

1. 退出“词典”应用。
2. 删除或移走 `~/Library/Dictionaries/` 中的旧版本。
3. 将新版 `.dictionary` 文件夹复制到该目录。
4. 重新打开“词典”并确认新版已勾选。

如果同名旧版仍被缓存，可先将旧版取消勾选，退出“词典”，再安装新版。

## 卸载

1. 打开“词典”→“设置…”，取消勾选本词典。
2. 退出“词典”。
3. 在访达中前往 `~/Library/Dictionaries/`。
4. 将对应 `.dictionary` 文件夹移到废纸篓。
5. 重新打开“词典”。

## 常见问题

### 安装后找不到词典

- 确认复制的是完整 `.dictionary` 文件夹；
- 确认路径是当前用户的 `~/Library/Dictionaries/`；
- 完全退出并重新打开“词典”；
- 在“词典”→“设置…”列表底部查找并手动勾选；
- 必要时注销并重新登录 macOS。

### 三指查询没有出现 ECDICT

系统查询只使用“词典”设置中已启用的来源。请勾选本词典，并将它拖到靠前位置。已经打开的查询浮窗不会即时刷新，需要关闭后重新触发。

### 音标颜色与 Dictionary.app 不完全一致

macOS 的三指查询浮窗会过滤或覆盖第三方词典的部分 CSS。Dictionary.app 中能看到完整排版；快速查询浮窗中的颜色可能随系统版本和外观模式变化。

### 为什么安装包很大

词典包含约 340 万条索引和离线正文。解压后的 `.dictionary` 大约 416 MB，属于正常体积。

## 从源码构建

构建需要：

- Python 3；
- `readmdict`；
- Apple Dictionary Development Kit；
- 上游 ECDICT MDX 文件。

导出结构化 XML：

```bash
python3 scripts/export_ecdict_styled.py \
  "简明英汉字典增强版.mdx" \
  "dictionary-source/ECDICT-styled.xml"
```

然后进入 `dictionary-source`，确认 Makefile 中的 Dictionary Development Kit 路径，再运行：

```bash
make all
```

成品会生成在 `dictionary-source/objects/`。完整构建需要较长时间和数 GB 临时磁盘空间。

Apple 已不再面向普通用户维护 Dictionary Development Kit，因此不同 macOS 版本的构建兼容性可能有所差异。Apple 开发工具本身不包含在本仓库中。

## 项目结构

```text
dictionary-source/       样式、XSL、Info.plist 和 Makefile
scripts/                 MDX 到 Apple Dictionary XML 的转换脚本
LICENSE                  上游 MIT License
NOTICE                   数据来源和非官方声明
```

## 来源与许可证

词典数据和上游 MDX 来自 [ECDICT 1.0.28](https://github.com/skywind3000/ECDICT/releases/tag/1.0.28)。ECDICT 以 MIT License 发布；本仓库保留其许可声明与来源说明。

本项目是非官方转换版本，与 Apple Inc. 及 ECDICT 原作者均无隶属、合作或背书关系。词典内容按原许可证“按原样”提供，不保证所有释义均准确或适合专业用途。
