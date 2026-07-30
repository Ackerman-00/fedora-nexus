#!/bin/bash

SPEC_FILE="fluxer.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
API_URL="https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm"

echo "Checking for upstream updates..."

VERSION=$(curl -sI "$API_URL" | grep -i "^X-Fluxer-Version:" | awk '{print $2}' | tr -d '\r')

if [ -z "$VERSION" ]; then
    echo "Error: Failed to fetch upstream version."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $VERSION"

    echo "Downloading upstream RPM..."
    curl -sL -o "fluxer-app-${VERSION}-x86_64.rpm" "$API_URL"

    sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    sed -i "s/^Source0:.*/Source0:        fluxer-app-${VERSION}-x86_64.rpm/" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $VERSION-1"
        echo "- Update to version $VERSION"
    } >> "$SPEC_FILE"

    echo "Successfully updated to $VERSION."
else
    echo "Package is already at $VERSION. No update needed."
fi
