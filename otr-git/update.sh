#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
REPO="general-packages/otr"
API="https://git.pika-os.com/api/v1/repos/$REPO"
SPEC_FILE="otr-git.spec"
PACKAGER="Ackerman-00 <no-reply>"
LATEST_COMMIT=$(curl -sL "$API/commits/main" | jq -r '.sha')
LATEST_DATE_RAW=$(curl -sL "$API/commits/main" | jq -r '.commit.committer.date')
LATEST_DATE=$(date -u -d "$LATEST_DATE_RAW" +%Y%m%d%H%M%S)

CURRENT_COMMIT=$(grep -E "^%global commit" "$SPEC_FILE" | awk '{print $3}')

echo "Checking for upstream updates on $REPO..."
if [ -z "$LATEST_COMMIT" ] || [ "$LATEST_COMMIT" == "null" ]; then
    echo "Error: failed to fetch latest commit." >&2
    exit 1
fi

if [ "$CURRENT_COMMIT" = "$LATEST_COMMIT" ]; then
    echo "Already at latest commit."
    exit 0
fi

SHORT_COMMIT=${LATEST_COMMIT:0:7}
BASE_TAG=$(curl -fsSL "$API/releases" | jq -r '.[0].tag_name')
BASE_VER=${BASE_TAG#v}
if [ -z "$BASE_VER" ] || [ "$BASE_VER" == "null" ]; then
    echo "Error: failed to read base version from VERSION file." >&2
    exit 1
fi
TARBALL="otr-$SHORT_COMMIT-source.tar.gz"
rm -f otr-*.tar.gz
curl -fsSL --retry 3 --connect-timeout 30 "https://git.pika-os.com/api/v1/repos/$REPO/archive/$LATEST_COMMIT.tar.gz" -o "otr-$SHORT_COMMIT.tar.gz" || { echo "Download failed." >&2; exit 1; }
tar -tzf "otr-$SHORT_COMMIT.tar.gz" > /dev/null || { echo "Corrupt tarball." >&2; exit 1; }
SHA256=$(sha256sum "otr-$SHORT_COMMIT.tar.gz" | awk '{print $1}')
SIZE=$(stat -c%s "otr-$SHORT_COMMIT.tar.gz")
sed -i -E "s/^%global commit.*/%global commit          $LATEST_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global shortcommit.*/%global shortcommit     $SHORT_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global gitdate.*/%global gitdate         $LATEST_DATE/" "$SPEC_FILE"
sed -i -E "s/^%global base_version.*/%global base_version    $BASE_VER/" "$SPEC_FILE"
sed -i -E "s/^Source0: .*/Source0:        https:\/\/git.pika-os.com\/api\/v1\/repos\/general-packages\/otr\/archive\/$LATEST_COMMIT.tar.gz#\/otr-$LATEST_COMMIT.tar.gz/" "$SPEC_FILE"
sed -i -E "s/^# sha256: .*/# sha256: $SHA256/" "$SPEC_FILE"
sed -i -E "s/^Release: .*/Release:        1%{?dist}/" "$SPEC_FILE"
DEB_DATE=$(date -u +"%a %b %d UTC %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DEB_DATE $PACKAGER - ${BASE_VER}+git${LATEST_DATE}.${SHORT_COMMIT}-1"
    echo "- Nightly sync with upstream main branch (Commit: $SHORT_COMMIT)"
} >> "$SPEC_FILE"
echo "Updated otr-git to $LATEST_COMMIT"
