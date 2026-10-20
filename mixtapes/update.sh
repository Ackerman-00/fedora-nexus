#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="mixtapes.spec"
GITHUB_REPO="m-obeid/Mixtapes"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "  -> [ERROR] Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" == "$LATEST_COMMIT" ]; then
    echo "  -> [OK] Package is already at the latest commit ($SHORT_COMMIT). No update needed."
    exit 0
fi

echo "  -> [UPDATE] ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"

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

if grep -q '^# verify-fedora-source0:' "$SPEC_FILE"; then
    SRC0_URL="https://github.com/$GITHUB_REPO/archive/$LATEST_COMMIT/mixtapes-$SHORT_COMMIT.tar.gz"
    TMP_TAR=$(mktemp -t mixtapes-src0.XXXXXX)
    if curl -fsSL "$SRC0_URL" -o "$TMP_TAR"; then
        SRC0_SHA=$(sha256sum "$TMP_TAR" | awk '{print $1}')
        sed -i -E "s|^# verify-fedora-source0:.*|# verify-fedora-source0: $SRC0_URL|" "$SPEC_FILE"
        sed -i -E "s|^# verify-fedora-sha256:.*|# verify-fedora-sha256: $SRC0_SHA|" "$SPEC_FILE"
        echo "  -> [OK] verification header refreshed for $SHORT_COMMIT (sha256 $SRC0_SHA)"
    else
        echo "  -> [WARN] could not download Source0; verification header still names the old pin" >&2
    fi
    rm -f "$TMP_TAR"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
