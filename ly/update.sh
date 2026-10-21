#!/bin/bash
# Tracks ly from its Codeberg forge (the GitHub mirror serves the archives).
set -u

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="ly.spec"
CODEBERG_REPO="fairyglade/ly"
PACKAGER="Nexus Auto-Updater <bot@github.com>"
ZIG_SERIES="0.17"

echo "Checking for upstream updates on codeberg.org/$CODEBERG_REPO..."

get_latest_tag() {
    local remote="$1"
    git ls-remote --tags "$remote" 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
}

LATEST_TAG=""
for attempt in 1 2 3; do
    LATEST_TAG=$(get_latest_tag "https://codeberg.org/$CODEBERG_REPO.git")
    [ -n "$LATEST_TAG" ] && break
    echo "  -> [RETRY] Codeberg ls-remote attempt $attempt failed, retrying..."
    sleep 5
done
[ -z "$LATEST_TAG" ] && LATEST_TAG=$(get_latest_tag "https://github.com/$CODEBERG_REPO.git")

if [ -z "$LATEST_TAG" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag." >&2
    exit 1
fi

LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo "  -> [OK] ly is already on latest ($CURRENT_VERSION)."
    exit 0
fi

echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

ARCHIVE_URL="https://github.com/$CODEBERG_REPO/archive/$LATEST_TAG.tar.gz"
echo "  -> [CHECK] Verifying $ARCHIVE_URL"
if ! curl --output /dev/null --silent --location --head --retry 3 --max-time 120 --fail "$ARCHIVE_URL"; then
    echo "  -> [SKIP] Source archive for $LATEST_TAG is not available (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

VENDOR_URL="https://codeberg.org/$CODEBERG_REPO/releases/download/$LATEST_TAG/vendor.tar.zst"
echo "  -> [CHECK] Verifying $VENDOR_URL"
if ! curl --output /dev/null --silent --location --head --retry 3 --max-time 120 --fail "$VENDOR_URL"; then
    echo "  -> [SKIP] Vendor tarball for $LATEST_TAG is not available (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

# The spec pins one zig0.17 build; a newer Zig series needs its own package first.
ZIG_FLOOR=$(curl --silent --location --retry 3 --max-time 60 \
    "https://raw.githubusercontent.com/$CODEBERG_REPO/$LATEST_TAG/build.zig.zon" \
    | sed -n 's/.*minimum_zig_version[^0-9]*\([0-9.]*[0-9]\).*/\1/p' | head -1)
if [ -n "$ZIG_FLOOR" ] && [ "${ZIG_FLOOR%.*}" != "$ZIG_SERIES" ]; then
    echo "  -> [HOLD] $LATEST_TAG needs Zig $ZIG_FLOOR; this spec builds with zig$ZIG_SERIES."
    echo "  -> [HOLD] Add a zig$ZIG_FLOOR toolchain package, then bump."
    exit 0
fi

echo "  -> [CHECK] Reading bundled Zig dependency versions..."
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
if ! curl --silent --location --retry 3 --max-time 180 --fail -o "$TMP_DIR/vendor.tar.zst" "$VENDOR_URL"; then
    echo "  -> [ERROR] Failed to download vendor tarball for version sync." >&2
    exit 1
fi
VENDOR_DIRS=$(tar --zstd -tf "$TMP_DIR/vendor.tar.zst" 2>/dev/null | sed -n 's|^zig-pkg/\([^/]*\)/$|\1|p')
[ -n "$VENDOR_DIRS" ] || { echo "  -> [ERROR] vendor tarball has no zig-pkg entries." >&2; exit 1; }

dep_version() {
    printf '%s\n' "$VENDOR_DIRS" | sed -n "s/^$1-\([0-9][0-9.]*\)-.*\$/\1/p" | head -1
}

for dep in clap zigini ini zlua; do
    ver=$(dep_version "$dep")
    if [ -z "$ver" ]; then
        echo "  -> [WARN] $dep is not in the $LATEST_TAG vendor bundle; keeping the pinned version."
        continue
    fi
    sed -i "s/^%global ${dep}_ver .*/%global ${dep}_ver $ver/" "$SPEC_FILE"
    echo "    -> [OK] $dep $ver"
done

sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
    echo "- Auto-update to upstream release $LATEST_TAG"
} >> "$SPEC_FILE"

echo "  -> [DONE] $SPEC_FILE is ready for build."

if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
