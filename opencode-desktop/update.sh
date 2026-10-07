#!/bin/bash

# Run this from its own package directory. update-engine.yml does `pushd <pkg>`
# first; running update.sh from the repo root instead let the changelog append
# create a stray <pkg>.spec at the repo root, and the Name: check then reported
# a false corruption (hit twice, 2026-10-07: stray umbriel-git.spec, then 32
# stray root specs during an agent sweep).
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi
# update.sh for opencode-desktop (upstream .deb repack; the .rpm carries a
# strip-damaged bundled opencode-cli, the same-release .deb verified good)

SPEC_FILE="opencode-desktop.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
STABLE_URL="https://opencode.ai/download/stable/linux-x64-deb"

echo "Checking for upstream updates..."

# The stable URL 302-redirects to the versioned file
# (.../files/bin/<version>/opencode-desktop-linux-amd64.deb);
# the redirect target is the version source of truth.
EFFECTIVE_URL=$(curl -sIL -o /dev/null -w '%{url_effective}' --max-time 30 "$STABLE_URL")
LATEST_VERSION=$(echo "$EFFECTIVE_URL" | grep -oP 'files/bin/\K[0-9]+\.[0-9]+\.[0-9]+' | head -1)

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Could not resolve version from $STABLE_URL (got: $EFFECTIVE_URL)."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    DEB_URL="https://opencode.ai/files/bin/$LATEST_VERSION/opencode-desktop-linux-amd64.deb"
    echo "  -> [CHECK] Verifying $DEB_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$DEB_URL"; then
        echo "  -> [SKIP] DEB for $LATEST_VERSION is not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    sed -i -E "s|files/bin/[^/]+/opencode-desktop-linux-amd64.deb|files/bin/%{version}/opencode-desktop-linux-amd64.deb|" "$SPEC_FILE"

    # Refresh the pinned sha256 for the new deb (teardown-sweep verifies
    # Source0 against this pin; a stale pin fails the next run)
    echo "  -> [HASH] Computing sha256 of $DEB_URL"
    SHA256=$(curl -sL "$DEB_URL" | sha256sum | awk '{print $1}')
    if [ -n "$SHA256" ]; then
        sed -i -E "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"
    else
        echo "  -> [WARN] Could not compute sha256; pin left stale on purpose"
    fi

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_VERSION"
    } >> "$SPEC_FILE"

    echo "Successfully patched $SPEC_FILE."
else
    echo "Package is already at $LATEST_VERSION. No update needed."
fi
# Guard: an updater must never leave a spec without its header. If the
# changelog rewrite or a sed wiped the file, restore from git and fail loudly.
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
