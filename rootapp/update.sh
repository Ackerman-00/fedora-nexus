#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="rootapp.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
APPIMAGE_URL="https://installer.rootapp.com/installer/Linux/X64/Root.AppImage"

echo "Checking for rootapp updates..."

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

curl -sL -o "$TMPDIR/Root.AppImage" "$APPIMAGE_URL"
NEW_SHA=$(sha256sum "$TMPDIR/Root.AppImage" | awk '{print $1}')

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')
CURRENT_SHA=$(grep -E "^# sha256:" "$SPEC_FILE" | awk '{print $3}')

if [ -n "$CURRENT_SHA" ] && [ "$NEW_SHA" = "$CURRENT_SHA" ]; then
    echo "Package is up to date (sha256: $CURRENT_SHA)."
    exit 0
fi

echo "Downloaded AppImage SHA256: $NEW_SHA"
if [ -n "$CURRENT_SHA" ]; then
    echo "Previous SHA256: $CURRENT_SHA"
fi
echo "Update detected."

VERSION=""
EXTRACTED=0

if command -v unsquashfs &>/dev/null; then
    OFFSET=$(od -An -N8 -t u8 -j 40 "$TMPDIR/Root.AppImage" | tr -d ' ')
    MAGIC=$(dd if="$TMPDIR/Root.AppImage" bs=1 skip=$OFFSET count=4 2>/dev/null)

    if [ "$MAGIC" != "hsqs" ]; then
        OFFSET=$(python3 -c "
with open('$TMPDIR/Root.AppImage', 'rb') as f:
    d = f.read()
    p = d.find(b'hsqs', 200000)
    print(p if p >= 0 else 0)
")
    fi

    dd if="$TMPDIR/Root.AppImage" bs=$OFFSET skip=1 of="$TMPDIR/squashfs.img" 2>/dev/null
    unsquashfs -d "$TMPDIR/squashfs-root" -f "$TMPDIR/squashfs.img" >/dev/null 2>&1

    if [ -d "$TMPDIR/squashfs-root" ]; then
        EXTRACTED=1
    fi
elif command -v python3 &>/dev/null; then
    chmod +x "$TMPDIR/Root.AppImage"
    cd "$TMPDIR"
    "$TMPDIR/Root.AppImage" --appimage-extract >/dev/null 2>&1 || true
    if [ -d "$TMPDIR/squashfs-root" ]; then
        EXTRACTED=1
    fi
fi


if [ "$EXTRACTED" = "1" ]; then
    ROOT="$TMPDIR/squashfs-root"

    if [ -z "$VERSION" ] && [ -f "$ROOT/usr/bin/sq.version" ]; then
        VERSION=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    root = ET.parse('$ROOT/usr/bin/sq.version').getroot()
    ns = {'ns': 'http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd'}
    m = root.find('.//ns:metadata/ns:version', ns)
    if m is not None and m.text:
        print(m.text)
    else:
        m2 = root.find('.//metadata/version')
        if m2 is not None and m2.text:
            print(m2.text)
except:
    print('')
")
    fi

    if [ -z "$VERSION" ] && [ -f "$ROOT/resources/app/package.json" ]; then
        VERSION=$(python3 -c "
import json
try:
    d = json.load(open('$ROOT/resources/app/package.json'))
    print(d.get('version', ''))
except:
    print('')
")
    fi


    rm -rf "$TMPDIR/squashfs-root" "$TMPDIR/squashfs.img"
fi

if [ -n "$VERSION" ]; then
    MAJOR="${VERSION%%.*}"
    if [ "$MAJOR" -gt 5 ] 2>/dev/null; then
        echo "ERROR: Extracted version $VERSION has implausible major version $MAJOR"
        VERSION=""
    fi
fi

if [ -n "$VERSION" ] && [ "$VERSION" != "$CURRENT_VERSION" ]; then
    echo "Detected version: $VERSION ($CURRENT_VERSION -> $VERSION)"
    sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
else
    VERSION="$CURRENT_VERSION"
    echo "Version unchanged: $VERSION"
fi

if grep -q "^# sha256:" "$SPEC_FILE"; then
    sed -i "s/^# sha256:.*/# sha256: $NEW_SHA/" "$SPEC_FILE"
else
    sed -i "/^Source0:/a # sha256:  $NEW_SHA" "$SPEC_FILE"
fi

if [ "$VERSION" != "$CURRENT_VERSION" ] || [ "$NEW_SHA" != "$CURRENT_SHA" ]; then
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $VERSION-1"
        echo "- Auto-update to $VERSION via update.sh"
    } >> "$SPEC_FILE"
fi

echo "Spec file updated to version $VERSION."
if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
