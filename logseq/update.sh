#!/bin/bash
# update.sh for Logseq (Repackaging Build)

SPEC_FILE="logseq.spec"
GITHUB_REPO="logseq/logseq"
ASSET_BASE="https://github.com/$GITHUB_REPO/releases/download"

echo "Checking for latest Logseq release..."

# Get latest stable tag via git ls-remote (no rate limit)
LATEST_VERSION=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

# Read current version from .spec
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

# Compare and update
if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    # Verify the Linux x86_64 zip source actually exists for this version
    ZIP_URL="${ASSET_BASE}/${LATEST_VERSION}/Logseq-linux-x86_64-${LATEST_VERSION}.zip"

    echo "  -> [CHECK] Verifying download link..."
    if ! curl --output /dev/null --silent --head --fail "$ZIP_URL"; then
        echo "  -> [ERROR] Linux x86_64 zip for $LATEST_VERSION is not yet available on GitHub. Skipping update."
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
    echo "  -> [OK] Logseq is already on latest ($CURRENT_VERSION)."
fi
