#!/bin/bash

set -euo pipefail

REPOSITORY="343534-code/ecdict-macos-dictionary"
DICTIONARY_NAME="ECDICT 简明英汉字典.dictionary"
INSTALL_DIR="${ECDICT_INSTALL_DIR:-$HOME/Library/Dictionaries}"
API_URL="${ECDICT_RELEASE_API_URL:-https://api.github.com/repos/$REPOSITORY/releases/latest}"

work_dir=""

cleanup() {
    if [[ -n "$work_dir" && -d "$work_dir" ]]; then
        /bin/rm -rf -- "$work_dir"
    fi
}

fail() {
    printf '安装失败：%s\n' "$1" >&2
    exit 1
}

command -v curl >/dev/null 2>&1 || fail "系统中找不到 curl。"
command -v ditto >/dev/null 2>&1 || fail "系统中找不到 ditto。"
command -v shasum >/dev/null 2>&1 || fail "系统中找不到 shasum。"

[[ "$(uname -s)" == "Darwin" ]] || fail "此安装脚本仅支持 macOS。"
[[ -n "$INSTALL_DIR" && "$INSTALL_DIR" != "/" ]] || fail "安装目录不安全。"

work_dir="$(/usr/bin/mktemp -d "${TMPDIR:-/tmp}/ecdict-install.XXXXXX")"
trap cleanup EXIT INT TERM

release_json="$work_dir/release.json"
checksum_file="$work_dir/SHA256SUMS.txt"
archive_file="$work_dir/dictionary.zip"
extract_dir="$work_dir/extracted"

printf '正在获取 ECDICT 最新版本信息…\n'
/usr/bin/curl -fsSL --retry 3 \
    -H 'Accept: application/vnd.github+json' \
    "$API_URL" -o "$release_json" \
    || fail "无法连接 GitHub Releases。"

zip_url="$(/usr/bin/awk -F '"' '/browser_download_url/ && /ECDICT-macOS-Dictionary-v[0-9.]+\.zip/ { print $4; exit }' "$release_json")"
checksum_url="$(/usr/bin/awk -F '"' '/browser_download_url/ && /SHA256SUMS\.txt/ { print $4; exit }' "$release_json")"

[[ -n "$zip_url" ]] || fail "最新版 Release 中没有找到 macOS ZIP。"
[[ -n "$checksum_url" ]] || fail "最新版 Release 中没有找到 SHA256SUMS.txt。"

zip_name="${zip_url##*/}"

printf '正在下载 %s…\n' "$zip_name"
/usr/bin/curl -fL --retry 3 "$zip_url" -o "$archive_file" \
    || fail "词典下载失败。"
/usr/bin/curl -fsSL --retry 3 "$checksum_url" -o "$checksum_file" \
    || fail "校验文件下载失败。"

expected_hash="$(/usr/bin/awk -v name="$zip_name" '$2 == name { print $1; exit }' "$checksum_file")"
actual_hash="$(/usr/bin/shasum -a 256 "$archive_file" | /usr/bin/awk '{ print $1 }')"

[[ -n "$expected_hash" ]] || fail "校验文件中没有 $zip_name。"
[[ "$actual_hash" == "$expected_hash" ]] || fail "SHA-256 校验失败，文件可能不完整。"

printf 'SHA-256 校验通过。\n'
/bin/mkdir -p "$extract_dir"
/usr/bin/ditto -x -k "$archive_file" "$extract_dir" \
    || fail "ZIP 解压失败。"

dictionary_path="$(/usr/bin/find "$extract_dir" -maxdepth 2 -type d -name "$DICTIONARY_NAME" -print -quit)"
[[ -n "$dictionary_path" ]] || fail "ZIP 中没有找到完整的 .dictionary 文件夹。"

/bin/mkdir -p "$INSTALL_DIR"
destination="$INSTALL_DIR/$DICTIONARY_NAME"

if [[ -e "$destination" ]]; then
    backup_dir="$INSTALL_DIR/ECDICT Backups"
    timestamp="$(/bin/date '+%Y%m%d-%H%M%S')"
    backup_path="$backup_dir/ECDICT 简明英汉字典-$timestamp.dictionary"
    /bin/mkdir -p "$backup_dir"
    /bin/mv "$destination" "$backup_path"
    printf '旧版本已备份到：%s\n' "$backup_path"
fi

/usr/bin/ditto --noextattr --norsrc "$dictionary_path" "$destination" \
    || fail "无法复制词典到 $INSTALL_DIR。"
/usr/bin/touch "$INSTALL_DIR"
if [[ "${ECDICT_SKIP_RESTART:-0}" != "1" ]]; then
    /usr/bin/killall Dictionary >/dev/null 2>&1 || true
fi

printf '\n安装完成：%s\n' "$destination"
printf '请重新打开“词典”App，进入“设置…”（Command-,）：\n'
printf '  1. 勾选“ECDICT 简明英汉字典”；\n'
printf '  2. 同时勾选至少一个 macOS 系统自带词典；\n'
printf '  3. 搜索 two 确认释义可以正常显示。\n'
