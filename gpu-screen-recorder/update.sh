#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="gpu-screen-recorder.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
GIT_URL="https://git.dec05eba.com/gpu-screen-recorder/"

echo "Checking for upstream updates..."

LATEST_VERSION=$(curl -sL "$GIT_URL" | grep -oE 'tag/\?h=[0-9]+\.[0-9]+\.[0-9]+' | sed 's|tag/?h=||' | sort -V | tail -1)

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch upstream version."
    exit 1
fi

echo "Latest upstream version: $LATEST_VERSION"

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update available: $CURRENT_VERSION -> $LATEST_VERSION"

    if ! curl -s -o /dev/null --fail "https://dec05eba.com/snapshot/gpu-screen-recorder.git.${LATEST_VERSION}.tar.gz"; then
        echo "Error: Snapshot tarball for $LATEST_VERSION is not available. Aborting."
        exit 1
    fi

    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Update to version $LATEST_VERSION"
    } >> "$SPEC_FILE"

    echo "Successfully updated to $LATEST_VERSION."
else
    echo "Package is already at $LATEST_VERSION. No update needed."
fi
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
