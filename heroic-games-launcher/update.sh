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

SPEC_FILE="heroic-games-launcher.spec"
GITHUB_REPO="Heroic-Games-Launcher/HeroicGamesLauncher"
PACKAGER="Ackerman-00 <no-reply>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(git ls-remote --tags "https://github.com/$GITHUB_REPO.git" 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' \
    | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' | sed -E 's/^v?([0-9].*)/\1 &/' | sort -V -k1,1 | tail -1 | awk '{print $2}')
LATEST_VERSION=${LATEST_TAG#v}

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" == "$CURRENT_VERSION" ]; then
    echo "  -> [OK] Package is already at $CURRENT_VERSION. No update needed."
    exit 0
fi

echo "  -> [UPDATE] $CURRENT_VERSION -> $LATEST_VERSION"

RPM_URL="https://github.com/$GITHUB_REPO/releases/download/v${LATEST_VERSION}/Heroic-${LATEST_VERSION}-linux-x86_64.rpm"
echo "  -> [CHECK] Verifying $RPM_URL"
TMP_RPM=$(mktemp /tmp/heroic-bump.XXXXXX.rpm)
if ! curl --output "$TMP_RPM" --silent --location --fail "$RPM_URL"; then
    rm -f "$TMP_RPM"
    echo "  -> [SKIP] Upstream RPM for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
    exit 0
fi
SHA256=$(sha256sum "$TMP_RPM" | awk '{print $1}')
rm -f "$TMP_RPM"
echo "  -> [SHA256] $SHA256"

sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
if grep -q '^# sha256:' "$SPEC_FILE"; then
    sed -i -E "s/^# sha256:.*/# sha256: $SHA256/" "$SPEC_FILE"
else
    sed -i -E "\|^Source0:|i # sha256: $SHA256" "$SPEC_FILE"
fi

echo "  -> [NOTE] Re-check the bundled legendary/gogdl/nile/comet versions in"
echo "            $SPEC_FILE against the new artifact:"
echo "            rpm2cpio Heroic-${LATEST_VERSION}-linux-x86_64.rpm | cpio -idm"
echo "            then run each binary in build/bin/x64/linux with --version."

DATE=$(LC_ALL=C date +"%a %b %d %Y")
if sed -n '/^%changelog/,$p' "$SPEC_FILE" | grep -q '^\*'; then
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
fi
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
    echo "- Auto-update to upstream release $LATEST_TAG"
} >> "$SPEC_FILE"

echo "  -> [DONE] Successfully patched $SPEC_FILE."
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
