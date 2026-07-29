#!/bin/bash

SPEC_FILE="libcava.spec"
GITHUB_REPO="LukashonakV/cava"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream releases on $GITHUB_REPO..."

# Get latest tag via git ls-remote (no rate limit)
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)
LATEST_TAG=${LATEST_TAG#v}

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_TAG" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_TAG"

    sed -i -E "s/^Version:.*/Version:        $LATEST_TAG/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # Update Source0 to match new version
    sed -i -E "s|^Source0:.*|Source0:        %{url}/archive/%{version}/cava-%{version}.tar.gz|" "$SPEC_FILE"

    # Update setup directory name
    sed -i -E "s/-n cava-.*/%autosetup -n cava-%{version}/" "$SPEC_FILE"

    DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE_STRING $PACKAGER - $LATEST_TAG-1"
        echo "- Update to $LATEST_TAG"
    } >> "$SPEC_FILE"

    echo "Successfully updated $SPEC_FILE to $LATEST_TAG."
else
    echo "Package is already at $LATEST_TAG. No update needed."
fi
