#!/bin/bash

SPEC_FILE="xcur2png.spec"
GITHUB_REPO="eworm-de/xcur2png"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Latest tag via git ls-remote (no API rate limit). This repo tags bare
# versions (0.7.1), no v-prefix.
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^[0-9]' | sort -uV | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

LATEST_VERSION="$LATEST_TAG"
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    # The release asset is the original upstream tarball re-hosted by the
    # fork; make sure it exists before touching the spec (same guard as
    # freebuff/logseq: a not-yet-published asset is not a script failure).
    ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/${LATEST_VERSION}/${GITHUB_REPO##*/}-${LATEST_VERSION}.tar.gz"
    if ! curl -L --output /dev/null --silent --head --fail "$ASSET_URL"; then
        echo "Asset for $LATEST_VERSION not published yet; keeping $CURRENT_VERSION."
        exit 0
    fi

    SHA256=$(curl -sL "$ASSET_URL" | sha256sum | awk '{print $1}')
    if [ -z "$SHA256" ]; then
        echo "Error: could not hash $ASSET_URL."
        exit 1
    fi

    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    sed -i "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to version $LATEST_VERSION"
        echo "- sha256 refreshed: $SHA256"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at $LATEST_VERSION. No update needed."
fi
