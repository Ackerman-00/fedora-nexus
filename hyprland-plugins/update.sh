#!/bin/bash

SPEC_FILE="hyprland-plugins.spec"
GITHUB_REPO="hyprwm/hyprland-plugins"
HYPRLAND_SPEC="../hyprland/hyprland.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get the hyprland version the plugins must match
if [ -f "$HYPRLAND_SPEC" ]; then
    HYPRLAND_VER=$(grep "^Version:" "$HYPRLAND_SPEC" | awk '{print $2}')
else
    echo "Error: Could not read $HYPRLAND_SPEC (expected relative to this package dir)."
    exit 1
fi
echo "Target hyprland version: $HYPRLAND_VER"

# hyprland-plugins tracks hyprland main (git). The repo builds hyprland as a
# STABLE release, so the plugins must be pinned to the hyprpm commit for that
# release version - NOT main HEAD (which chases newer hyprland main and may
# reference headers not in the installed release). The hyprpm pins live in
# hyprpm.toml; the matching commit carries the version in its message, e.g.
# "hyprpm: add pin for 0.56.2".
LATEST_COMMIT=$(curl -s --max-time 30 \
    "https://api.github.com/repos/$GITHUB_REPO/commits?path=hyprpm.toml&per_page=100" \
    | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
ver = sys.argv[1]
best = None
for c in d:
    msg_head = c["commit"]["message"].split("\n")[0]
    if ver in msg_head:
        best = c["sha"]
        break
if best:
    print(best)
else:
    sys.exit(1)
' "$HYPRLAND_VER")

if [ -z "$LATEST_COMMIT" ]; then
    echo "Error: could not find a hyprpm pin commit for hyprland $HYPRLAND_VER. Sticking with current pin."
    exit 1
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}

# Get current values from spec
CURRENT_COMMIT=$(grep -E "^%global commit0" "$SPEC_FILE" | awk '{print $3}')
CURRENT_BUMPVER=$(grep -E "^%global bumpver" "$SPEC_FILE" | awk '{print $3}')

CURRENT_HYPRLAND_VER=$(grep -E "^%global hyprland_ver" "$SPEC_FILE" | awk '{print $3}')

# Check if update needed
COMMIT_CHANGED=$([ "$CURRENT_COMMIT" != "$LATEST_COMMIT" ] && echo true || echo false)
HYPRLAND_CHANGED=$([ "$CURRENT_HYPRLAND_VER" != "$HYPRLAND_VER" ] && echo true || echo false)

if [ "$COMMIT_CHANGED" == "false" ] && [ "$HYPRLAND_CHANGED" == "false" ]; then
    echo "Plugins at hyprland $HYPRLAND_VER pin ($SHORT_COMMIT). No update needed."
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
    echo "- Sync to hyprpm pin commit $SHORT_COMMIT for hyprland $HYPRLAND_VER"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."