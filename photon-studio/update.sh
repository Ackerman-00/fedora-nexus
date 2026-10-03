#!/bin/bash
# update.sh for Photon Studio (upstream AppImage repack)

SPEC_FILE="photon-studio.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
STABLE_URL="https://tenzen.studio/api/v1/photon/download?platform=linux&arch=x64&kind=appimage"

echo "Checking for upstream updates..."

# The API 302-redirects to the versioned file
# (.../photon/stable/linux/<version>/Photon-Studio-<version>-linux-x64.AppImage);
# the redirect target is the version source of truth.
# The API rejects HEAD (405); a 1-byte ranged GET follows the redirect
# without downloading the ~760 MB file.
EFFECTIVE_URL=$(curl -sL -r 0-0 -o /dev/null -w '%{url_effective}' --max-time 30 "$STABLE_URL")
LATEST_VERSION=$(echo "$EFFECTIVE_URL" | grep -oP 'photon/stable/linux/\K[0-9]+\.[0-9]+\.[0-9]+' | head -1)

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Could not resolve version from $STABLE_URL (got: $EFFECTIVE_URL)."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    APPIMAGE_URL="https://downloads.tenzen.studio/photon/stable/linux/$LATEST_VERSION/Photon-Studio-${LATEST_VERSION}-linux-x64.AppImage"
    echo "  -> [CHECK] Verifying $APPIMAGE_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$APPIMAGE_URL"; then
        echo "  -> [SKIP] Linux x86_64 AppImage for $LATEST_VERSION is not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    sed -i -E "s|photon/stable/linux/[^/]+/Photon-Studio-.*-linux-x64.AppImage|photon/stable/linux/$LATEST_VERSION/Photon-Studio-${LATEST_VERSION}-linux-x64.AppImage|" "$SPEC_FILE"

    # Refresh the pinned sha256 for the new AppImage (teardown-sweep verifies
    # Source0 against this pin; a stale pin fails the next run). NOTE: the
    # AppImage is ~760 MB, so this download is heavy — but it only runs on
    # actual version bumps.
    echo "  -> [HASH] Computing sha256 of $APPIMAGE_URL"
    SHA256=$(curl -sL "$APPIMAGE_URL" | sha256sum | awk '{print $1}')
    if [ -n "$SHA256" ]; then
        sed -i -E "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"
    else
        echo "  -> [WARN] Could not compute sha256; pin left stale on purpose"
    fi

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_VERSION"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at $LATEST_VERSION. No update needed."
fi
