#!/bin/bash
# update.sh for wlroots (GitLab-hosted)
#
# Uses `git ls-remote --tags` (no HTTP API) for robustness: the GitLab REST
# API intermittently returns 504 Gateway Time-outs under load, which previously
# made this script exit 1 and silently skip version checks on every run of the
# auto-updater (the package could have gone stale unnoticed). ls-remote works
# over the git protocol and is the same mechanism used by every other update.sh
# in this repo.

SPEC_FILE="wlroots.spec"
GIT_URL="https://gitlab.freedesktop.org/wlroots/wlroots.git"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on wlroots..."

# Latest stable tag. wlroots tags are bare versions (0.20.2, 0.20.0-rc5).
# Pre-release tags (rc, beta, alpha, ~) are excluded so we only track stable.
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

# wlroots tags have no 'v' prefix, but strip one defensively.
LATEST_VERSION="${LATEST_TAG#v}"

# Read the current version from the spec (the %global tag macro derives from it).
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    # 1. Update Version and reset Release to 1 (new upstream version)
    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # 2. Replace changelog with a single entry
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
