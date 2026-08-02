#!/bin/bash

SPEC_FILE="gpu-screen-recorder.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
ATOM_URL="https://git.dec05eba.com/gpu-screen-recorder/atom/?h=master"

echo "Checking for upstream updates..."

# The upstream is a self-hosted cgit. Version releases appear as commit
# titles matching a numeric version (e.g. "5.15.3") in the master atom feed.
LATEST_VERSION=$(curl -s "$ATOM_URL" | grep -oE '<title>[0-9]+\.[0-9]+\.[0-9]+</title>' | sed -E 's/<[^>]+>//g' | sort -V | tail -1)

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch upstream version."
    exit 1
fi

echo "Latest upstream version: $LATEST_VERSION"

# Verify the snapshot tarball actually exists for that version
if ! curl -s -o /dev/null --fail "https://dec05eba.com/snapshot/gpu-screen-recorder.git.${LATEST_VERSION}.tar.gz"; then
    echo "Error: Snapshot tarball for $LATEST_VERSION is not available. Aborting."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update available: $CURRENT_VERSION -> $LATEST_VERSION"

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
