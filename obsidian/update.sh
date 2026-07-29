#!/bin/bash
# update.sh for Obsidian (Repackaging Build)

SPEC_FILE="obsidian.spec"
GITHUB_REPO="obsidianmd/obsidian-releases"

echo "Checking for latest Obsidian release..."

# Get latest tag via git ls-remote (no rate limit)
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

# Read current version from .spec
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

# Compare and update
if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    # Verify the .deb source actually exists for this version
    DEB_URL="https://github.com/$GITHUB_REPO/releases/download/v${LATEST_VERSION}/obsidian_${LATEST_VERSION}_amd64.deb"
    
    echo "  -> [CHECK] Verifying download link..."
    if ! curl --output /dev/null --silent --head --fail "$DEB_URL"; then
        echo "  -> [ERROR] .deb file for $LATEST_VERSION is not yet available on GitHub. Skipping update."
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
    echo "  -> [OK] Obsidian is already on latest ($CURRENT_VERSION)."
fi
