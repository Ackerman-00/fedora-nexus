#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="xcur2png.spec"
GITHUB_REPO="eworm-de/xcur2png"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^[0-9]' | sort -uV | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

LATEST_VERSION="$LATEST_TAG"
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/${LATEST_VERSION}/${GITHUB_REPO##*/}-${LATEST_VERSION}.tar.gz"
    if ! curl -L --output /dev/null --silent --head --fail "$ASSET_URL"; then
        echo "Asset for $LATEST_VERSION not published yet; keeping $CURRENT_VERSION."
        exit 0
    fi

    if ! SHA256=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$ASSET_URL"); then
        echo "Error: could not download $ASSET_URL for hashing." >&2
        exit 1
    fi
    if [ -z "$SHA256" ]; then
        echo "Error: could not hash $ASSET_URL."
        exit 1
    fi

    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    sed -i "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to version $LATEST_VERSION"
        echo "- sha256 refreshed: $SHA256"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at $LATEST_VERSION. No update needed."
fi
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
