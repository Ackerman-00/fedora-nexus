#!/bin/bash
# update.sh for Freebuff Desktop (Repackaging Build)

SPEC_FILE="freebuff.spec"
GITHUB_REPO="CodebuffAI/codebuff-community"
TAG_PREFIX="freebuff-desktop-v"

echo "Checking for latest Freebuff Desktop release..."

# The desktop app is only one of several products in this repo, so releases/latest
# points at the Codebuff CLI. Filter tags by the desktop release prefix instead.
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E "^${TAG_PREFIX}[0-9]" | sort -uV | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed "s/^${TAG_PREFIX}//")

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

# Read current version from .spec
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

# Compare and update
if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    # Verify the AppImage asset actually exists for this version
    ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/${TAG_PREFIX}${LATEST_VERSION}/Freebuff-${LATEST_VERSION}-linux-x86_64.AppImage"

    echo "  -> [CHECK] Verifying download link..."
    if ! curl -L --output /dev/null --silent --head --fail "$ASSET_URL"; then
        echo "  -> [ERROR] AppImage asset for $LATEST_VERSION is not yet available on GitHub. Skipping update."
        exit 1
    fi

    echo "  -> [ACTION] Updating $SPEC_FILE..."

    # Update Version and Reset Release to 1
    sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # Replace changelog with single entry
    DATE_STR=$(date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE_STR Ackerman-00 <quietcraft@gmail.com> - $LATEST_VERSION-1"
        echo "- Auto-updated to $LATEST_VERSION via update.sh"
    } >> "$SPEC_FILE"

    echo "  -> [DONE] $SPEC_FILE is ready for build."
else
    echo "  -> [OK] Freebuff Desktop is already on latest ($CURRENT_VERSION)."
fi