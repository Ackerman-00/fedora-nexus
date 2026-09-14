#!/bin/bash

SPEC_FILE="opencode-desktop.spec"
GITHUB_REPO="anomalyco/opencode"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Tags can exist without their release asset uploaded yet (upstreams delete
# assets when re-running a release; v2.0.x tags carry no desktop .deb at
# all). Walk tags newest-first and take the first one whose .deb is
# published — bumping onto an asset-less tag pins a 404 Source0.
LATEST_VERSION=""
for TAG in $(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sort -Vu | tail -10 | sort -Vr); do
    CANDIDATE=$(echo "$TAG" | sed 's/^v//')
    DEB_URL="https://github.com/$GITHUB_REPO/releases/download/v${CANDIDATE}/opencode-desktop-linux-amd64.deb"
    if curl --output /dev/null --silent --location --head --fail "$DEB_URL"; then
        LATEST_VERSION="$CANDIDATE"
        LATEST_TAG="$TAG"
        break
    else
        echo "  -> [SKIP] No published asset for $TAG (yet)."
    fi
done

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: No tag with a published desktop asset found."
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
