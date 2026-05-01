#!/bin/bash

SPEC_FILE="scenefx.spec"
GITHUB_REPO="wlrfx/scenefx"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Fetch the latest release tag from GitHub API
# Inject GITHUB_TOKEN if available to bypass the strict 60/hr API rate limit
if [ -n "$GITHUB_TOKEN" ]; then
    LATEST_VERSION=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v?([^"]+)".*/\1/')
else
    LATEST_VERSION=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v?([^"]+)".*/\1/')
fi

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch the latest version. Check API limits or connection."
    exit 1
fi

# Grab the current version from the spec file
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"
    
    # 1. Update the Version and Release fields
    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    # 2. Auto-generate the Changelog entry safely using awk
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    
    awk -v date="$DATE" -v pkg="$PACKAGER" -v ver="$LATEST_VERSION" '
    /^%changelog/ {
        print $0
        print "* " date " " pkg " - " ver "-1"
        print "- Auto-update to version " ver
        print ""
        next
    }
    { print $0 }
    ' "$SPEC_FILE" > "${SPEC_FILE}.tmp" && mv "${SPEC_FILE}.tmp" "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE."
else
    echo "✅ Package is already at $LATEST_VERSION. No update needed."
fi
