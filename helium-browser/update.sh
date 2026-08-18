#!/bin/bash
# update.sh for Helium Browser (Repackaging Build)

SPEC_FILE="helium-browser.spec"
GITHUB_REPO="imputnet/helium-linux"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest tag via git ls-remote (no rate limit)
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?$' | sort -V | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

LATEST_VERSION="$LATEST_TAG"

# Read current version from the spec file
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

# Compare and update
if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    # A tag can exist before its release assets do: helium's release workflow
    # uploads the tarballs at the end. Bumping on a tag whose asset is missing
    # produces a spec whose Source0 404s, so every COPR rebuild of that NVR
    # fails. Only bump once the tarball really exists.
    TARBALL_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_VERSION/helium-$LATEST_VERSION-x86_64_linux.tar.xz"
    echo "  -> [CHECK] Verifying $TARBALL_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$TARBALL_URL"; then
        echo "  -> [ERROR] Linux x86_64 tarball for $LATEST_VERSION is not yet available on GitHub. Skipping update."
        exit 1
    fi

    # 1. Update the Version and Release fields
    sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # 2. Replace changelog with single entry
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_TAG"
    } >> "$SPEC_FILE"

    echo "  -> [DONE] $SPEC_FILE is ready for build."
else
    echo "  -> [OK] Helium is already on latest ($CURRENT_VERSION)."
fi

# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
