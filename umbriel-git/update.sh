#!/bin/bash

SPEC_FILE="umbriel-git.spec"
GITHUB_REPO="noctalia-dev/umbriel"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get HEAD commit via git ls-remote (no rate limit)
LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

# Base version: latest tag if any, else the meson project() version at HEAD
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)

if [ -n "$LATEST_TAG" ]; then
    BASE_VER=$(echo "$LATEST_TAG" | sed 's/^v//')
    echo "Latest upstream tag: $LATEST_TAG (base version: $BASE_VER)"
else
    BASE_VER=$(curl -fsSL "https://raw.githubusercontent.com/$GITHUB_REPO/$LATEST_COMMIT/meson.build" \
        | grep -oP "^\s*version:\s*'\K[^']+" | head -1)
    echo "No upstream tags; base version from meson.build: $BASE_VER"
fi

if [ -z "$BASE_VER" ]; then
    echo "Error: Failed to determine base version."
    exit 1
fi

# SceneFX submodule pin — only when upstream still uses the subproject.
# As of 2026-09-01 commit 729e7eb upstream vendored the renderer as
# umbrielfx/ and removed subprojects/scenefx; archives no longer contain
# subprojects/. Detect the upstream build system before trying to pin.
USES_SCENEFX="no"
if curl -fsSL "https://raw.githubusercontent.com/$GITHUB_REPO/$LATEST_COMMIT/meson.build" 2>/dev/null | grep -q "scenefx"; then
    USES_SCENEFX="yes"
    echo "Upstream meson.build references scenefx — checking submodule pin..."
    check_scenefx_api() {
        local sha="$1"
        [ -n "$sha" ] || return 1
        local hdr
        hdr=$(curl -fsSL ${GITHUB_TOKEN:+-H "Authorization: token $GITHUB_TOKEN"} \
            "https://raw.githubusercontent.com/noctalia-dev/scenefx/$sha/include/scenefx/types/wlr_scene.h" 2>/dev/null) || return 1
        echo "$hdr" | grep -q wlr_scene_blur_set_ignore_alpha &&
        echo "$hdr" | grep -q wlr_scene_tree_set_clip &&
        echo "$hdr" | grep -q wlr_scene_output_set_sdr_white_level
    }
    SCENEFX_COMMIT=$(curl -sfL ${GITHUB_TOKEN:+-H "Authorization: token $GITHUB_TOKEN"} \
        "https://api.github.com/repos/$GITHUB_REPO/contents/subprojects/scenefx?ref=$LATEST_COMMIT" \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null)
    if ! check_scenefx_api "$SCENEFX_COMMIT"; then
        echo "Warning: scenefx gitlink ${SCENEFX_COMMIT:0:7} misses Umbriel patched APIs (upstream forgot to bump the submodule); falling back to umbriel branch HEAD."
        SCENEFX_COMMIT=$(curl -sfL ${GITHUB_TOKEN:+-H "Authorization: token $GITHUB_TOKEN"} \
            "https://api.github.com/repos/noctalia-dev/scenefx/commits/umbriel" \
            | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null)
        if ! check_scenefx_api "$SCENEFX_COMMIT"; then
            echo "Error: even scenefx umbriel HEAD ${SCENEFX_COMMIT:0:7} lacks the patched APIs; upstream is mid-refactor."
            exit 1
        fi
    fi
else
    echo "Upstream meson.build no longer references scenefx (umbrielfx vendored) — skipping scenefx pin."
    SCENEFX_COMMIT=""
fi

# Get current values from spec
CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')
CURRENT_BASE_VER=$(grep "^Version:" "$SPEC_FILE" | awk '{print $2}' | sed 's/\^.*//')
CURRENT_SCENEFX=$(grep -E "^%global scenefx_commit" "$SPEC_FILE" 2>/dev/null | awk '{print $3}' || echo "")
HAS_SCENEFX_SPEC=$([ -n "$CURRENT_SCENEFX" ] && echo yes || echo no)

# Check if update needed (scenefx only matters when upstream uses it)
COMMIT_CHANGED=$([ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ] && echo true || echo false)
BASE_VER_CHANGED=$([ "$CURRENT_BASE_VER" != "$BASE_VER" ] && echo true || echo false)
if [ "$USES_SCENEFX" == "yes" ]; then
    SCENEFX_CHANGED=$([ -n "$SCENEFX_COMMIT" ] && [ "$CURRENT_SCENEFX" != "$SCENEFX_COMMIT" ] && echo true || echo false)
else
    # Upstream dropped scenefx — need update if spec still carries the old pin
    SCENEFX_CHANGED=$([ "$HAS_SCENEFX_SPEC" == "yes" ] && echo true || echo false)
fi

if [ "$COMMIT_CHANGED" == "false" ] && [ "$BASE_VER_CHANGED" == "false" ] && [ "$SCENEFX_CHANGED" == "false" ]; then
    echo "Package is already at the latest commit ($SHORT_COMMIT). No update needed."
    exit 0
fi

[ "$COMMIT_CHANGED" == "true" ] && echo "New commit: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"
[ "$BASE_VER_CHANGED" == "true" ] && echo "Base version bump: $CURRENT_BASE_VER -> $BASE_VER"
if [ "$USES_SCENEFX" == "yes" ]; then
    [ "$SCENEFX_CHANGED" == "true" ] && echo "SceneFX submodule pin: ${CURRENT_SCENEFX:0:7} -> ${SCENEFX_COMMIT:0:7}"
else
    [ "$SCENEFX_CHANGED" == "true" ] && echo "SceneFX removed upstream (umbrielfx vendored) — dropping spec pin"
fi

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

# Update spec — handle both scenefx-present and scenefx-removed upstream
sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global gitdate.*/%global gitdate         $GIT_DATE/" "$SPEC_FILE"
if [ "$USES_SCENEFX" == "yes" ]; then
    if grep -q "^%global scenefx_commit" "$SPEC_FILE"; then
        sed -i -E "s/^%global scenefx_commit.*/%global scenefx_commit      $SCENEFX_COMMIT/" "$SPEC_FILE"
    else
        # Upstream re-added scenefx — re-insert pin (rare)
        sed -i "/^%global gitdate/a %global scenefx_commit      $SCENEFX_COMMIT\n%global scenefx_shortcommit %(c=%{scenefx_commit}; echo \${c:0:7})" "$SPEC_FILE"
    fi
else
    # Upstream vendored umbrielfx — remove obsolete scenefx pins if present
    sed -i -E "/^%global scenefx_commit/d" "$SPEC_FILE"
    sed -i -E "/^%global scenefx_shortcommit/d" "$SPEC_FILE"
    # Remove Source1 and %prep scenefx handling if still present (idempotent)
    sed -i -E "/^Source1:.*scenefx/d" "$SPEC_FILE"
    sed -i -E "s/^%autosetup -n umbriel-%\{commit\} -a1/%autosetup -n umbriel-%{commit}/" "$SPEC_FILE"
    # Remove old rm/mv lines and stale comment
    sed -i -E "/^rm -rf subprojects\/scenefx/d" "$SPEC_FILE"
    sed -i -E "/^mv scenefx-/d" "$SPEC_FILE"
    sed -i -E "/^# GitHub archives exclude git submodules.*scenefx/d" "$SPEC_FILE"
    sed -i -E "s/^%meson_install --skip-subprojects/%meson_install/" "$SPEC_FILE"
fi
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
