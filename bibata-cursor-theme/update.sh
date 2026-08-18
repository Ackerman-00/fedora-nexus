#!/bin/bash

SPEC_FILE="bibata-cursor-theme.spec"
GITHUB_REPO="ful1e5/Bibata_Cursor"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)
VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$VERSION" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

echo "Latest upstream tag: $LATEST_TAG (version: $VERSION)"

CURRENT_VERSION=$(grep "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" == "$VERSION" ]; then
    echo "Package is already at the latest version ($VERSION). No update needed."
    exit 0
fi

echo "Updating: $CURRENT_VERSION -> $VERSION"

# A tag can exist before its release asset is uploaded (and upstreams do delete
# assets when re-running a release). Bumping onto a tag whose asset is missing
# pins a Source0 that 404s and breaks every rebuild of that NVR.
ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/v${VERSION}/Bibata.tar.xz"
echo "  -> [CHECK] Verifying $ASSET_URL"
if ! curl --output /dev/null --silent --location --head --fail "$ASSET_URL"; then
    echo "  -> [SKIP] Release asset for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

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
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
