#!/bin/bash
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="helium-browser.spec"
GITHUB_REPO="imputnet/helium-linux"
PACKAGER="Ackerman-00 <no-reply>"

api() {
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        curl -sfL -H "Authorization: token $GITHUB_TOKEN" "$@"
    else
        curl -sfL "$@"
    fi
}

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(api "https://api.github.com/repos/$GITHUB_REPO/releases?per_page=30" \
    | python3 -c '
import json, re, sys
asset = re.compile(r"^helium-[0-9][^-]*-x86_64_linux\.tar\.xz$")
for rel in json.load(sys.stdin):
    if rel.get("draft") or rel.get("prerelease"):
        continue
    if any(asset.match(a.get("name", "")) for a in rel.get("assets", [])):
        print(rel["tag_name"].lstrip("v"))
        break
' 2>/dev/null)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: no release on $GITHUB_REPO carries a helium-*-x86_64_linux.tar.xz asset."
    exit 1
fi

CURRENT_VERSION=$(awk '/^Version:/{print $2; exit}' "$SPEC_FILE")

if [ "$CURRENT_VERSION" = "$LATEST_TAG" ]; then
    echo "Already up to date ($CURRENT_VERSION)."
    exit 0
fi

echo "Update found: $CURRENT_VERSION -> $LATEST_TAG"

ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/helium-$LATEST_TAG-x86_64_linux.tar.xz"
TREE="helium-$LATEST_TAG-x86_64_linux"
TMPDIR=$(mktemp -d) || exit 1
trap 'rm -rf "$TMPDIR"' EXIT

if ! api -o "$TMPDIR/helium.tar.xz" "$ASSET_URL"; then
    echo "  -> [SKIP] release asset for $LATEST_TAG is not downloadable yet; keeping $CURRENT_VERSION."
    exit 0
fi

SHA=$(sha256sum "$TMPDIR/helium.tar.xz" | awk '{print $1}')
[ ${#SHA} -eq 64 ] || { echo "Error: sha256 of $ASSET_URL failed."; exit 1; }

if ! tar tf "$TMPDIR/helium.tar.xz" | grep -qx "$TREE/"; then
    echo "Error: $ASSET_URL does not contain the expected $TREE/ tree."
    exit 1
fi

tar xf "$TMPDIR/helium.tar.xz" -C "$TMPDIR" "$TREE"
BIN_VER=$("$TMPDIR/$TREE/helium" --version 2>/dev/null | head -1)
INTERNAL=$(sed -n 's/^Helium \([0-9][0-9.]*\).*/\1/p' <<< "$BIN_VER")
CHROMIUM=$(sed -n 's/.*Chromium \([0-9][0-9.]*\).*/\1/p' <<< "$BIN_VER")
if [ -n "$INTERNAL" ] && [ "$INTERNAL" != "$LATEST_TAG" ]; then
    echo "Error: $ASSET_URL ships $INTERNAL but the release tag is $LATEST_TAG." >&2
    exit 1
fi

sed -i -E "s/^Version:.*/Version:        $LATEST_TAG/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s/^# sha256: [0-9a-f]{64}$/# sha256: $SHA/" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $LATEST_TAG-1"
    if [ -n "$CHROMIUM" ]; then
        echo "- Update to upstream release $LATEST_TAG (Chromium $CHROMIUM, read from the"
        echo "  shipped binary with --version; tarball sha256 verified)"
    else
        echo "- Update to upstream release $LATEST_TAG"
    fi
} >> "$SPEC_FILE"

grep -q "^Name:" "$SPEC_FILE" || {
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
}

echo "Bumped $CURRENT_VERSION -> $LATEST_TAG (sha256 $SHA), internal version ${INTERNAL:-unread}."
