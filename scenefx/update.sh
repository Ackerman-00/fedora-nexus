#!/bin/bash

SPEC_FILE="scenefx.spec"
GITHUB_REPO="wlrfx/scenefx"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_VERSION=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v?([^"]+)".*/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch the latest version. Check API limits or connection."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"
    
    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    NEW_CHANGELOG="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to version $LATEST_VERSION\n"
    
    sed -i "/^%changelog/a $NEW_CHANGELOG" "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE."
else
    echo "✅ Package is already at $LATEST_VERSION. No update needed."
fi
