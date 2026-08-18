#!/bin/bash
# update.sh for Heroic Games Launcher (repackages the upstream RPM)
#
# This package MUST have its own updater. The generic release scanner in
# .github/workflows/update-engine.yml only rewrites "Version:" - it does not
# reset Release, does not add a %changelog entry, and does not check that the
# release asset exists. That is exactly how commit ac57abe produced a spec at
# "2.22.1" with a stale "Release: 3" and a changelog whose newest entry still
# said 2.22.0-3. Packages with an update.sh are skipped by that scanner, so
# this script is also the fix for that class of bug here.

SPEC_FILE="heroic-games-launcher.spec"
GITHUB_REPO="Heroic-Games-Launcher/HeroicGamesLauncher"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest tag via git ls-remote (no rate limit)
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

# Upstream tags the repo before the release RPM is uploaded (and 2.22.1 was
# tagged days before its asset appeared). Bumping onto a tag whose RPM is
# missing pins a Source0 that 404s, which fails every COPR build of that NVR.
RPM_URL="https://github.com/$GITHUB_REPO/releases/download/v${LATEST_VERSION}/Heroic-${LATEST_VERSION}-linux-x86_64.rpm"
echo "  -> [CHECK] Verifying $RPM_URL"
if ! curl --output /dev/null --silent --location --head --fail "$RPM_URL"; then
    echo "  -> [SKIP] Upstream RPM for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

# New upstream version -> Release restarts at 1 (rpm-version(7)).
sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

# The bundled() Provides describe binaries shipped INSIDE the upstream RPM, so
# they cannot be guessed - they are only correct after someone reads them out
# of the new artifact. Flag that instead of silently keeping stale values.
echo "  -> [NOTE] Re-check the bundled legendary/gogdl/nile/comet versions in"
echo "            $SPEC_FILE against the new artifact:"
echo "            rpm2cpio Heroic-${LATEST_VERSION}-linux-x86_64.rpm | cpio -idm"
echo "            then run each binary in build/bin/x64/linux with --version."

DATE=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_ENTRY="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to upstream release $LATEST_TAG\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
    sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
    printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
