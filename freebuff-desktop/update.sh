#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="freebuff-desktop.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
API_URL="https://freebuff.com/api/desktop/download/linux"

echo "Checking for Freebuff desktop updates..."

EFFECTIVE_URL=$(curl -sI --max-time 60 -o /dev/null -w '%{redirect_url}' "$API_URL")
if [ -z "$EFFECTIVE_URL" ]; then echo "Error: upstream redirect unavailable."; exit 1; fi

LATEST_VERSION=$(echo "$EFFECTIVE_URL" | grep -oP 'freebuff-desktop-v\K[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [ -z "$LATEST_VERSION" ]; then echo "Error: could not parse version from $EFFECTIVE_URL"; exit 1; fi

DEB_URL=$(echo "$EFFECTIVE_URL" | grep -oP '\S*Freebuff-[^/]+-linux-amd64\.deb')
if [ -z "$DEB_URL" ]; then echo "Error: redirect did not land on a Freebuff amd64 .deb ($EFFECTIVE_URL)"; exit 1; fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    CURRENT_SHA=$(grep -E "^# sha256:" "$SPEC_FILE" | head -1 | awk '{print $3}')
    if SHA=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$DEB_URL"); then
        if [ "$SHA" = "$CURRENT_SHA" ]; then
            echo "Package is already at $LATEST_VERSION. No update needed."
            exit 0
        fi
        echo "Upstream respinned $CURRENT_VERSION (sha256 $CURRENT_SHA -> $SHA); re-pinning and bumping Release."
        sed -i -E "s|^# sha256:.*|# sha256:  $SHA|" "$SPEC_FILE"
        OLD_REL=$(grep -E "^Release:" "$SPEC_FILE" | awk '{print $2}' | sed 's/%.*//')
        NEW_REL=$((OLD_REL + 1))
        sed -i -E "s|^Release:.*|Release:        ${NEW_REL}%{?dist}|" "$SPEC_FILE"
        DATE=$(LC_ALL=C date +"%a %b %d %Y")
        sed -i '/^%changelog/,$d' "$SPEC_FILE"
        {
            echo "%changelog"
            echo "* $DATE $PACKAGER - $LATEST_VERSION-$NEW_REL"
            echo "- Re-pin .deb (upstream respinned the tag)"
        } >> "$SPEC_FILE"
    else
        echo "Warning: could not hash $DEB_URL; leaving pin unchanged."
    fi
    if ! grep -q "^Name:" "$SPEC_FILE"; then
        echo "FATAL: $SPEC_FILE lost its Name: header; restoring" >&2
        git checkout -- "$SPEC_FILE" 2>/dev/null || true
        exit 1
    fi
    exit 0
fi

echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

SHA=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$DEB_URL") || { echo "Error: could not download $DEB_URL."; exit 1; }

sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s|^Source0:.*|Source0:        $DEB_URL|" "$SPEC_FILE"
sed -i -E "s|^# sha256:.*|# sha256:  $SHA|" "$SPEC_FILE"
sed -i -E "s|^Release:.*|Release:        0|" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $LATEST_VERSION-0"
    echo "- Update to upstream release $LATEST_VERSION"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."

if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
