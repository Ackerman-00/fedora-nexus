#!/bin/bash

SPEC_FILE="awww.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
UPSTREAM_URL="https://codeberg.org/LGFae/awww"

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

echo "Fetching source archive for $LATEST_TAG via git (codeberg archive endpoint is unreliable)..."
TMP_DIR=$(mktemp -d)
if ! git clone --depth 1 --branch "$LATEST_TAG" "$UPSTREAM_URL.git" "$TMP_DIR/src" 2>/dev/null; then
    echo "Error: failed to clone $UPSTREAM_URL.git at tag $LATEST_TAG."
    rm -rf "$TMP_DIR"
    exit 1
fi

if ! (cd "$TMP_DIR/src" && git archive --format=tar.gz --prefix="awww-$VERSION/" -o "$TMP_DIR/awww-$VERSION.tar.gz" HEAD); then
    echo "Error: failed to generate source archive for $VERSION."
    rm -rf "$TMP_DIR"
    exit 1
fi

rm -f awww-*.tar.gz
mv "$TMP_DIR/awww-$VERSION.tar.gz" "./awww-$VERSION.tar.gz"
rm -rf "$TMP_DIR"

ls -la awww-*.tar.gz

sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $VERSION-1"
    echo "- Update to version $VERSION"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE. Commit awww-$VERSION.tar.gz together with the spec."
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
