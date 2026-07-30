#!/bin/bash

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

# Try to extract version from the AppImage
VERSION=""
EXTRACTED=0

# Method 1: extract with unsquashfs
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
# Method 2: Python-based extract (fallback when unsquashfs not available)
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

    # .NET/Avalonia apps: version in sq.version (NuSpec XML)
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

    # Electron apps: version in package.json
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

    # No wildcard recursive grep — it picks up dependency versions (e.g. Stripe billing SDK "19.2.5")
    # sq.version is the ONLY authoritative source for .NET/Avalonia app versions.

    rm -rf "$TMPDIR/squashfs-root" "$TMPDIR/squashfs.img"
fi

# Validate extracted version (reject implausible values like dependency versions)
if [ -n "$VERSION" ]; then
    MAJOR="${VERSION%%.*}"
    if [ "$MAJOR" -gt 5 ] 2>/dev/null; then
        echo "ERROR: Extracted version $VERSION has implausible major version $MAJOR"
        VERSION=""
    fi
fi

# Update spec
if [ -n "$VERSION" ] && [ "$VERSION" != "$CURRENT_VERSION" ]; then
    echo "Detected version: $VERSION ($CURRENT_VERSION -> $VERSION)"
    sed -i "s/^Version:.*/Version:        $VERSION/" "$SPEC_FILE"
    sed -i "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
else
    VERSION="$CURRENT_VERSION"
    echo "Version unchanged: $VERSION"
fi

# Update sha256 comment
if grep -q "^# sha256:" "$SPEC_FILE"; then
    sed -i "s/^# sha256:.*/# sha256: $NEW_SHA/" "$SPEC_FILE"
else
    sed -i "/^Source0:/a # sha256:  $NEW_SHA" "$SPEC_FILE"
fi

# Update changelog
DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $VERSION-1"
    echo "- Auto-update to $VERSION via update.sh"
} >> "$SPEC_FILE"

echo "Spec file updated to version $VERSION."
