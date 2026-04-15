#!/bin/bash

# Fetch the absolute latest commit hash from the main branch
LATEST_COMMIT=$(curl -sL "https://api.github.com/repos/Supreeeme/xwayland-satellite/commits/main" | jq -r '.sha')

if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Failed to fetch Xwayland-Satellite commit from GitHub."
    exit 1
fi

# Generate today's date for the version number (e.g., 20260415)
DATE_VER=$(date -u +%Y%m%d)

# Inject the new commit hash and date version into the spec file
sed -i -E "s/^%global commit\s+.*/%global commit          $LATEST_COMMIT/" xwayland-satellite-git.spec
sed -i -E "s/^Version:\s+.*/Version:        $DATE_VER/" xwayland-satellite-git.spec

echo "Xwayland-Satellite local check complete. Upstream commit is $LATEST_COMMIT."
