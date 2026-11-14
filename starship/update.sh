#!/bin/bash

# owner 2026-11-14: auto-update disabled; updates are published by Ackerman-00
if [ -z "${NEXUS_OWNER_UPDATE:-}" ]; then
    echo "auto-update disabled (owner rule 2026-11-14); updates are published manually by Ackerman-00"
    exit 0
fi
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="starship.spec"
GITHUB_REPO="starship/starship"
PACKAGER="Ackerman-00 <no-reply>"
PATCH_FILE="starship-gix-0.90.patch"
GIX_FIXED="0.90.0"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(gh api "repos/$GITHUB_REPO/releases/latest" --cache 3600s --jq .tag_name 2>/dev/null)
if [ -z "$LATEST_TAG" ]; then
    LATEST_TAG=$(curl -sL --max-time 30 "https://api.github.com/repos/$GITHUB_REPO/releases/latest" \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name',''))" 2>/dev/null)
fi
if [ -z "$LATEST_TAG" ]; then
    echo "Error: failed to fetch the latest release tag."
    exit 1
fi

VERSION=${LATEST_TAG#v}
CURRENT_VERSION=$(awk '/^Version:/{print $2; exit}' "$SPEC_FILE")

if [ "$CURRENT_VERSION" = "$VERSION" ]; then
    echo "Package is already at the latest version ($VERSION). No update needed."
    exit 0
fi

echo "Updating: $CURRENT_VERSION -> $VERSION"

TMPDIR=$(mktemp -d) || exit 1
trap 'rm -rf "$TMPDIR"' EXIT

ARCHIVE_URL="https://github.com/$GITHUB_REPO/archive/refs/tags/v$VERSION.tar.gz"
if ! curl -sL --max-time 180 --fail -o "$TMPDIR/src.tar.gz" "$ARCHIVE_URL"; then
    echo "Error: $ARCHIVE_URL did not download."
    exit 1
fi
SHA256=$(sha256sum "$TMPDIR/src.tar.gz" | awk '{print $1}')

GIX_VERSION=$(tar xzf "$TMPDIR/src.tar.gz" -O "starship-$VERSION/Cargo.toml" 2>/dev/null \
    | awk -F'"' '/^gix = /{print $2; exit}')

sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
sed -i -E "s|^Release:.*|Release:        1%{?dist}|" "$SPEC_FILE"
sed -i "0,/^# sha256:.*/s|^# sha256:.*|# sha256:  $SHA256|" "$SPEC_FILE"

if [ -n "$GIX_VERSION" ] && [ "$(printf '%s\n%s\n' "$GIX_FIXED" "$GIX_VERSION" | sort -V | head -1)" = "$GIX_FIXED" ]; then
    echo "Upstream ships gix $GIX_VERSION (>= $GIX_FIXED): the gix backport is no longer needed."
    sed -i '/^# GHSA-q54r-jf2p-rfr2$/d; /^Patch0: *starship-gix-0.90.patch$/d' "$SPEC_FILE"
    rm -f "$PATCH_FILE"
else
    echo "Upstream ships gix ${GIX_VERSION:-unknown}: keeping the gix backport."
    grep -q '^Patch0:' "$SPEC_FILE" || sed -i "s|^Source0:.*|&\n# GHSA-q54r-jf2p-rfr2\nPatch0:         $PATCH_FILE|" "$SPEC_FILE"
fi

sed -i '/^%changelog/,$d' "$SPEC_FILE"
cat >> "$SPEC_FILE" <<EOF
%changelog
* $(date -u '+%a %b %d %Y') $PACKAGER - $VERSION-1
- Update to version $VERSION
EOF

echo "Successfully patched $SPEC_FILE to $VERSION (sha256 $SHA256)."
