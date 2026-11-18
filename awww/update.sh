#!/bin/bash
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="awww.spec"
NAME="awww"
PACKAGER="Ackerman-00 <no-reply>"
UPSTREAM_URL="https://codeberg.org/LGFae/awww"

echo "Checking for upstream updates on codeberg.org/LGFae/awww..."

LATEST_TAG=$(curl -sL --max-time 30 "https://codeberg.org/api/v1/repos/LGFae/awww/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name',''))" 2>/dev/null)

if [ -z "$LATEST_TAG" ]; then
    echo "  -> [SKIP] Release feed unreachable (host down or DNS). Keeping $(grep -E '^Version:' "$SPEC_FILE" | awk '{print $2}')."
    exit 0
fi

VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')

echo "Latest upstream tag: $LATEST_TAG (version: $VERSION)"

CURRENT_VERSION=$(grep "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" == "$VERSION" ]; then
    echo "Package is already at the latest version ($VERSION). No update needed."
    exit 0
fi

echo "Updating: $CURRENT_VERSION -> $VERSION"

ARCHIVE_URL="$UPSTREAM_URL/archive/$LATEST_TAG.tar.gz"
ARCHIVE_FILE="$NAME-$VERSION.tar.gz"
if ! curl -sL --max-time 300 --fail -o "$ARCHIVE_FILE" "$ARCHIVE_URL"; then
    rm -f "$ARCHIVE_FILE"
    echo "Error: $ARCHIVE_URL did not download."
    exit 1
fi
if ! tar tzf "$ARCHIVE_FILE" >/dev/null 2>&1; then
    rm -f "$ARCHIVE_FILE"
    echo "Error: $ARCHIVE_URL is not a valid tarball."
    exit 1
fi

SHA256=$(sha256sum "$ARCHIVE_FILE" | awk '{print $1}')
for old in "$NAME"-*.tar.gz; do
    [ -e "$old" ] || continue
    [ "$old" = "$ARCHIVE_FILE" ] && continue
    rm -f "$old"
done

sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i "s|^Source0:.*|Source0:        %{name}-%{version}.tar.gz|" "$SPEC_FILE"
if grep -q '^# sha256:' "$SPEC_FILE"; then
    sed -i -E "s|^# sha256:.*|# sha256: $SHA256|" "$SPEC_FILE"
else
    sed -i "/^Source0:/a # sha256: $SHA256" "$SPEC_FILE"
fi

DATE_STRING=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE_STRING $PACKAGER - $VERSION-1"
    echo "- Update to version $VERSION"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE (sha256 $SHA256)."
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
