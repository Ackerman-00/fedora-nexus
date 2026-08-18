#!/bin/bash
# update.sh for Ghostty (Deb Repackaging Build)
# Ghostty itself publishes no Linux binaries on GitHub; the official install
# docs point Linux users to the community-built Ubuntu .deb from
# mkasberg/ghostty-ubuntu. We repackage that .deb (noble/24.04 variant, the
# oldest glibc baseline => best Fedora compatibility).

SPEC_FILE="ghostty.spec"
GITHUB_REPO="mkasberg/ghostty-ubuntu"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Release tags look like "1.3.1-0-ppa2" (Ghostty version + PPA build counter).
# Sorting with -V orders both version bumps and counter bumps correctly.
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+-[0-9]+-ppa[0-9]+$' | sort -V | tail -1)

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Failed to fetch latest tag from mkasberg/ghostty-ubuntu. Check connection."
    exit 1
fi

# 1.3.1-0-ppa2 -> Ghostty version "1.3.1" and .deb asset version "1.3.1-0.ppa2"
GHOSTTY_VERSION=$(echo "$LATEST_TAG" | cut -d- -f1)
DEB_VER="${GHOSTTY_VERSION}-0.${LATEST_TAG##*-}"

# Grab the current values from the spec file
CURRENT_TAG=$(grep -E "^%global ppatag" "$SPEC_FILE" | awk '{print $3}')
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_TAG" == "$LATEST_TAG" ]; then
    echo "Package is already at the latest PPA release ($LATEST_TAG). No update needed."
    exit 0
fi

echo "Update found: $CURRENT_TAG -> $LATEST_TAG"

# A tag is pushed before its release assets are built and uploaded, and the
# maintainer re-runs releases (e.g. ppa2 follows ppa1 for the same version).
# Bumping onto a tag whose .deb is missing pins a Source0 that 404s and breaks
# every COPR rebuild of that NVR, so only bump once the .deb really exists.
DEB_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/ghostty_${DEB_VER}_amd64_24.04.deb"
echo "  -> [CHECK] Verifying $DEB_URL"
if ! curl --output /dev/null --silent --location --head --fail "$DEB_URL"; then
    echo "  -> [SKIP] Release assets for $LATEST_TAG are not published (yet). Keeping $CURRENT_TAG."
    exit 0
fi

# 1. Update the Ghostty version (and reset Release when it changed)
if [ "$CURRENT_VERSION" != "$GHOSTTY_VERSION" ]; then
    sed -i -E "s/^Version:.*/Version:        %{ghostty_version}/" "$SPEC_FILE"
    sed -i -E "s/^%global ghostty_version.*/%global ghostty_version $GHOSTTY_VERSION/" "$SPEC_FILE"
fi
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

# 2. Update the PPA release tag and the .deb asset version; Source0 expands from
#    these macros so the download URL follows automatically.
sed -i -E "s/^%global ppatag.*/%global ppatag $LATEST_TAG/" "$SPEC_FILE"
sed -i -E "s/^%global debver.*/%global debver $DEB_VER/" "$SPEC_FILE"

# 3. Replace changelog with single entry
DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $GHOSTTY_VERSION-1"
    echo "- Auto-update to upstream ghostty release $GHOSTTY_VERSION (PPA release $LATEST_TAG)"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."

# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).

