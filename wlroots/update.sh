#!/bin/bash

# Configuration
SPEC_FILE="wlroots.spec"
GITLAB_REPO="wlroots/wlroots"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITLAB_REPO..."

# Fetch the latest release tag from GitLab API
LATEST_VERSION=$(curl -s "https://gitlab.freedesktop.org/api/v4/projects/${GITLAB_REPO//\//%2F}/releases" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data and len(data) > 0:
        # Filter out pre-release versions (rc, beta, alpha, etc.)
        releases = [r['tag_name'] for r in data if all(x not in r['tag_name'].lower() for x in ['rc', 'beta', 'alpha', '~'])]
        print(releases[0] if releases else data[0]['tag_name'])
except:
    sys.exit(1)
")

if [ -z "$LATEST_VERSION" ]; then
    # Fallback: use tags API
    LATEST_VERSION=$(curl -s "https://gitlab.freedesktop.org/api/v4/projects/${GITLAB_REPO//\//%2F}/repository/tags?per_page=1&order_by=version" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data:
        print(data[0]['name'])
except:
    sys.exit(1)
")
fi

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch the latest version. Check API limits or connection."
    exit 1
fi

# Handle tilde in version (rc versions like 0.20.0~rc2)
SPEC_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')
# The spec uses %global tag %{gsub %{version} ~ -} so 0.20.0~rc2 becomes tag 0.20.0-rc2
# Strip 'v' prefix if present
LATEST_VERSION="${LATEST_VERSION#v}"

if [ "$SPEC_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $SPEC_VERSION -> $LATEST_VERSION"

    # 1. Update the Version and Release fields
    sed -i "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # 2. Auto-generate the Changelog entry
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    NEW_CHANGELOG="* $DATE $PACKAGER - $LATEST_VERSION-1\n- Auto-update to version $LATEST_VERSION"

    # 3. Wipe out old logs below %changelog and replace with the single new entry
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    echo "%changelog" >> "$SPEC_FILE"
    echo -e "$NEW_CHANGELOG" >> "$SPEC_FILE"

    echo "Upstream source updated from $SPEC_VERSION to $LATEST_VERSION."
else
    echo "Package version $SPEC_VERSION is up to date."
fi
