#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="fluxer.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
API_URL="https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm"

echo "Checking for upstream updates..."

HEADER=$(curl -sI --max-time 15 -A "Mozilla/5.0" "$API_URL")
VERSION=$(echo "$HEADER" | grep -i "^X-Fluxer-Version:" | awk '{print $2}' | tr -d '\r')
DISP_VERSION=$(echo "$HEADER" | grep -i "content-disposition" | grep -oP 'Fluxer-\K[0-9.]+' | head -1)
if [ -n "$DISP_VERSION" ] && [ "$DISP_VERSION" != "$VERSION" ]; then
    echo "Note: X-Fluxer-Version=$VERSION vs Content-Disposition=$DISP_VERSION, using $DISP_VERSION (filename authoritative)"
    VERSION="$DISP_VERSION"
fi
if [ -z "$VERSION" ] || [ "$VERSION" != "$DISP_VERSION" ]; then
    FINAL_HEADER=$(curl -sI --max-time 15 -L -A "Mozilla/5.0" "$API_URL")
    FINAL_DISP=$(echo "$FINAL_HEADER" | grep -i "content-disposition" | grep -oP 'Fluxer-\K[0-9.]+' | head -1)
    if [ -n "$FINAL_DISP" ]; then
        if [ "$FINAL_DISP" != "$VERSION" ]; then
            echo "Note: served RPM filename $FINAL_DISP vs X-Fluxer-Version=$VERSION, using $FINAL_DISP (filename authoritative)"
        fi
        VERSION="$FINAL_DISP"
    fi
fi

if [ -z "$VERSION" ]; then
    echo "Error: Failed to fetch upstream version."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$VERSION" ]; then
    echo "Update available: $CURRENT_VERSION -> $VERSION"

    sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    echo "  -> [HASH] Computing sha256 of served artifact"
    if ! SHA256=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$API_URL" --http1.1 -A "Mozilla/5.0"); then
        echo "Error: could not download $API_URL for hashing." >&2
        exit 1
    fi
    if [ -n "$SHA256" ]; then
        if grep -q "^# sha256:" "$SPEC_FILE"; then
            sed -i -E "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"
        else
            sed -i "/^Source0:/a # sha256: $SHA256" "$SPEC_FILE"
        fi
    else
        echo "  -> [WARN] Could not compute sha256; pin left stale on purpose"
    fi

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
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
