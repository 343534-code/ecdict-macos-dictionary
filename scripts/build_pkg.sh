#!/bin/bash

set -euo pipefail
export COPYFILE_DISABLE=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DICTIONARY_NAME="ECDICT 简明英汉字典.dictionary"
VERSION="${VERSION:-1.2.1}"
BUNDLE_PATH="${1:-$REPOSITORY_ROOT/dictionary-source/objects/$DICTIONARY_NAME}"
OUTPUT_PATH="${2:-$REPOSITORY_ROOT/dist/ECDICT-macOS-Dictionary-v$VERSION.pkg}"
PACKAGE_IDENTIFIER="com.ecdict.dictionary.installer"
SIGN_IDENTITY="${PKG_SIGN_IDENTITY:-}"
PACKAGE_SCRIPTS_SOURCE="$REPOSITORY_ROOT/packaging/scripts"

[[ "$(uname -s)" == "Darwin" ]] || {
    printf '此脚本仅支持 macOS。\n' >&2
    exit 1
}

[[ -d "$BUNDLE_PATH/Contents" ]] || {
    printf '找不到词典包：%s\n' "$BUNDLE_PATH" >&2
    exit 1
}

[[ -x "$PACKAGE_SCRIPTS_SOURCE/postinstall" ]] || {
    printf '找不到可执行的 PKG 安装后脚本：%s\n' "$PACKAGE_SCRIPTS_SOURCE/postinstall" >&2
    exit 1
}

work_dir="$(/usr/bin/mktemp -d "${TMPDIR:-/tmp}/ecdict-pkg.XXXXXX")"

cleanup() {
    if [[ -n "$work_dir" && -d "$work_dir" ]]; then
        /bin/rm -rf -- "$work_dir"
    fi
}

trap cleanup EXIT INT TERM

payload_root="$work_dir/payload"
install_dir="$payload_root/Library/Dictionaries"
package_scripts="$work_dir/scripts"
/bin/mkdir -p "$install_dir" "$(dirname "$OUTPUT_PATH")"
/usr/bin/ditto --noextattr --norsrc "$BUNDLE_PATH" "$install_dir/$DICTIONARY_NAME"
/usr/bin/ditto --noextattr --norsrc "$PACKAGE_SCRIPTS_SOURCE" "$package_scripts"
/usr/bin/xattr -cr "$payload_root" >/dev/null 2>&1 || true
/usr/bin/xattr -cr "$package_scripts" >/dev/null 2>&1 || true
/usr/bin/find "$payload_root" -type f -name '._*' -delete
/usr/bin/find "$package_scripts" -type f -name '._*' -delete

if [[ -n "$SIGN_IDENTITY" ]]; then
    COPYFILE_DISABLE=1 /usr/bin/pkgbuild \
        --root "$payload_root" \
        --identifier "$PACKAGE_IDENTIFIER" \
        --version "$VERSION" \
        --install-location / \
        --ownership recommended \
        --scripts "$package_scripts" \
        --sign "$SIGN_IDENTITY" \
        "$OUTPUT_PATH"
else
    COPYFILE_DISABLE=1 /usr/bin/pkgbuild \
        --root "$payload_root" \
        --identifier "$PACKAGE_IDENTIFIER" \
        --version "$VERSION" \
        --install-location / \
        --ownership recommended \
        --scripts "$package_scripts" \
        "$OUTPUT_PATH"
    printf '提示：未设置 PKG_SIGN_IDENTITY，生成的是未签名 PKG。\n' >&2
fi

printf '已生成：%s\n' "$OUTPUT_PATH"
