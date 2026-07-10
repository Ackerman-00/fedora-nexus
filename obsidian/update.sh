#!/bin/bash
# update.sh for Obsidian (Repackaging Build)

SPEC_FILE="obsidian.spec"

echo "🔍 Checking for latest Obsidian release..."

# 1. Fetch latest version from GitHub API
# Using a User-Agent is good practice to avoid rate-limiting
LATEST_VERSION=$(curl -s -H "User-Agent: Fedora-Update-Script" https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | jq -r .tag_name | sed 's/^v//')

if [ -z "$LATEST_VERSION" ] || [ "$LATEST_VERSION" == "null" ]; then
    echo "  -> [ERROR] Failed to fetch latest version from GitHub API."
    exit 1
fi

# 2. Read current version from .spec
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

# 3. Compare and update
if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    # 4. CRITICAL: Verify the .deb source actually exists for this version
    # This prevents your COPR from failing with a 404
    DEB_URL="https://github.com/obsidianmd/obsidian-releases/releases/download/v${LATEST_VERSION}/obsidian_${LATEST_VERSION}_amd64.deb"
    
    echo "  -> [CHECK] Verifying download link..."
    if ! curl --output /dev/null --silent --head --fail "$DEB_URL"; then
        echo "  -> [ERROR] .deb file for $LATEST_VERSION is not yet available on GitHub. Skipping update."
        exit 1
    fi

    echo "  -> [ACTION] Updating $SPEC_FILE..."
    
    # Update Version and Reset Release to 1
    # Note: Using exact spacing to match your clean .spec file
    sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    # 5. Replace changelog with single entry
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
