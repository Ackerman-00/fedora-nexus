#!/bin/bash

SPEC_FILE="zen-browser.spec"
GITHUB_REPO="zen-browser/desktop"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Get latest tag via git ls-remote (no rate limit)
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -V | tail -1)

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "Error: Failed to fetch Zen Browser version from GitHub. Check API limits or connection."
    exit 1
fi

# Copr/RPM spec files do not allow dashes in the Version field. Sanitize it.
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's@-@.@g')

# Grab the current version from the spec file
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    # A tag can exist long before (or after) its release assets do: zen's release
    # workflow pushes the tag first and uploads the tarball at the end, and it has
    # been observed DELETING the assets when a release build is re-run. Bumping on
    # a tag whose asset is missing produces a spec whose Source0 404s, so every
    # COPR rebuild of that NVR fails. Only bump once the tarball really exists.
    TARBALL_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/zen.linux-x86_64.tar.xz"
    echo "  -> [CHECK] Verifying $TARBALL_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$TARBALL_URL"; then
        echo "  -> [SKIP] Release assets for $LATEST_TAG are not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    # 1. Update the Version and Release fields
    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # The spec carries Epoch: 1 because upstream once deleted a release we had
    # already shipped (1.21.13b) and only an Epoch could supersede it. Keep the
    # Epoch on every future bump - dropping it would make new builds sort BELOW
    # the epoch'd ones and users would never get the update.
    EPOCH=$(grep -E "^Epoch:" "$SPEC_FILE" | awk '{print $2}')
    
    # 2. Update the download URL path in the spec file with the RAW tag
    sed -i -E "s|download/[^/]+/zen.linux-x86_64.tar.xz|download/$LATEST_TAG/zen.linux-x86_64.tar.xz|g" "$SPEC_FILE"
    
    # 3. Replace changelog with single entry
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - ${EPOCH:+$EPOCH:}$LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_TAG"
    } >> "$SPEC_FILE"
    
    echo "✅ Successfully patched $SPEC_FILE."
else
    echo "✅ Package is already at $LATEST_VERSION. No update needed."
fi
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
