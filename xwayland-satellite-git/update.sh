#!/bin/bash

SPEC_FILE="xwayland-satellite-git.spec"
GITHUB_REPO="Supreeeme/xwayland-satellite"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
BASE_VER="0.8.1"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Set up header array for API extraction
API_HEADERS=()
if [ -n "$GITHUB_TOKEN" ]; then
    API_HEADERS+=(-H "Authorization: token $GITHUB_TOKEN")
fi

# Fetch the absolute latest commit payload from the main branch
RESPONSE=$(curl -sL "${API_HEADERS[@]}" "https://api.github.com/repos/$GITHUB_REPO/commits/main")

LATEST_COMMIT=$(echo "$RESPONSE" | jq -r '.sha // empty')
COMMIT_DATE_RAW=$(echo "$RESPONSE" | jq -r '.commit.committer.date // empty')

if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Error: Failed to fetch Xwayland-Satellite payload from GitHub. Check API limits or connection."
    exit 1
fi

# Clean the ISO 8601 timestamp (2026-06-05T05:28:52Z -> 20260605052852)
GIT_DATE=$(echo "$COMMIT_DATE_RAW" | tr -d '\-TZ:')
SHORT_COMMIT=${LATEST_COMMIT:0:7}

# Grab the current commit from the spec file to compare
CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ]; then
    echo "Update found: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"
    echo "Commit Timestamp: $GIT_DATE"
    
    # 1. Update the Commit metadata and reset Release fields
    sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
    sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    
    # 2. Auto-generate the Changelog entry matching your multi-commit nightly layout
    DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
    CHANGELOG_VER="${BASE_VER}^${GIT_DATE}git${SHORT_COMMIT}-1"
    
    awk -v date="$DATE_STRING" -v pkg="$PACKAGER" -v ver="$CHANGELOG_VER" -v commit="$SHORT_COMMIT" '
    /^%changelog/ {
        print $0
        print "* " date " " pkg " - " ver
        print "- Nightly sync with upstream main branch (Commit: " commit ")"
        print ""
        next
    }
    { print $0 }
    ' "$SPEC_FILE" > "${SPEC_FILE}.tmp" && mv "${SPEC_FILE}.tmp" "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE."
else
    echo "✅ Package is already at the latest commit ($SHORT_COMMIT). No update needed."
fi
