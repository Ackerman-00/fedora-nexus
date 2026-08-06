#!/bin/bash

SPEC_FILE="awww.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on codeberg.org/LGFae/awww..."

LATEST_TAG=$(curl -sL --max-time 30 "https://codeberg.org/api/v1/repos/LGFae/awww/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name',''))" 2>/dev/null)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch latest release tag."
    exit 1
fi

VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

echo "Latest upstream tag: $LATEST_TAG (version: $VERSION)"

CURRENT_VERSION=$(grep "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" == "$VERSION" ]; then
    echo "Package is already at the latest version ($VERSION). No update needed."
    exit 0
fi

echo "Updating: $CURRENT_VERSION -> $VERSION"

sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $VERSION-1"
    echo "- Update to version $VERSION"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."
