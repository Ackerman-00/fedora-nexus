#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="zen-browser.spec"
GITHUB_REPO="zen-browser/desktop"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# upstream mixes v-prefixed and bare tags - plain sort -V picks the wrong latest
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sed -E 's/^v?([0-9].*)/\1 &/' | sort -V -k1,1 | tail -1 | awk '{print $2}')

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "Error: Failed to fetch Zen Browser version from GitHub. Check API limits or connection."
    exit 1
fi

LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's@-@.@g')

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    TARBALL_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/zen.linux-x86_64.tar.xz"
    echo "  -> [CHECK] Verifying $TARBALL_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$TARBALL_URL"; then
        echo "  -> [SKIP] Release assets for $LATEST_TAG are not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    EPOCH=$(grep -E "^Epoch:" "$SPEC_FILE" | awk '{print $2}')
    
    sed -i -E "s|download/[^/]+/zen.linux-x86_64.tar.xz|download/$LATEST_TAG/zen.linux-x86_64.tar.xz|g" "$SPEC_FILE"

    echo "  -> [HASH] Computing sha256 of $TARBALL_URL"
    SHA256=$(curl -sL "$TARBALL_URL" | sha256sum | awk '{print $1}')
    if [ -n "$SHA256" ]; then
        sed -i -E "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"
    else
        echo "  -> [WARN] Could not compute sha256; pin left stale on purpose"
    fi
    
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
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
