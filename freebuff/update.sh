#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="freebuff.spec"
GITHUB_REPO="CodebuffAI/codebuff-community"
TAG_PREFIX="freebuff-v"

echo "Checking for latest Freebuff Desktop release..."

LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E "^${TAG_PREFIX}[0-9]" | sort -uV | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed "s/^${TAG_PREFIX}//")

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/${TAG_PREFIX}${LATEST_VERSION}/freebuff-linux-x64.tar.gz"

    echo "  -> [CHECK] Verifying download link..."
    if ! curl -L --output /dev/null --silent --head --fail "$ASSET_URL"; then
        echo "  -> [SKIP] tar.gz asset for $LATEST_VERSION is not yet available on GitHub yet. Keeping $CURRENT_VERSION."
        exit 0
    fi

    echo "  -> [ACTION] Updating $SPEC_FILE..."

    sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"

    if ! SHA256=$(bash "$_update_sh_dir/../tools/fetch-sha256.sh" "$ASSET_URL"); then
        echo "Error: could not download $ASSET_URL for hashing." >&2
        exit 1
    fi
    sed -i "s/^# sha256:.*/# sha256: $SHA256/" "$SPEC_FILE"

    DATE_STR=$(date +"%a %b %d %Y")
    ENTRY_TMP=$(mktemp)
    {
        echo "* $DATE_STR Ackerman-00 <quietcraft@gmail.com> - $LATEST_VERSION-1"
        echo "- Auto-updated to $LATEST_VERSION via update.sh"
    } > "$ENTRY_TMP"
    sed -i "/^%changelog$/r $ENTRY_TMP" "$SPEC_FILE"
    rm -f "$ENTRY_TMP"

    echo "  -> [DONE] $SPEC_FILE is ready for build."
else
    echo "  -> [OK] Freebuff Desktop is already on latest ($CURRENT_VERSION)."
fi
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
