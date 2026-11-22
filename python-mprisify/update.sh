#!/bin/bash
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="python-mprisify.spec"
GIT_URL="https://gitlab.com/zehkira/mprisify.git"
PACKAGER="Ackerman-00 <no-reply>"

echo "Checking GitLab tags for zehkira/mprisify..."

fetch_tags() {
    local i out
    for i in 1 2 3; do
        if out=$(git ls-remote --tags "$GIT_URL" 2>&1) && [ -n "$out" ]; then
            printf '%s\n' "$out"
            return 0
        fi
        echo "  -> tag fetch attempt $i failed, retrying" >&2
        sleep 5
    done
    return 1
}

LATEST_TAG=$(fetch_tags \
  | awk '{print $2}' \
  | sed 's|refs/tags/||; s/\^{}//' \
  | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' \
  | sort -uV \
  | tail -1)
LATEST_VERSION=${LATEST_TAG#v}

if [ -z "$LATEST_VERSION" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag from $GIT_URL."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" == "$CURRENT_VERSION" ]; then
    echo "  -> [OK] Package is already at $CURRENT_VERSION. No update needed."
    exit 0
fi

echo "  -> [UPDATE] $CURRENT_VERSION -> $LATEST_VERSION"

sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
CHANGELOG_ENTRY="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to upstream tag $LATEST_TAG\n"
if grep -q '^%changelog' "$SPEC_FILE"; then
    sed -i "0,/^%changelog$/s//%changelog\n$CHANGELOG_ENTRY/" "$SPEC_FILE"
else
    printf '\n%%changelog\n%b' "$CHANGELOG_ENTRY" >> "$SPEC_FILE"
fi

echo "  -> [DONE] Successfully patched $SPEC_FILE."
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
