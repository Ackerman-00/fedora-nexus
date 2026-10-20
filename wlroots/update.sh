#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="wlroots.spec"
GIT_URL="https://gitlab.freedesktop.org/wlroots/wlroots.git"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on wlroots..."

LATEST_TAG=$(git ls-remote --tags "$GIT_URL" 2>/dev/null \
  | awk '{print $2}' \
  | sed 's|refs/tags/||; s/\^{}//' \
  | grep -E '^[0-9]' \
  | grep -vE 'rc|beta|alpha|~' \
  | sort -uV \
  | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch the latest version. Check API limits or connection."
    exit 1
fi

LATEST_VERSION="${LATEST_TAG#v}"

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_VERSION"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at the latest version ($CURRENT_VERSION). No update needed."
fi
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
