#!/bin/bash

# Run this from its own package directory. update-engine.yml does `pushd <pkg>`
# first; running update.sh from the repo root instead let the changelog append
# create a stray <pkg>.spec at the repo root, and the Name: check then reported
# a false corruption (hit twice, 2026-10-07: stray umbriel-git.spec, then 32
# stray root specs during an agent sweep).
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi
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

# Refresh the verification header (verify-fedora-source0 / -sha256) so it
# never drifts behind the pin again: 2026-10-08 the header still named the
# 2026-10-03 pin e95c9e9 while Source0 pointed at 790bd83, which would make
# the next sha256 audit compare the wrong tarball. Best effort: a download
# failure warns loudly but does not abort a valid version bump.
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
# Guard: an updater must never leave a spec without its header. If the
# changelog rewrite or a sed wiped the file, restore from git and fail loudly.
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
