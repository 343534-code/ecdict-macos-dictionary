# 贡献指南

感谢你对 ECDICT macOS Dictionary 的关注与支持！欢迎通过提交 Issue 或 Pull Request 参与改进，包括但不限于：

- 修复词典导出、排版或安装脚本中的问题；
- 完善自动化测试与语义重构层的校验逻辑；
- 改进中英文文档、FAQ 或查询示例。

## 本地开发环境

本项目使用 Python 3（推荐 3.12+）。

- **运行测试与语义校验**（无需 LZO 或 Apple Dictionary Development Kit）：

  ```bash
  python3 -m pip install -r requirements-semantic.txt
  ```

- **从 MDX 源码构建 `.dictionary`**（仅 macOS 构建完整词典时需要）：

  ```bash
  brew install lzo
  python3 -m pip install -r requirements.txt
  ```

## 提交前检查

提交 Pull Request 前，建议在仓库根目录运行与 CI 一致的本地检查：

```bash
# 1. 运行单元测试
python3 -m unittest discover -s tests -v

# 2. 校验 Python 语法
python3 -m compileall -q scripts semantic_cleanup tests

# 3. 校验 dictionary-source/MyInfo.plist XML
python3 -c "import plistlib, xml.etree.ElementTree as ET; ET.parse('dictionary-source/MyInfo.plist'); assert plistlib.load(open('dictionary-source/MyInfo.plist', 'rb')).get('CFBundleShortVersionString')"

# 4. 检查 Shell 脚本语法与静态规范
bash -n scripts/install.sh scripts/build_pkg.sh packaging/scripts/postinstall
shellcheck scripts/install.sh scripts/build_pkg.sh packaging/scripts/postinstall
```

## 版本号与打包

- 词典版本号以 [`dictionary-source/MyInfo.plist`](dictionary-source/MyInfo.plist) 中的 `CFBundleShortVersionString` 为准。
- 运行 [`scripts/build_pkg.sh`](scripts/build_pkg.sh) 时，如果未指定 `VERSION` 环境变量，脚本会自动从 `dictionary-source/MyInfo.plist` 读取 `CFBundleShortVersionString`。
- 发布新版本时，请在 [`docs/releases/`](docs/releases/) 新增对应版本的发布说明，并同步更新根目录的 [`CHANGELOG.md`](CHANGELOG.md)。

## Pull Request 流程

1. 从 `main` 分支切出新的功能或修复分支，分支名建议简洁明确（例如 `fix/installer-check` 或 `docs/update-faq`）。
2. 保持单个 PR 改动聚焦，避免在同一提交中混入无关重构。
3. 如涉及转换逻辑或排版改动，请补充或更新 `tests/` 中对应的单元测试；如涉及用户行为变化，请同步更新 `README.md` / `README.en.md`。
4. 推送分支并创建 PR，确保 GitHub Actions CI 检查全部通过。

## 报告问题与提出建议

- 提交 Bug 报告或功能建议时，请优先使用仓库提供的 [Issue 模板](.github/ISSUE_TEMPLATE/)。
- 反馈 macOS“词典”显示异常时，请注明 macOS 版本、词典版本、安装方式以及是否已同时勾选至少一个系统自带词典。

## 许可证

提交到本仓库的贡献将按仓库根目录的 [MIT License](LICENSE) 发布。上游词典数据归属与说明见 [NOTICE](NOTICE)。
