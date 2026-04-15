#!/bin/bash

# Fetch the absolute latest commit hash from the main branch
LATEST_COMMIT=$(curl -sL "https://api.github.com/repos/YaLTeR/niri/commits/main" | jq -r '.sha')

if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Failed to fetch Niri commit from GitHub."
    exit 1
fi

# Generate today's date for the version number
DATE_VER=$(date -u +%Y%m%d)

# Inject the new commit hash and date version into the spec file
sed -i -E "s/^%global commit\s+.*/%global commit          $LATEST_COMMIT/" niri-git.spec
sed -i -E "s/^Version:\s+.*/Version:        $DATE_VER/" niri-git.spec

echo "Niri local check complete. Upstream commit is $LATEST_COMMIT."
