#!/bin/bash

SPEC_FILE="niri-git.spec"
GITHUB_REPO="YaLTeR/niri"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest tag via git ls-remote (no rate limit)
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)
BASE_VER=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$BASE_VER" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

echo "Latest upstream tag: $LATEST_TAG (base version: $BASE_VER)"

# Get HEAD commit via git ls-remote (no rate limit)
LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

# Get current values from spec
CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')
CURRENT_BASE_VER=$(grep "^Version:" "$SPEC_FILE" | awk '{print $2}' | sed 's/\^.*//')

# Check if update needed
COMMIT_CHANGED=$([ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ] && echo true || echo false)
BASE_VER_CHANGED=$([ "$CURRENT_BASE_VER" != "$BASE_VER" ] && echo true || echo false)

if [ "$COMMIT_CHANGED" == "false" ] && [ "$BASE_VER_CHANGED" == "false" ]; then
    echo "Package is already at the latest commit ($SHORT_COMMIT). No update needed."
    exit 0
fi

[ "$COMMIT_CHANGED" == "true" ] && echo "New commit: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"
[ "$BASE_VER_CHANGED" == "true" ] && echo "Base version bump: $CURRENT_BASE_VER -> $BASE_VER"

# Fetch commit date via API (needs token for rate limits)
if [ -n "$GITHUB_TOKEN" ]; then
    COMMIT_DATE_RAW=$(curl -sL -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null)
else
    COMMIT_DATE_RAW=$(curl -sL "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null)
fi

if [ -z "$COMMIT_DATE_RAW" ]; then
    echo "Warning: Could not fetch commit date. Using spec file date."
    GIT_DATE=$(grep "^%global gitdate" "$SPEC_FILE" | awk '{print $3}')
else
    GIT_DATE=$(echo "$COMMIT_DATE_RAW" | tr -d '\-TZ:')
fi

# Update spec
sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s/^Version:.*/Version:        ${BASE_VER}^%{gitdate}git%{shortcommit}/" "$SPEC_FILE"

# Update changelog
DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_VER="${BASE_VER}^${GIT_DATE}git${SHORT_COMMIT}-1"
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $CHANGELOG_VER"
    echo "- Nightly sync with upstream main branch (Commit: $SHORT_COMMIT)"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."
