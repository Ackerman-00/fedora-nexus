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

SPEC_FILE="caelestia-shell-mango.spec"
GITHUB_REPO="Ackerman-00/caelestia-shell-mango"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get HEAD commit via git ls-remote (no rate limit)
LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ]; then
    echo "Update found: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"

    # Fetch commit date via API (needs token for rate limits)
    if [ -n "$GITHUB_TOKEN" ]; then
        GIT_DATE=$(curl -sL -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null | sed 's/[^0-9]//g' | cut -c1-14)
    else
        GIT_DATE=$(curl -sL "https://api.github.com/repos/$GITHUB_REPO/commits/$LATEST_COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('committer',{}).get('date',''))" 2>/dev/null | sed 's/[^0-9]//g' | cut -c1-14)
    fi

    if [ -z "$GIT_DATE" ]; then
        GIT_DATE=$(grep "^%global gitdate" "$SPEC_FILE" | awk '{print $3}')
    fi

    # Resolve the upstream release base version from the tag that points at
    # HEAD. rpmbuild tarballs carry no .git, so the spec passes -DVERSION
    # explicitly; this keeps that value in sync with the real upstream tag
    # instead of silently going stale (the 2.0.0-vs-2.1.0 bug).
    BASE_VER=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null \
        | awk -v target="$LATEST_COMMIT" '$1==target{ref=$2; sub(/^refs\/tags\//,"",ref); sub(/\^\{\}$/,"",ref); if(ref ~ /^v?[0-9]+\.[0-9]+\.[0-9]+$/){sub(/^v/,"",ref); print ref; exit}}')

    # Fall back to the currently packaged base version if HEAD is not tagged
    # (e.g. a post-release commit on main).
    if [ -z "$BASE_VER" ]; then
        BASE_VER=$(grep "^%global basever" "$SPEC_FILE" | awk '{print $3}')
    fi

    if [ -z "$BASE_VER" ]; then
        echo "Error: could not determine upstream base version."
        exit 1
    fi

    sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
    sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
    sed -i -E "s/^%global basever.*/%global basever         $BASE_VER/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    sed -i -E "s/^Version:.*/Version:        %{basever}^%{gitdate}git%{shortcommit}/" "$SPEC_FILE"

    DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
    CHANGELOG_VER="${BASE_VER}^${GIT_DATE}git${SHORT_COMMIT}-1"
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE_STRING $PACKAGER - $CHANGELOG_VER"
        echo "- Nightly sync with upstream main branch (Commit: $SHORT_COMMIT)"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at the latest commit ($SHORT_COMMIT). No update needed."
fi
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
# Guard: an updater must never leave a spec without its header. If the
# changelog rewrite or a sed wiped the file, restore from git and fail loudly.
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
