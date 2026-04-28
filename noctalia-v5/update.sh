#!/bin/bash

SPEC_FILE="noctalia-v5.spec"
GITHUB_REPO="noctalia-dev/noctalia-shell"
BRANCH="v5"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream commits on $GITHUB_REPO (Branch: $BRANCH)..."

# Fetch the latest commit hash and full timestamp from the v5 branch
LATEST_COMMIT=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/commits/$BRANCH" | grep '"sha":' | head -n 1 | cut -d '"' -f 4)

# FIX: Strip dashes, colons, T, and Z to create a purely ascending chronological integer (e.g., 20260428143200)
LATEST_DATE=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/commits/$BRANCH" | grep '"date":' | head -n 1 | cut -d '"' -f 4 | sed 's/[-T:Z]//g')

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: Failed to fetch the latest commit. Check API limits or connection."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

# Extract the current commit from the spec file
CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ]; then
    echo "New commit found: $SHORT_COMMIT (Timestamp: $LATEST_DATE)"
    
    # 1. Inject the new commit and the granular date into the globals
    sed -i "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
    sed -i "s/^%global gitdate.*/%global gitdate         $LATEST_DATE/" "$SPEC_FILE"
    
    # 2. Reset the Release field
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    # 3. Add Changelog entry
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    NEW_CHANGELOG="* $DATE $PACKAGER - 5.0.0^${LATEST_DATE}git${SHORT_COMMIT}-1\n- Nightly sync with upstream v5 branch (Commit: $SHORT_COMMIT)\n"
    sed -i "/^%changelog/a $NEW_CHANGELOG" "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE."
else
    echo "✅ Package is already tracking the latest commit ($SHORT_COMMIT). No update needed."
fi
