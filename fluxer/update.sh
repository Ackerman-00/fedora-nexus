#!/bin/bash
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="fluxer.spec"
PACKAGER="Ackerman-00 <no-reply>"
API_URL="https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm"
SRC_BASE="https://pkgs.fluxer.com/desktop/stable/linux/x64"

echo "Checking for upstream updates..."

# the served RPM filename is authoritative; X-Fluxer-Version can name a build that 404s
FINAL_URL=$(curl -sIL --max-time 30 -A "Mozilla/5.0" -o /dev/null -w '%{url_effective}' "$API_URL")
VERSION=$(printf '%s' "$FINAL_URL" | grep -oP 'Fluxer-\K[0-9]+(\.[0-9]+)+' | head -1)
HEADER_VERSION=$(curl -sI --max-time 15 -A "Mozilla/5.0" "$API_URL" | grep -i "^X-Fluxer-Version:" | awk '{print $2}' | tr -d '\r')

if [ -z "$VERSION" ]; then
    echo "Error: Failed to fetch upstream version (url: $FINAL_URL)."
    exit 1
fi
if [ -n "$HEADER_VERSION" ] && [ "$HEADER_VERSION" != "$VERSION" ]; then
    echo "Note: X-Fluxer-Version=$HEADER_VERSION, served filename=$VERSION (filename authoritative)"
fi
if ! curl -sfI -L --max-time 30 -o /dev/null -A "Mozilla/5.0" "$SRC_BASE/$VERSION/rpm"; then
    echo "Error: versioned artifact $SRC_BASE/$VERSION/rpm does not resolve." >&2
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$VERSION" ]; then
    echo "Update available: $CURRENT_VERSION -> $VERSION"

    sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    echo "  -> [HASH] Computing sha256 of $SRC_BASE/$VERSION/rpm"
    if ! SHA256=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$SRC_BASE/$VERSION/rpm" --http1.1 -A "Mozilla/5.0"); then
        echo "Error: could not download $SRC_BASE/$VERSION/rpm for hashing." >&2
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
