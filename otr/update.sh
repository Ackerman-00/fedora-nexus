#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
REPO="general-packages/otr"
API="https://git.pika-os.com/api/v1/repos/$REPO"
SPEC_FILE="otr.spec"
PACKAGER="Ackerman-00 <no-reply>"
LATEST_TAG=$(curl -fsSL "$API/releases" | jq -r '.[0].tag_name')
LATEST_VERSION=${LATEST_TAG#v}
if [ -z "$LATEST_VERSION" ] || [ "$LATEST_VERSION" == "null" ]; then
    echo "Error: failed to fetch latest release tag." >&2
    exit 1
fi
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')
echo "Checking for upstream updates on $REPO..."
if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo "otr already at $LATEST_VERSION. No update needed."
    exit 0
fi
echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"
curl -fsSL --retry 3 --connect-timeout 30 "https://git.pika-os.com/api/v1/repos/$REPO/archive/v$LATEST_VERSION.tar.gz" -o /tmp/otr-$LATEST_VERSION.tar.gz
tar -tzf /tmp/otr-$LATEST_VERSION.tar.gz > /dev/null || { echo "Corrupt tarball." >&2; rm /tmp/otr-$LATEST_VERSION.tar.gz; exit 1; }
SHA256=$(sha256sum /tmp/otr-$LATEST_VERSION.tar.gz | awk '{print $1}')
rm -f otr-*.tar.gz
sed -i -E "s/^Version: .*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Source0: .*/Source0:        %{url}\/archive\/v$LATEST_VERSION.tar.gz#\/otr-v$LATEST_VERSION.tar.gz/" "$SPEC_FILE"
sed -i -E "s/^# sha256: .*/# sha256: $SHA256/" "$SPEC_FILE"
sed -i -E "s/^Release: .*/Release:        1%{?dist}/" "$SPEC_FILE"
DEB_DATE=$(date -u +"%a %b %d UTC %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DEB_DATE $PACKAGER - $LATEST_VERSION-1"
    echo "- Update to version $LATEST_VERSION"
} >> "$SPEC_FILE"
echo "Updated otr to $LATEST_VERSION"
