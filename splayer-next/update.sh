#!/bin/bash
# update.sh for SPlayer-Next (repackages the upstream RPM)
#
# This package MUST have its own updater. The generic release scanner in
# .github/workflows/update-engine.yml only rewrites "Version:" - it does not
# reset Release, does not add a %changelog entry, and does not check that the
# release asset exists. Packages with an update.sh are skipped by that
# scanner, so this script is also the fix for that class of bug here.

SPEC_FILE="splayer-next.spec"
GITHUB_REPO="SPlayer-Dev/SPlayer-Next"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest stable tag via git ls-remote (no rate limit).
# Deliberately numeric X.Y.Z only: dev-branch prereleases such as
# 1.2.0-alpha.1 never match and are never picked up.
LATEST_TAG=$(git ls-remote --tags "https://github.com/$GITHUB_REPO.git" 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' \
    | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)
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

# Upstream publishes several Linux artifacts per release (.rpm/.deb/
# .AppImage/.tar.gz/.pacman for x86_64+aarch64). This spec repackages the
# x86_64 RPM, so confirm that exact asset exists before bumping - otherwise
# the new Source0 404s and fails every COPR build of that NVR.
RPM_URL="https://github.com/$GITHUB_REPO/releases/download/v${LATEST_VERSION}/splayer-next-${LATEST_VERSION}-x86_64.rpm"
echo "  -> [CHECK] Verifying $RPM_URL"
if ! curl --output /dev/null --silent --location --head --fail "$RPM_URL"; then
    echo "  -> [SKIP] Upstream x86_64 RPM for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

# New upstream version -> Release restarts at 1 (rpm-version(7)).
sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

# The bundled() Provides and the sha256 comment describe binaries shipped
# INSIDE the upstream RPM, so they cannot be guessed - they are only correct
# after someone tears the new artifact apart. Flag that instead of silently
# keeping stale values.
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
