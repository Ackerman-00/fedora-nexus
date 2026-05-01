#!/bin/bash

SPEC_FILE="zen-browser.spec"
GITHUB_REPO="zen-browser/desktop"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Fetch the absolute latest stable release tag directly from GitHub API
# Inject GITHUB_TOKEN if available to bypass the strict 60/hr API rate limit
if [ -n "$GITHUB_TOKEN" ]; then
    LATEST_TAG=$(curl -sL -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | jq -r '.tag_name')
else
    LATEST_TAG=$(curl -sL "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | jq -r '.tag_name')
fi

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "Error: Failed to fetch Zen Browser version from GitHub. Check API limits or connection."
    exit 1
fi

# Copr/RPM spec files do not allow dashes in the Version field. Sanitize it.
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's@-@.@g')

# Grab the current version from the spec file
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"
    
    # 1. Update the Version and Release fields
    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    # 2. Update the download URL path in the spec file with the RAW tag
    sed -i -E "s|download/[^/]+/zen.linux-x86_64.tar.xz|download/$LATEST_TAG/zen.linux-x86_64.tar.xz|g" "$SPEC_FILE"
    
    # 3. Auto-generate the Changelog entry safely using awk
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    
    awk -v date="$DATE" -v pkg="$PACKAGER" -v ver="$LATEST_VERSION" -v tag="$LATEST_TAG" '
    /^%changelog/ {
        print $0
        print "* " date " " pkg " - " ver "-1"
        print "- Auto-update to upstream release " tag
        print ""
        next
    }
    { print $0 }
    ' "$SPEC_FILE" > "${SPEC_FILE}.tmp" && mv "${SPEC_FILE}.tmp" "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE."
else
    echo "✅ Package is already at $LATEST_VERSION. No update needed."
fi
