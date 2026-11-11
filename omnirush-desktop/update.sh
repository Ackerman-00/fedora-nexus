#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="omnirush-desktop.spec"
PACKAGER="Ackerman-00 <no-reply>"
REPO="omnirush-ai/omnirush-gui"

echo "Checking for OmniRush updates on $REPO..."

LATEST=$(curl -fsSL --retry 3 --max-time 30 "https://api.github.com/repos/$REPO/releases/latest")
LATEST_TAG=$(printf '%s' "$LATEST" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tag_name',''))")
if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" = "null" ]; then echo "Error: no tag_name in latest release."; exit 1; fi
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//;s@-@.@g')

ASSET_URL=$(printf '%s' "$LATEST" | python3 -c "
import json,sys
d = json.load(sys.stdin)
print(next((a['browser_download_url'] for a in d.get('assets', [])
            if 'omnirush-linux-amd64-' in a['name'] and a['name'].endswith('.deb')), ''))")

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    CURRENT_SHA=$(grep -E "^# sha256:" "$SPEC_FILE" | head -1 | awk '{print $3}')
    if [ -n "$ASSET_URL" ]; then
        if SHA=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$ASSET_URL"); then
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
            echo "Warning: could not hash $ASSET_URL; leaving pin unchanged."
        fi
    else
        echo "Package is already at $LATEST_VERSION. No update needed."
    fi
    if ! grep -q "^Name:" "$SPEC_FILE"; then
        echo "FATAL: $SPEC_FILE lost its Name: header; restoring" >&2
        git checkout -- "$SPEC_FILE" 2>/dev/null || true
        exit 1
    fi
    exit 0
fi

if [ -z "$ASSET_URL" ]; then echo "Error: no omnirush-linux-amd64 .deb in release assets."; exit 1; fi

echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

SHA=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$ASSET_URL") || { echo "Error: could not download $ASSET_URL."; exit 1; }

sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s|^Source0:.*|Source0:        $ASSET_URL|" "$SPEC_FILE"
sed -i -E "s|^# sha256:.*|# sha256:  $SHA|" "$SPEC_FILE"
sed -i -E "s|^Release:.*|Release:        1%{?dist}|" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
    echo "- Update to upstream release $LATEST_VERSION"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."

if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
