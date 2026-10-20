#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="splayer-next.spec"
GITHUB_REPO="SPlayer-Dev/SPlayer-Next"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

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

RPM_URL="https://github.com/$GITHUB_REPO/releases/download/v${LATEST_VERSION}/splayer-next-${LATEST_VERSION}-x86_64.rpm"
echo "  -> [CHECK] Verifying $RPM_URL"
if ! curl --output /dev/null --silent --location --head --fail "$RPM_URL"; then
    echo "  -> [SKIP] Upstream x86_64 RPM for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

echo "  -> [NOTE] Re-verify the bundled electron/better-sqlite3 versions,"
echo "            the sha256 comment, and the readelf NEEDED set in"
echo "            $SPEC_FILE against the new artifact:"
echo "            rpm2cpio splayer-next-${LATEST_VERSION}-x86_64.rpm | cpio -idm"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_ENTRY="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to upstream release $LATEST_TAG\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
    sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
    printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
