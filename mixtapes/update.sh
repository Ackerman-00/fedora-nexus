#!/bin/bash
# update.sh for mixtapes (Git HEAD tracking - upstream publishes no tags;
# metainfo releases like 2026-09-04.0 are date-based and contain dashes,
# so the RPM Version follows the house git-snapshot scheme instead)

SPEC_FILE="mixtapes.spec"
GITHUB_REPO="m-obeid/Mixtapes"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get HEAD commit via git ls-remote (no rate limit)
LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "  -> [ERROR] Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

# Get current values from spec
CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" == "$LATEST_COMMIT" ]; then
    echo "  -> [OK] Package is already at the latest commit ($SHORT_COMMIT). No update needed."
    exit 0
fi

echo "  -> [UPDATE] ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"

# Commit date -> gitdate macro (token-aware GitHub API, like umbriel-git)
if [ -n "$GITHUB_TOKEN" ]; then
    COMMIT_DATE_RAW=$(curl -sL -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null)
else
    COMMIT_DATE_RAW=$(curl -sL "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null)
fi

if [ -z "$COMMIT_DATE_RAW" ]; then
    echo "  -> [ERROR] Could not fetch commit date; refusing to bump blind."
    exit 1
fi
GIT_DATE=$(echo "$COMMIT_DATE_RAW" | tr -d '\-TZ:')

# New upstream state -> refresh pin + gitdate, Release restarts at 1
sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s/^Version:.*/Version:        0^%{gitdate}git%{shortcommit}/" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_ENTRY="* $DATE $PACKAGER - 0^${GIT_DATE}git${SHORT_COMMIT}-1\n- Nightly sync with upstream main branch (Commit: $SHORT_COMMIT)\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
    sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
    printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
