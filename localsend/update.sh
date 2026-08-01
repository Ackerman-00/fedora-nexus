#!/bin/bash

SPEC_FILE="localsend.spec"
GITHUB_REPO="localsend/localsend"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest tag via git ls-remote (no rate limit)
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "Error: Failed to fetch LocalSend version from GitHub. Check API limits or connection."
    exit 1
fi

# Copr/RPM spec files do not allow dashes in the Version field. Sanitize it.
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//;s@-@.@g')

# Grab the current version from the spec file
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    # 1. Update the Version and Release fields
    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # 2. Update the download URL path in the spec file with the RAW tag
    sed -i -E "s|download/[^/]+/LocalSend-[^/]+\.deb|download/$LATEST_TAG/LocalSend-$LATEST_VERSION-linux-x86-64.deb|g" "$SPEC_FILE"

    # 3. Replace changelog with single entry
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_TAG"
    } >> "$SPEC_FILE"
else
    echo "Already up to date ($CURRENT_VERSION)."
fi
