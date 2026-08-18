#!/bin/bash

SPEC_FILE="cascadia-code-nerd-fonts.spec"
GITHUB_REPO="ryanoasis/nerd-fonts"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest release tag via GitHub API (tags without a release must be ignored).
# Use GITHUB_TOKEN when available to avoid unauthenticated rate limits.
if [ -n "$GITHUB_TOKEN" ]; then
    LATEST_TAG=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tag_name',''))")
else
    LATEST_TAG=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tag_name',''))")
fi
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch latest release."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    # A release can exist before all of its assets finished uploading (nerd-fonts
    # publishes ~70 archives one by one). Bumping onto a version whose archive is
    # missing pins a Source0 that 404s and breaks every rebuild of that NVR.
    ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/v${LATEST_VERSION}/CascadiaCode.tar.xz"
    echo "  -> [CHECK] Verifying $ASSET_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$ASSET_URL"; then
        echo "  -> [SKIP] Release asset for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to version $LATEST_VERSION"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at $LATEST_VERSION. No update needed."
fi
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
