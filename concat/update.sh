#!/bin/bash
# update.sh for Concat (upstream .rpm repack)

SPEC_FILE="concat.spec"
GITHUB_REPO="jub0t/Concat"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Tags are v-prefixed (v0.2.5); version is bare (0.2.5). Exclude prereleases.
LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | grep -vEi '(alpha|beta|rc[0-9]*|[-.]pre|[-.]dev|nightly|canary)' | sort -V | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch latest tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    RPM_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/Concat-${LATEST_VERSION}-linux-x86_64.rpm"
    echo "  -> [CHECK] Verifying $RPM_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$RPM_URL"; then
        echo "  -> [SKIP] Linux x86_64 rpm for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
    sed -i -E "s|releases/download/[^/]+/Concat-.*-linux-x86_64.rpm|releases/download/$LATEST_TAG/Concat-${LATEST_VERSION}-linux-x86_64.rpm|" "$SPEC_FILE"

    # Refresh the pinned sha256 for the new rpm (teardown-sweep verifies
    # Source0 against this pin; a stale pin fails the next run)
    echo "  -> [HASH] Computing sha256 of $RPM_URL"
    SHA256=$(curl -sL "$RPM_URL" | sha256sum | awk '{print $1}')
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
        echo "- Auto-update to upstream release $LATEST_TAG"
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
