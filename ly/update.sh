#!/bin/bash
# update.sh for ly (TUI display manager)

SPEC_FILE="ly.spec"
CODEBERG_REPO="fairyglade/ly"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"

echo "Checking for upstream updates on codeberg.org/$CODEBERG_REPO..."

# Get latest tag via git ls-remote (no rate limit).
# Development happens on Codeberg (GitHub is only a mirror), so the
# authoritative source is codeberg - but codeberg's git service is flaky,
# so retry a few times and fall back to the GitHub mirror for tag detection
# only; source/asset URLs always stay on codeberg.
get_latest_tag() {
    local remote="$1"
    git ls-remote --tags "$remote" 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
}

LATEST_TAG=""
for attempt in 1 2 3; do
    LATEST_TAG=$(get_latest_tag "https://codeberg.org/$CODEBERG_REPO.git")
    [ -n "$LATEST_TAG" ] && break
    echo "  -> [RETRY] Codeberg ls-remote attempt $attempt failed, retrying..."
    sleep 5
done
[ -z "$LATEST_TAG" ] && LATEST_TAG=$(get_latest_tag "https://github.com/$CODEBERG_REPO.git")

if [ -z "$LATEST_TAG" ]; then
    echo "  -> [ERROR] Failed to fetch latest tag."
    exit 1
fi

LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

# Read current version from the spec file
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

# Compare and update
if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "  -> [UPDATE] New version detected: $LATEST_VERSION (Current: $CURRENT_VERSION)"

    # A tag can exist before its release assets do. Bumping on a tag whose
    # sources are missing produces a spec whose Source0/Source1 404s, so every
    # COPR rebuild of that NVR fails. Only bump once everything really exists.
    ARCHIVE_URL="https://codeberg.org/$CODEBERG_REPO/archive/$LATEST_TAG.tar.gz"
    echo "  -> [CHECK] Verifying $ARCHIVE_URL"
    if ! curl --output /dev/null --silent --location --head --retry 3 --max-time 120 --fail "$ARCHIVE_URL"; then
        echo "  -> [SKIP] Source archive for $LATEST_TAG is not available (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    VENDOR_URL="https://codeberg.org/$CODEBERG_REPO/releases/download/$LATEST_TAG/vendor.tar.zst"
    echo "  -> [CHECK] Verifying $VENDOR_URL"
    if ! curl --output /dev/null --silent --location --head --retry 3 --max-time 120 --fail "$VENDOR_URL"; then
        echo "  -> [SKIP] Vendor tarball for $LATEST_TAG is not available (yet). Keeping $CURRENT_VERSION."
        exit 0
    fi

    # The spec pins the vendored Zig dependency hashes via %zig_fetch. If the
    # new release bumped any dependency, its hash lands in the vendor tarball
    # under a new directory while the spec still references the old one, and
    # the COPR build fails at the fetch step. Verify every pinned hash exists.
    echo "  -> [CHECK] Verifying vendored Zig dependency hashes..."
    TMP_DIR=$(mktemp -d)
    trap 'rm -rf "$TMP_DIR"' EXIT
    if ! curl --silent --location --retry 3 --max-time 180 --fail -o "$TMP_DIR/vendor.tar.zst" "$VENDOR_URL"; then
        echo "  -> [ERROR] Failed to download vendor tarball for hash verification."
        exit 1
    fi
    VENDOR_DIRS=$(tar --zstd -tf "$TMP_DIR/vendor.tar.zst" 2>/dev/null | sed -n 's|^zig-pkg/\([^/]*\)/$|\1|p')
    MISSING=0
    while read -r name hash; do
        if ! grep -qx "$hash" <<< "$VENDOR_DIRS"; then
            echo "    -> [MISSING] $name = $hash is not in the $LATEST_TAG vendor tarball"
            MISSING=1
        fi
    done < <(grep -oE '^%global\s+[a-z0-9_]+_hash\s+\S+' "$SPEC_FILE" | awk '{print $2, $3}')
    if [ "$MISSING" -eq 1 ]; then
        echo "  -> [ERROR] Dependency hashes changed in $LATEST_TAG. Update the %global *_hash lines in $SPEC_FILE manually, then re-run."
        exit 1
    fi
    echo "    -> [OK] All pinned dependency hashes present in the vendor tarball"

    # 1. Update the Version and Release fields
    sed -i "s/^Version:\s*.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:\s*.*/Release:        1%{?dist}/" "$SPEC_FILE"

    # 2. Replace changelog with single entry
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_TAG"
    } >> "$SPEC_FILE"

    echo "  -> [DONE] $SPEC_FILE is ready for build."
else
    echo "  -> [OK] ly is already on latest ($CURRENT_VERSION)."
fi