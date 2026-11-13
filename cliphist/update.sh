#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="cliphist.spec"
GITHUB_REPO="sentriz/cliphist"
PACKAGER="Ackerman-00 <no-reply>"

echo "Checking for upstream updates on $GITHUB_REPO..."

LATEST_TAG=$(git ls-remote --tags https://github.com/$GITHUB_REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v?[0-9]' | sed -E 's/^v?([0-9].*)/\1 &/' | sort -V -k1,1 | tail -1 | awk '{print $2}')

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "Error: Failed to fetch cliphist version from GitHub. Check API limits or connection."
    exit 1
fi

LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//;s@-@.@g')

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"

    sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
    sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"

    sed -i -E "s|archive/v[^/]*/cliphist-v[^/]*\.tar\.gz|archive/v$LATEST_VERSION/cliphist-v$LATEST_VERSION.tar.gz|" "$SPEC_FILE"

    # vendored deps: regenerated with the version, never carried over
    if ! command -v go >/dev/null 2>&1; then
        echo "FATAL: the go toolchain is required to regenerate the vendor tarball." >&2
        git checkout -- "$SPEC_FILE" 2>/dev/null || true
        exit 1
    fi
    TMPDIR_V=$(mktemp -d) || exit 1
    trap 'rm -rf "$TMPDIR_V"' EXIT
    SRC_URL="https://github.com/$GITHUB_REPO/archive/v$LATEST_VERSION/cliphist-v$LATEST_VERSION.tar.gz"
    if ! curl -sSfL "$SRC_URL" -o "$TMPDIR_V/src.tar.gz"; then
        echo "FATAL: cannot download $SRC_URL to vendor its modules." >&2
        git checkout -- "$SPEC_FILE" 2>/dev/null || true
        exit 1
    fi
    tar -xzf "$TMPDIR_V/src.tar.gz" -C "$TMPDIR_V" || exit 1
    if ! ( cd "$TMPDIR_V/cliphist-$LATEST_VERSION" && GOFLAGS= go mod vendor ); then
        echo "FATAL: go mod vendor failed for $LATEST_VERSION." >&2
        git checkout -- "$SPEC_FILE" 2>/dev/null || true
        exit 1
    fi
    ( cd "$TMPDIR_V/cliphist-$LATEST_VERSION" \
        && tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner -cf "$TMPDIR_V/vendor.tar" vendor \
        && gzip -n -9 -c "$TMPDIR_V/vendor.tar" > "$_update_sh_dir/cliphist-$LATEST_VERSION-vendor.tar.gz" ) || exit 1
    find "$_update_sh_dir" -maxdepth 1 -name 'cliphist-*-vendor.tar.gz' ! -name "cliphist-$LATEST_VERSION-vendor.tar.gz" -delete
    VENDOR_SHA=$(sha256sum "$_update_sh_dir/cliphist-$LATEST_VERSION-vendor.tar.gz" | awk '{print $1}')
    sed -i -E "s|^# sha256:.*|# sha256:  $VENDOR_SHA|" "$SPEC_FILE"
    echo "Vendored modules for $LATEST_VERSION (sha256 $VENDOR_SHA)."

    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $LATEST_VERSION-1"
        echo "- Auto-update to upstream release $LATEST_TAG"
    } >> "$SPEC_FILE"
else
    echo "Already up to date ($CURRENT_VERSION)."
fi
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
