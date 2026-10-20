#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="ghostty.spec"
GITHUB_REPO="mkasberg/ghostty-ubuntu"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+-[0-9]+-ppa[0-9]+$' | sort -V | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch latest tag from mkasberg/ghostty-ubuntu. Check connection."
    exit 1
fi

GHOSTTY_VERSION=$(echo "$LATEST_TAG" | cut -d- -f1)
DEB_VER="${GHOSTTY_VERSION}-0.${LATEST_TAG##*-}"

CURRENT_TAG=$(grep -E "^%global ppatag" "$SPEC_FILE" | awk '{print $3}')
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_TAG" == "$LATEST_TAG" ]; then
    echo "Package is already at the latest PPA release ($LATEST_TAG). No update needed."
    exit 0
fi

echo "Update found: $CURRENT_TAG -> $LATEST_TAG"

DEB_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/ghostty_${DEB_VER}_amd64_24.04.deb"
echo "  -> [CHECK] Verifying $DEB_URL"
if ! curl --output /dev/null --silent --location --head --fail "$DEB_URL"; then
    echo "  -> [SKIP] Release assets for $LATEST_TAG are not published (yet). Keeping $CURRENT_TAG."
    exit 0
fi

if [ "$CURRENT_VERSION" != "$GHOSTTY_VERSION" ]; then
    sed -i -E "s/^Version:.*/Version:        %{ghostty_version}/" "$SPEC_FILE"
    sed -i -E "s/^%global ghostty_version.*/%global ghostty_version $GHOSTTY_VERSION/" "$SPEC_FILE"
fi
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

sed -i -E "s/^%global ppatag.*/%global ppatag $LATEST_TAG/" "$SPEC_FILE"
sed -i -E "s/^%global debver.*/%global debver $DEB_VER/" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $GHOSTTY_VERSION-1"
    echo "- Auto-update to upstream ghostty release $GHOSTTY_VERSION (PPA release $LATEST_TAG)"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."


if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
