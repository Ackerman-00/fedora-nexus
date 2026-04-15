#!/bin/bash

# Fetch the absolute latest stable release tag directly from GitHub API
LATEST_TAG=$(curl -sL "https://api.github.com/repos/zen-browser/desktop/releases/latest" | jq -r '.tag_name')

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "Failed to fetch Zen Browser version from GitHub."
    exit 1
fi

# Copr/RPM spec files do not allow dashes in the Version field. Sanitize it.
ZEN_VER_SPEC=$(echo "$LATEST_TAG" | sed 's@-@.@g')

# New version and update the download URL path in the spec file
sed -i -E "s/^Version:\s+.*/Version:            $ZEN_VER_SPEC/" zen-browser.spec
sed -i -E "s|download/[^/]+/zen.linux-x86_64.tar.xz|download/$LATEST_TAG/zen.linux-x86_64.tar.xz|g" zen-browser.spec

echo "Zen Browser local check complete. Upstream is at $LATEST_TAG."
