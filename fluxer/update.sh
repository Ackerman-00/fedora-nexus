#!/bin/bash

SPEC_FILE="fluxer.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
API_URL="https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm"

echo "Checking for upstream updates..."

VERSION=$(curl -sI --max-time 15 -A "Mozilla/5.0" "$API_URL" | grep -i "^X-Fluxer-Version:" | awk '{print $2}' | tr -d '\r')

if [ -z "$VERSION" ]; then
    echo "Error: Failed to fetch upstream version."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$VERSION" ]; then
    echo "Update available: $CURRENT_VERSION -> $VERSION"

    sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

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
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
