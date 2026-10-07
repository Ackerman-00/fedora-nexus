#!/bin/bash
# update.sh for OpenCADStudio (upstream .AppImage repack)

SPEC_FILE="opencad-studio.spec"
GITHUB_REPO="HakanSeven12/OpenCADStudio"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on $GITHUB_REPO..."

# Tags are weekly vYYYY.N with vYYYY.N.M fix releases (v2026.40.1).
# Exclude prereleases: an -rc AppImage is an unstable NVR, never ship it.
LATEST_TAG=$(git ls-remote --tags "https://github.com/$GITHUB_REPO.git" 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v[0-9]{4}\.[0-9]+(\.[0-9]+)?$' | grep -vEi '(alpha|beta|rc[0-9]*|[-.]pre|[-.]dev|nightly|canary)' | sort -V | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Failed to fetch latest stable tag."
    exit 1
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    # The full tag (with v) is embedded in both the path and the filename.
    APPIMAGE_URL="https://github.com/$GITHUB_REPO/releases/download/$LATEST_TAG/OpenCADStudio-${LATEST_TAG}-linux-x86_64.AppImage"
    echo "  -> [CHECK] Verifying $APPIMAGE_URL"
    if ! curl --output /dev/null --silent --location --head --fail "$APPIMAGE_URL"; then
        echo "  -> [SKIP] Linux x86_64 AppImage for $LATEST_TAG is not published (yet). Keeping $CURRENT_VERSION."
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
    if ! printf '%s' "$API_JSON" | grep -q "\"name\": *\"OpenCADStudio-${LATEST_TAG}-linux-x86_64.AppImage\""; then
        echo "  -> [SKIP] Release $LATEST_TAG has no OpenCADStudio-${LATEST_TAG}-linux-x86_64.AppImage asset yet. Keeping $CURRENT_VERSION."
        exit 0
    fi

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # Source0 embeds the full tag twice (path and filename).
    sed -i -E "s|releases/download/v[^/]+/OpenCADStudio-v[^-]+-linux|releases/download/${LATEST_TAG}/OpenCADStudio-${LATEST_TAG}-linux|" "$SPEC_FILE"

    # Refresh the pinned sha256 (teardown-sweep verifies Source0 against it).
    echo "  -> [HASH] Computing sha256 of $APPIMAGE_URL"
    SHA256=$(curl -sL "$APPIMAGE_URL" | sha256sum | awk '{print $1}')
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
