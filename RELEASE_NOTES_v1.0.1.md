# ECDICT macOS Dictionary v1.0.1

v1.0.1 是针对安装体验和发布一致性的修正版。词典正文、索引和排版结构与已验证可用的 v1.0.0 保持一致。

## 下载内容

- `ECDICT-macOS-Dictionary-v1.0.1.zip`：macOS 自带“词典”应用安装包；
- `ECDICT-MDX-1.0.28.mdx`：上游 MDX 原文件，可用于欧路词典、GoldenDict、MDict 等支持 MDX 的软件。

## 安装

1. 下载并解压 `ECDICT-macOS-Dictionary-v1.0.1.zip`。
2. 完全退出 macOS“词典”应用（按 `Command-Q`）。
3. 在访达中选择“前往”→“前往文件夹…”，输入 `~/Library/`。
4. 打开 `Dictionaries` 文件夹；如果不存在，请在 `~/Library/` 中新建该文件夹。
5. 将整个 `ECDICT 简明英汉字典.dictionary` 复制到 `~/Library/Dictionaries/`，**不要只复制其中的 `Contents`**。
6. 重新打开“词典”→“设置…”，勾选“ECDICT 简明英汉字典”。
7. **必须同时勾选至少一个 macOS 系统自带词典**，例如系统提供的英语词典或英汉词典。某些 macOS 版本只勾选 ECDICT 时，可能无法显示释义。
8. 可将 ECDICT 拖到词典列表前部，使其优先显示。
9. 再次完全退出并重新打开“词典”，搜索 `two` 确认可以正常显示释义。

> 如果以前安装过测试版，请先在“词典”设置中取消勾选旧版，并从 `~/Library/Dictionaries/` 移走名称中含“优化版”、“高对比版”或“结构化版”的旧词典。

## 文件校验

```text
a97debcf691a75c69264994be306672d2fcb821ea72096b1640f6cd104dbe238  ECDICT-macOS-Dictionary-v1.0.1.zip
275e71b58fd359bfe649af1cbee533ea81770bdbc53ec4a34567f84720a5751b  ECDICT-MDX-1.0.28.mdx
```

## 本次改进

- 补全访达安装步骤、隐藏目录进入方法和旧测试版清理说明；
- 明确说明必须同时启用至少一个 macOS 系统自带词典；
- 将源码构建名称统一为“ECDICT 简明英汉字典”；
- 锁定 `readmdict==0.1.1` 和 `python-lzo==1.15` 构建依赖；
- 统一 ECDICT 1.0.28 的 MIT License 来源声明；
- 清理 ZIP 中的 AppleDouble 和隔离属性元数据。

## 来源与许可

词典数据来自 [skywind3000/ECDICT](https://github.com/skywind3000/ECDICT) 1.0.28。本仓库保留该版本中 `Copyright (c) 2017 Linwei` 的 MIT License 许可声明，转换脚本和排版修改也按同一 MIT License 提供。本项目为非官方 macOS 转换版，与 Apple Inc. 及 ECDICT 原作者无隶属、合作或背书关系。
