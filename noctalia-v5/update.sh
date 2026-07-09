#!/bin/bash

SPEC_FILE="noctalia-v5.spec"
GITHUB_REPO="noctalia-dev/noctalia"
BRANCH="main"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream commits on $GITHUB_REPO (Branch: $BRANCH)..."

# Fetch the latest commit data from the main branch
# Inject GITHUB_TOKEN if available to bypass the strict 60/hr API rate limit
if [ -n "$GITHUB_TOKEN" ]; then
    API_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/commits/$BRANCH")
else
    API_RESPONSE=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/commits/$BRANCH")
fi

# Extract SHA and Timestamp using jq to halve our API calls
LATEST_COMMIT=$(echo "$API_RESPONSE" | jq -r '.sha')
LATEST_DATE_RAW=$(echo "$API_RESPONSE" | jq -r '.commit.committer.date')

if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Error: Failed to fetch the latest commit. Check API limits or connection."
    exit 1
fi

# Strip dashes, colons, T, and Z to create a purely ascending chronological integer (e.g., 20260428143200)
LATEST_DATE=$(echo "$LATEST_DATE_RAW" | sed 's/[-T:Z]//g')
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
    
    # 3. Wipe out old logs below %changelog and replace with the single new entry
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - 5.0.0^${LATEST_DATE}git${SHORT_COMMIT}-1"
        echo "- Nightly sync with upstream main branch (Commit: ${SHORT_COMMIT})"
    } >> "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE and replaced the changelog history."
else
    echo "✅ Package is already tracking the latest commit ($SHORT_COMMIT). No update needed."
fi
