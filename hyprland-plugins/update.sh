#!/bin/bash

SPEC_FILE="hyprland-plugins.spec"
GITHUB_REPO="hyprwm/hyprland-plugins"
HYPRLAND_SPEC="../hyprland/hyprland.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get HEAD commit via git ls-remote (no rate limit)
LATEST_COMMIT=$(git ls-remote https://github.com/$GITHUB_REPO.git HEAD 2>/dev/null | awk '{print $1}')

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: Failed to fetch HEAD commit."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

# Get current values from spec
CURRENT_COMMIT=$(grep -E "^%global commit0" "$SPEC_FILE" | awk '{print $3}')
CURRENT_BUMPVER=$(grep -E "^%global bumpver" "$SPEC_FILE" | awk '{print $3}')

# Get the hyprland version the plugins must match
if [ -f "$HYPRLAND_SPEC" ]; then
    HYPRLAND_VER=$(grep "^Version:" "$HYPRLAND_SPEC" | awk '{print $2}')
else
    echo "Error: Could not read $HYPRLAND_SPEC (expected relative to this package dir)."
    exit 1
fi
CURRENT_HYPRLAND_VER=$(grep -E "^%global hyprland_ver" "$SPEC_FILE" | awk '{print $3}')

# Check if update needed (commit changed, or hyprland moved -> plugins must rebuild)
COMMIT_CHANGED=$([ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ] && echo true || echo false)
HYPRLAND_CHANGED=$([ "$CURRENT_HYPRLAND_VER" != "$HYPRLAND_VER" ] && echo true || echo false)

if [ "$COMMIT_CHANGED" == "false" ] && [ "$HYPRLAND_CHANGED" == "false" ]; then
    echo "Plugins at latest commit ($SHORT_COMMIT) and hyprland version ($HYPRLAND_VER) unchanged. No update needed."
    exit 0
fi

[ "$COMMIT_CHANGED" == "true" ] && echo "New commit: ${CURRENT_COMMIT:0:7} -> $SHORT_COMMIT"
[ "$HYPRLAND_CHANGED" == "true" ] && echo "Hyprland version bump: $CURRENT_HYPRLAND_VER -> $HYPRLAND_VER"

NEW_BUMPVER=$((CURRENT_BUMPVER + 1))

# Update spec
sed -i -E "s/^%global commit0.*/%global commit0 $LATEST_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global bumpver.*/%global bumpver $NEW_BUMPVER/" "$SPEC_FILE"
sed -i -E "s/^%global hyprland_ver.*/%global hyprland_ver $HYPRLAND_VER/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s/^Version:.*/Version:        0.1^%{bumpver}.git%{shortcommit0}/" "$SPEC_FILE"

# Update changelog
DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_VER="0.1^${NEW_BUMPVER}.git${SHORT_COMMIT}-1"
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $CHANGELOG_VER"
    echo "- Sync with upstream main branch (Commit: $SHORT_COMMIT)"
    echo "- Builds against hyprland $HYPRLAND_VER"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."
