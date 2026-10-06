#!/bin/bash
# update.sh for DesignCraft (upstream .rpm repack)

SPEC_FILE="designcraft.spec"
GITHUB_REPO="storytold/designcraft"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Exclude prereleases: an -rc rpm is an unstable NVR, never ship it as current.
LATEST_TAG=$(git ls-remote --tags "https://github.com/$GITHUB_REPO.git" 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | grep -vEi '(alpha|beta|rc[0-9]*|[-.]pre|[-.]dev|nightly|canary)' | sort -V | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch latest stable tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    # Asset name carries the bare version (no v prefix).
    RPM_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/designcraft-${LATEST_VERSION}-linux-x86_64.rpm"
    echo "  -> [CHECK] Verifying $RPM_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$RPM_URL"; then
        echo "  -> [SKIP] Linux x86_64 rpm for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    # A tag can exist while its assets are still uploading; confirm first.
    # Plain curl, no gh (bare checkout has no gh CLI).
    API_JSON=$(curl -sL --max-time 30 -H "Accept: application/vnd.github+json" \
        ${GITHUB_TOKEN:+-H "Authorization: token $GITHUB_TOKEN"} \
        "https://api.github.com/repos/$GITHUB_REPO/releases/tags/$LATEST_TAG" 2>/dev/null)
    if [ -z "$API_JSON" ]; then
        echo "  -> [SKIP] Release API unreachable for $LATEST_TAG. Keeping $CURRENT_VERSION."
        exit 0
    fi
    if ! printf '%s' "$API_JSON" | grep -q "\"name\":\"designcraft-${LATEST_VERSION}-linux-x86_64.rpm\""; then
        echo "  -> [SKIP] Release $LATEST_TAG has no designcraft-${LATEST_VERSION}-linux-x86_64.rpm asset yet. Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # Source0 embeds %{version}; only the tag literal needs refreshing.
    sed -i -E "s|releases/download/v[^/]+/designcraft-|releases/download/${LATEST_TAG}/designcraft-|" "$SPEC_FILE"

    # Refresh the pinned sha256 (teardown-sweep verifies Source0 against it).
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
