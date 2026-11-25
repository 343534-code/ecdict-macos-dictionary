# ECDICT macOS Dictionary v1.1.0

v1.1.0 重点改善 macOS“词典”App 与三指快速查询中的可读性，并将原始词频标记转换为更容易理解的标签。词典继续使用 ECDICT 1.0.28 数据，约含 340 万条离线词条。

## 下载

- `ECDICT-macOS-Dictionary-v1.1.0.zip`：macOS 自带“词典”应用安装包；
- `ECDICT-MDX-1.0.28.mdx`：上游 MDX，适用于欧路词典、GoldenDict 和 MDict 等。

## 安装

1. 下载并解压 `ECDICT-macOS-Dictionary-v1.1.0.zip`。
2. 完全退出 macOS“词典”App。
3. 将整个 `ECDICT 简明英汉字典.dictionary` 复制到 `~/Library/Dictionaries/`。
4. 重新打开“词典”→“设置…”（`Command-,`）。
5. 勾选“ECDICT 简明英汉字典”。
6. **同时勾选至少一个 macOS 系统自带词典**；部分系统版本只启用第三方词典时可能无法显示释义。
7. 再次退出并重新打开“词典”，搜索 `two` 验证安装。

## 本次更新

- 使用 macOS 自适应文字和链接颜色，改善浅色、深色及快速查询面板中的对比度；
- 提高音标、词头和释义的可读性，解决灰色音标不清晰的问题；
- 将原始 Collins 词频标记转换为 `Collins 1★` 至 `Collins 5★` 标签；
- 将 Oxford 3000 标记显示为直观标签；
- 优化词头、音标、词性、释义和补充信息的视觉层级；
- 补充真实查询效果图和醒目的三步安装说明；
- 将 XSL、偏好设置页面和图像资源纳入可复现构建流程；
- 补充词频标签转换的自动测试和上游许可说明。

## 已验证

- `.dictionary` 正文、关键词索引和资源文件构建完成；
- 在 macOS“词典”App 中实际查询 `two`，搜索列表和释义正常；
- 音标以高对比颜色显示；
- 原始 `-5` 标记正确显示为 `Collins 5★`；
- ZIP 压缩数据完整性检查通过。

Apple 构建工具因索引键长度限制跳过了 7 个超长英文短语，其余约 340 万条词条正常构建。

## SHA-256

```text
901e928048dc2a1dbb86916469c1590e589846dc24b54bfe6136753e509c6d23  ECDICT-macOS-Dictionary-v1.1.0.zip
275e71b58fd359bfe649af1cbee533ea81770bdbc53ec4a34567f84720a5751b  ECDICT-MDX-1.0.28.mdx
```
