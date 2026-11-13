#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="hermes-agent-desktop.spec"
GITHUB_REPO="NousResearch/hermes-agent"
PACKAGER="Ackerman-00 <no-reply>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v0\.[0-9]+\.[0-9]+$' | sort -V | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: no stable v0.x.y tag found upstream."
    exit 1
fi

BASE_VER=$(echo "$LATEST_TAG" | sed 's/^v//')
echo "Latest upstream stable tag: $LATEST_TAG (base version: $BASE_VER)"

CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')
CURRENT_BASE_VER=$(grep "^Version:" "$SPEC_FILE" | awk '{print $2}' | sed 's/\^.*//')

COMMIT_CHANGED=$([ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ] && echo true || echo false)
BASE_VER_CHANGED=$([ "$CURRENT_BASE_VER" != "$BASE_VER" ] && echo true || echo false)

if [ "$COMMIT_CHANGED" == "false" ] && [ "$BASE_VER_CHANGED" == "false" ]; then
    echo "Package is already at the latest commit ($SHORT_COMMIT). No update needed."
    exit 0
fi

[ "$COMMIT_CHANGED" == "true" ] && echo "New commit: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"
[ "$BASE_VER_CHANGED" == "true" ] && echo "Base version bump: $CURRENT_BASE_VER -> $BASE_VER"

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

# upstream commits every ~40 min; the 8 h update-engine schedule owns the bump
MIN_INTERVAL_HOURS=8
PIN_STAMP=$(grep -E "^%global gitdate" "$SPEC_FILE" | awk '{print $3}')
if [ "${#PIN_STAMP}" -ge 14 ]; then
    PIN_ISO="${PIN_STAMP:0:4}-${PIN_STAMP:4:2}-${PIN_STAMP:6:2} ${PIN_STAMP:8:2}:${PIN_STAMP:10:2}:${PIN_STAMP:12:2}"
else
    PIN_ISO="${PIN_STAMP:0:4}-${PIN_STAMP:4:2}-${PIN_STAMP:6:2}"
fi
PIN_EPOCH=$(date -u -d "$PIN_ISO" +%s 2>/dev/null || echo 0)
NEW_EPOCH=$(date -u -d "$COMMIT_DATE_RAW" +%s 2>/dev/null || echo 0)
if [ "$PIN_EPOCH" -gt 0 ] && [ "$NEW_EPOCH" -gt 0 ]; then
    AGE_H=$(( (NEW_EPOCH - PIN_EPOCH) / 3600 ))
    if [ "$AGE_H" -lt "$MIN_INTERVAL_HOURS" ]; then
        echo "Upstream moved ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT but only ${AGE_H}h past the pinned snapshot; the ${MIN_INTERVAL_HOURS}h cadence owns it."
        exit 0
    fi
fi

TARBALL_URL="https://github.com/$GITHUB_REPO/archive/$LATEST_COMMIT.tar.gz"
NEW_SHA256=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$TARBALL_URL" 2>/dev/null)
if [ -z "$NEW_SHA256" ]; then
    echo "Error: Failed to download $TARBALL_URL for sha256."
    exit 1
fi

sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
python3 - "$SPEC_FILE" "$NEW_SHA256" <<'PYEOF'
import sys
path, newpin = sys.argv[1], sys.argv[2]
lines = open(path).read().splitlines(keepends=True)
seen_source0 = False
for i, line in enumerate(lines):
    if line.startswith('Source0:'):
        seen_source0 = True
        continue
    if seen_source0 and line.startswith('# sha256:'):
        lines[i] = '# sha256:  %s\n' % newpin
        break
open(path, 'w').write(''.join(lines))
PYEOF
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s/^Version:.*/Version:        ${BASE_VER}^%{gitdate}git%{shortcommit}/" "$SPEC_FILE"

DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_VER="${BASE_VER}^${GIT_DATE}git${SHORT_COMMIT}-1"
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $CHANGELOG_VER"
    echo "- Nightly sync with upstream main branch (Commit: $SHORT_COMMIT)"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
