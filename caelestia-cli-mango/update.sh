#!/bin/bash

SPEC_FILE="caelestia-cli-mango.spec"
GITHUB_REPO="Ackerman-00/caelestia-cli-mango"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Upstream has no releases/tags, so the workflow's release scanner 404s on it.
# Track the default branch HEAD by commit instead (ls-remote: no rate limit).
LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" == "$LATEST_COMMIT" ]; then
    echo "Package is already at the latest commit ($SHORT_COMMIT). No update needed."
    exit 0
fi

echo "Update found: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"

# Commit date -> gitdate (needs a token for API rate limits; fall back to the
# value already in the spec so we never write an empty macro).
if [ -n "$GITHUB_TOKEN" ]; then
    GIT_DATE=$(curl -sL -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null | sed 's/[^0-9]//g' | cut -c1-14)
else
    GIT_DATE=$(curl -sL "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null | sed 's/[^0-9]//g' | cut -c1-14)
fi

if [ -z "$GIT_DATE" ]; then
    GIT_DATE=$(grep "^%global gitdate" "$SPEC_FILE" | awk '{print $3}')
fi

# The python project version (pyproject.toml) is independent of the rpm
# Version and drives the .dist-info path; keep %{pyver} as the base.
PY_VER=$(grep -E "^%global pyver" "$SPEC_FILE" | awk '{print $3}')
[ -z "$PY_VER" ] && PY_VER=2.0.0

sed -i -E "s/^%global commit .*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s/^Version:.*/Version:        %{pyver}^%{gitdate}git%{shortcommit}/" "$SPEC_FILE"

DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_VER="${PY_VER}^${GIT_DATE}git${SHORT_COMMIT}-1"
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $CHANGELOG_VER"
    echo "- Nightly sync with upstream main branch (Commit: $SHORT_COMMIT)"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."
