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

SPEC_FILE="bibata-cursor-theme.spec"
GITHUB_REPO="ful1e5/Bibata_Cursor"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# NOTE: upstream tags may mix v-prefixed and bare schemes (e.g. v1.0.7 vs 1.0.8);
# plain `sort -V` orders "v…" after bare versions and picks the WRONG latest
# (hellwal 1.0.8 downgrade, 2026-09-15). Sort by the v-stripped version key
# but keep the exact tag (download URLs need it verbatim).
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sed -E 's/^v?([0-9].*)/\1 &/' | sort -V -k1,1 | tail -1 | awk '{print $2}')
VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$VERSION" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

echo "Latest upstream tag: $LATEST_TAG (version: $VERSION)"

CURRENT_VERSION=$(grep "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" == "$VERSION" ]; then
    echo "Package is already at the latest version ($VERSION). No update needed."
    exit 0
fi

echo "Updating: $CURRENT_VERSION -> $VERSION"

# A tag can exist before its release asset is uploaded (and upstreams do delete
# assets when re-running a release). Bumping onto a tag whose asset is missing
# pins a Source0 that 404s and breaks every rebuild of that NVR.
ASSET_URL="https://github.com/$GITHUB_REPO/releases/download/v${VERSION}/Bibata.tar.xz"
echo "  -> [CHECK] Verifying $ASSET_URL"
if ! curl --output /dev/null --silent --location --head --fail "$ASSET_URL"; then
    echo "  -> [SKIP] Release asset for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
    exit 0
fi

sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $VERSION-1"
    echo "- Update to version $VERSION"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."
# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
# Guard: an updater must never leave a spec without its header. If the
# changelog rewrite or a sed wiped the file, restore from git and fail loudly.
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
