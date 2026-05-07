#!/bin/bash
# update.sh for Obsidian

SPEC_FILE="obsidian.spec"

echo "Checking for latest Obsidian release..."

# 1. Fetch the latest release tag from the GitHub API
# We use jq to parse the JSON and strip the 'v' prefix (e.g., v1.15.2 -> 1.15.2)
LATEST_VERSION=$(curl -s https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | jq -r .tag_name | sed 's/^v//')

if [ -z "$LATEST_VERSION" ] || [ "$LATEST_VERSION" == "null" ]; then
    echo "  -> [ERROR] Failed to fetch latest version from GitHub API."
    exit 1
fi

# 2. Read the current version from the .spec file
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

# 3. Compare and update if necessary
if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "  -> [UPDATE] Obsidian changed from $CURRENT_VERSION to $LATEST_VERSION!"
    
    # Update the Version field
    sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    
    # Reset the Release field back to 1
    sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    # Add a new changelog entry at the top of the %changelog section
    DATE_STR=$(date +"%a %b %d %Y")
    CHANGELOG_ENTRY="* $DATE_STR Ackerman-00 <quietcraft@gmail.com> - $LATEST_VERSION-1\n- Auto-updated to $LATEST_VERSION\n"
    sed -i "/^%changelog/a $CHANGELOG_ENTRY" "$SPEC_FILE"
else
    echo "  -> [OK] Obsidian is already on latest ($CURRENT_VERSION)."
fi
