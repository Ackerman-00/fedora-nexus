#!/bin/bash

SPEC_FILE="aylurs-gtk-shell.spec"
GITHUB_REPO="Aylur/ags"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest tag via git ls-remote (no rate limit)
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to version $LATEST_VERSION"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at $LATEST_VERSION. No update needed."
fi
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
