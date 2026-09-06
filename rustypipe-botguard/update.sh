#!/bin/bash
# update.sh for rustypipe-botguard (Codeberg release tracking, prebuilt binary)
#
# This package MUST have its own updater. The generic release scanner in
# .github/workflows/update-engine.yml only rewrites "Version:" - it does not
# reset Release, does not add a %changelog entry, and does not refresh the
# pinned sha256. Packages with an update.sh are skipped by that scanner.

SPEC_FILE="rustypipe-botguard.spec"
CODEBERG_REPO="ThetaDev/rustypipe-botguard"
ASSET="rustypipe-botguard-x86_64-unknown-linux-gnu.tar.xz"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking Codeberg releases for $CODEBERG_REPO..."

LATEST_TAG=$(python3 -c "
import json,urllib.request
rels = json.load(urllib.request.urlopen('https://codeberg.org/api/v1/repos/$CODEBERG_REPO/releases?limit=5',timeout=20))
stable = [r['tag_name'] for r in rels if not r.get('draft') and not r.get('prerelease')]
print(stable[0] if stable else '')
" 2>/dev/null)
LATEST_VERSION=${LATEST_TAG#v}

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest release."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" == "$CURRENT_VERSION" ]; then
    echo "  -> [OK] Package is already at $CURRENT_VERSION. No update needed."
    exit 0
fi

echo "  -> [UPDATE] $CURRENT_VERSION -> $LATEST_VERSION"

# The spec pins the tarball sha256 - refresh it from the new asset. If the
# asset cannot be fetched, keep the old version (a 404 Source0 would fail
# every COPR build of the new NVR).
ASSET_URL="https://codeberg.org/$CODEBERG_REPO/releases/download/${LATEST_TAG}/rustypipe-botguard-${LATEST_VERSION}-x86_64-unknown-linux-gnu.tar.xz"
echo "  -> [CHECK] Verifying $ASSET_URL"
NEW_SHA=$(curl --silent --location --fail "$ASSET_URL" 2>/dev/null | sha256sum 2>/dev/null | awk '{print $1}')
if [ -z "$NEW_SHA" ]; then
    echo "  -> [SKIP] Upstream asset for $LATEST_TAG is not fetchable (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

# New upstream version -> Release restarts at 1 (rpm-version(7)).
sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s/^# sha256:.*/# sha256: $NEW_SHA/" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_ENTRY="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to upstream release $LATEST_TAG (sha256 refreshed)\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
    sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
    printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
