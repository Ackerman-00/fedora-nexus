#!/bin/bash

SPEC_FILE="fluxer.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
API_URL="https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm"

echo "Checking for upstream updates..."

# Try X-Fluxer-Version header first, then Content-Disposition filename (header is sometimes stale)
HEADER=$(curl -sI --max-time 15 -A "Mozilla/5.0" "$API_URL")
VERSION=$(echo "$HEADER" | grep -i "^X-Fluxer-Version:" | awk '{print $2}' | tr -d '\r')
DISP_VERSION=$(echo "$HEADER" | grep -i "content-disposition" | grep -oP 'Fluxer-Canary-\K[0-9.]+' | head -1)
# Prefer the newer version if they differ (filename is authoritative when header lags)
if [ -n "$DISP_VERSION" ] && [ "$DISP_VERSION" != "$VERSION" ]; then
    echo "Note: X-Fluxer-Version=$VERSION vs Content-Disposition=$DISP_VERSION, using $DISP_VERSION (filename authoritative)"
    VERSION="$DISP_VERSION"
fi
# Also follow redirect and check final RPM's Content-Disposition if still empty
if [ -z "$VERSION" ] || [ "$VERSION" != "$DISP_VERSION" ]; then
    FINAL_HEADER=$(curl -sI --max-time 15 -L -A "Mozilla/5.0" "$API_URL")
    FINAL_DISP=$(echo "$FINAL_HEADER" | grep -i "content-disposition" | grep -oP 'Fluxer-Canary-\K[0-9.]+' | head -1)
    if [ -n "$FINAL_DISP" ]; then
        # Compare semantic version: use sort -V
        NEWER=$(printf "%s\n%s\n" "$VERSION" "$FINAL_DISP" | sort -V | tail -1)
        if [ "$NEWER" != "$VERSION" ]; then
            echo "Note: final redirect version $FINAL_DISP newer than $VERSION, using $FINAL_DISP"
            VERSION="$FINAL_DISP"
        fi
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
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
