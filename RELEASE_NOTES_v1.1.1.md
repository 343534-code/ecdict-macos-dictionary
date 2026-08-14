# ECDICT macOS Dictionary v1.1.1

v1.1.1 是安装体验更新。词典正文、索引和排版与 v1.1.0 保持一致，新增一行终端命令、macOS PKG 安装包和可供脚本验证的 `SHA256SUMS.txt`。

## 最快安装

打开“终端”，粘贴下面一整行：

```bash
curl -fsSL https://raw.githubusercontent.com/343534-code/ecdict-macos-dictionary/v1.1.1/scripts/install.sh | /bin/bash
```

脚本会自动下载最新版、验证 SHA-256、备份同名旧版，并安装到当前用户的 `~/Library/Dictionaries/`。此方式不需要管理员密码。

安装完成后仍需打开“词典”→“设置…”，勾选 ECDICT，并同时勾选至少一个 macOS 系统自带词典。

## 下载文件

- `ECDICT-macOS-Dictionary-v1.1.1.zip`：用户级手动安装包；
- `ECDICT-macOS-Dictionary-v1.1.1.pkg`：系统级图形化安装包；
- `ECDICT-MDX-1.0.28.mdx`：适用于欧路词典、GoldenDict 和 MDict 等软件；
- `SHA256SUMS.txt`：全部下载附件的 SHA-256。

## PKG 说明

PKG 将词典安装到 `/Library/Dictionaries/`，需要管理员密码。本次 PKG **未使用 Apple Developer Installer 证书签名**；如果 macOS 阻止打开，请在确认下载来源和 SHA-256 后，前往“系统设置”→“隐私与安全性”选择“仍要打开”。不希望使用未签名安装包时，请选择一行命令或 ZIP。

## SHA-256

```text
c226933719eb01183e1fd3d12ec3bbc1aa91a66660914b3745c66486add333bc  ECDICT-macOS-Dictionary-v1.1.1.zip
6c22083484d51a34160111da384d46766b61b00ccec18c5162d2fc91f79e7a6a  ECDICT-macOS-Dictionary-v1.1.1.pkg
275e71b58fd359bfe649af1cbee533ea81770bdbc53ec4a34567f84720a5751b  ECDICT-MDX-1.0.28.mdx
```
