#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="logseq.spec"
GITHUB_REPO="logseq/logseq"
ASSET_BASE="https://github.com/$GITHUB_REPO/releases/download"

echo "Checking for latest Logseq release..."

LATEST_VERSION=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    ZIP_URL="${ASSET_BASE}/${LATEST_VERSION}/Logseq-linux-x86_64-${LATEST_VERSION}.zip"

    echo "  -> [CHECK] Verifying download link..."
    if ! curl --output /dev/null --silent --head --fail "$ZIP_URL"; then
        echo "  -> [SKIP] Linux x86_64 zip for $LATEST_VERSION is not yet available on GitHub yet. Keeping $CURRENT_VERSION."
        exit 0
    fi

    echo "  -> [ACTION] Updating $SPEC_FILE..."

    sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"

    echo "  -> [HASH] Computing sha256 of $ZIP_URL"
    SHA256=$(curl -sL "$ZIP_URL" | sha256sum | awk '{print $1}')
    if [ -n "$SHA256" ]; then
        sed -i -E "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"
    else
        echo "  -> [WARN] Could not compute sha256; pin left stale on purpose"
    fi

    DATE_STR=$(date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE_STR Ackerman-00 <quietcraft@gmail.com> - $LATEST_VERSION-1"
        echo "- Auto-updated to $LATEST_VERSION via update.sh"
    } >> "$SPEC_FILE"

    echo "  -> [DONE] $SPEC_FILE is ready for build."
else
    echo "  -> [OK] Logseq is already on latest ($CURRENT_VERSION)."
fi
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
