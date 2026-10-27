#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="localsend.spec"
GITHUB_REPO="localsend/localsend"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | grep -vEi '(alpha|beta|rc[0-9]*|[-.]pre|[-.]dev|nightly|canary)' | sed -E 's/^v?([0-9].*)/\1 &/' | sort -V -k1,1 | tail -1 | awk '{print $2}')

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "Error: Failed to fetch LocalSend version from GitHub. Check API limits or connection."
    exit 1
fi

LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//;s@-@.@g')

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    DEB_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/LocalSend-$LATEST_VERSION-linux-x86-64.deb"
    echo "  -> [CHECK] Verifying $DEB_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$DEB_URL"; then
        echo "  -> [SKIP] Release asset for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    sed -i -E "s|download/[^/]+/LocalSend-[^/]+\.deb|download/$LATEST_TAG/LocalSend-$LATEST_VERSION-linux-x86-64.deb|g" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_TAG"
    } >> "$SPEC_FILE"
else
    echo "Already up to date ($CURRENT_VERSION)."
fi
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
