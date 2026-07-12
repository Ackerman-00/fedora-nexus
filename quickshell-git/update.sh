#!/bin/bash

SPEC_FILE="quickshell-git.spec"
FORGEJO_REPO="quickshell/quickshell"
FORGEJO_HOST="git.outfoxxed.me"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
BASE_VER="0.3.0"

echo "Checking for upstream updates on $FORGEJO_HOST/$FORGEJO_REPO..."

# Fetch the latest commit from the master branch via Forgejo API
RESPONSE=$(curl -sL "https://$FORGEJO_HOST/api/v1/repos/$FORGEJO_REPO/commits?sha=master&limit=1")

LATEST_COMMIT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['sha'])")
COMMIT_DATE_RAW=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['commit']['committer']['date'])")

if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Error: Failed to fetch quickshell payload from $FORGEJO_HOST. Check API limits or connection."
    exit 1
fi

# Clean the ISO 8601 timestamp (2026-07-10T01:58:38-07:00 -> 20260710015838)
GIT_DATE=$(echo "$COMMIT_DATE_RAW" | sed 's/[^0-9]//g' | cut -c1-14)
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

    # 2. Replace changelog with single entry
    DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
    CHANGELOG_VER="${BASE_VER}^${GIT_DATE}git${SHORT_COMMIT}-1"
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE_STRING $PACKAGER - $CHANGELOG_VER"
        echo "- Nightly sync with upstream master branch (Commit: $SHORT_COMMIT)"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at the latest commit ($SHORT_COMMIT). No update needed."
fi
