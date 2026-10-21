#!/bin/bash
# Tracks the 0.17 series from ziglang.org/download/index.json.
set -u

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="zig0.17.spec"
PACKAGER="Nexus Auto-Updater <bot@github.com>"
SERIES="0.17"
ARCH="x86_64-linux"

CURRENT_VERSION=$(sed -n 's/^Version:\s*//p' "$SPEC_FILE" | head -1)
echo "Checking ziglang.org for the newest $SERIES release (current: $CURRENT_VERSION)..."

INDEX=$(curl --silent --location --retry 3 --max-time 120 \
    https://ziglang.org/download/index.json) || {
    echo "  -> [ERROR] could not read the release index." >&2
    exit 1
}

LATEST=$(printf '%s' "$INDEX" | python3 -c '
import json, sys
series = sys.argv[1]
index = json.load(sys.stdin)
versions = [v for v in index if v.startswith(series + ".")]
def key(v):
    return tuple(int(p) for p in v.split("."))
print(max(versions, key=key) if versions else "")
' "$SERIES")

if [ -z "$LATEST" ]; then
    echo "  -> [ERROR] no $SERIES release in the index." >&2
    exit 1
fi

if [ "$LATEST" = "$CURRENT_VERSION" ]; then
    echo "  -> [OK] zig0.17 is already on $CURRENT_VERSION."
    exit 0
fi

URL="https://ziglang.org/download/$LATEST/zig-$ARCH-$LATEST.tar.xz"
echo "  -> [UPDATE] $CURRENT_VERSION -> $LATEST"
if ! SHA=$(curl --silent --location --retry 3 --max-time 300 --fail "$URL" | sha256sum | awk '{print $1}'); then
    echo "  -> [ERROR] could not download $URL" >&2
    exit 1
fi
[ ${#SHA} -eq 64 ] || { echo "  -> [ERROR] bad sha256 for $URL" >&2; exit 1; }

sed -i "s|^Version:\s*.*|Version:        $LATEST|" "$SPEC_FILE"
sed -i "s|^Release:\s*.*|Release:        1%{?dist}|" "$SPEC_FILE"
sed -i "s|^# sha256: .*|# sha256: $SHA|" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $LATEST-1"
    echo "- Update to the $LATEST Zig toolchain release"
    echo "  (sha256: $SHA)"
} >> "$SPEC_FILE"

echo "  -> [DONE] $SPEC_FILE is ready for build."
grep -q "^Name:" "$SPEC_FILE" || {
    echo "FATAL: $SPEC_FILE lost its Name: header during update" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
}
