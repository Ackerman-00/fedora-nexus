#!/bin/bash

SPEC_FILE="xwayland-satellite-git.spec"
GITHUB_REPO="Supreeeme/xwayland-satellite"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Fetch the absolute latest commit hash from the main branch
# Inject GITHUB_TOKEN if available to bypass the strict 60/hr API rate limit
if [ -n "$GITHUB_TOKEN" ]; then
    LATEST_COMMIT=$(curl -sL -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/commits/main" | jq -r '.sha')
else
    LATEST_COMMIT=$(curl -sL "https://api.github.com/repos/$GITHUB_REPO/commits/main" | jq -r '.sha')
fi

if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Error: Failed to fetch Xwayland-Satellite commit from GitHub. Check API limits or connection."
    exit 1
fi

# Grab the current commit from the spec file
CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ]; then
    echo "Update found: $CURRENT_COMMIT -> $LATEST_COMMIT"
    
    # Generate today's date for the version number and grab the short commit
    DATE_VER=$(date -u +%Y%m%d)
    SHORT_COMMIT=${LATEST_COMMIT:0:7}
    
    # 1. Update the Commit, Version, and Release fields
    sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
    sed -i -E "s/^Version:.*/Version:        $DATE_VER/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    # 2. Auto-generate the Changelog entry safely using awk
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    
    awk -v date="$DATE" -v pkg="$PACKAGER" -v ver="$DATE_VER" -v commit="$SHORT_COMMIT" '
    /^%changelog/ {
        print $0
        print "* " date " " pkg " - " ver "-1"
        print "- Nightly sync with upstream main branch (Commit: " commit ")"
        print ""
        next
    }
    { print $0 }
    ' "$SPEC_FILE" > "${SPEC_FILE}.tmp" && mv "${SPEC_FILE}.tmp" "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE."
else
    echo "✅ Package is already at the latest commit (${LATEST_COMMIT:0:7}). No update needed."
fi
