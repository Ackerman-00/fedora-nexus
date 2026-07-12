#!/bin/bash

SPEC_FILE="app2unit.spec"
GITHUB_REPO="Vladimir-csp/app2unit"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
BASE_VER="1.0.0"

echo "Checking for upstream updates on $GITHUB_REPO..."

if [ -n "$GITHUB_TOKEN" ]; then
    RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/commits?sha=master&per_page=1")
else
    RESPONSE=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/commits?sha=master&per_page=1")
fi

LATEST_COMMIT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['sha'])")
COMMIT_DATE_RAW=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['commit']['committer']['date'])")

if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Error: Failed to fetch commits from $GITHUB_REPO. Check API limits or connection."
    exit 1
fi

GIT_DATE=$(echo "$COMMIT_DATE_RAW" | sed 's/[^0-9]//g' | cut -c1-14)
SHORT_COMMIT=${LATEST_COMMIT:0:7}

CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ]; then
    echo "Update found: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"
    echo "Commit Timestamp: $GIT_DATE"

    sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
    sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

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
