#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
ZGR="otter-shell/zoolander"
ZLR="otter-shell/zooland"

API_ZGR="https://git.pika-os.com/api/v1/repos/$ZGR"
API_ZLR="https://git.pika-os.com/api/v1/repos/$ZLR"
SPEC_FILE="zoolander-git.spec"
PACKAGER="Ackerman-00 <no-reply>"

ZL_COMMIT=$(curl -sL "$API_ZGR/commits/main" | jq -r '.sha')
ZL_DATE_RAW=$(curl -sL "$API_ZGR/commits/main" | jq -r '.commit.committer.date')
ZL_SHORT=${ZL_COMMIT:0:7}
ZL_DATE=$(date -u -d "$ZL_DATE_RAW" +%Y%m%d%H%M%S)

ZOOLAND_COMMIT=$(curl -sL "$API_ZLR/commits/main" | jq -r '.sha')
ZOOLAND_TAG=$(curl -sL "$API_ZLR/tags" | jq -r '.[0].name')
if [ -z "$ZOOLAND_TAG" ] || [ "$ZOOLAND_TAG" == "null" ]; then
    ZOOLAND_TAG="v0.1.49"
fi

echo "Checking for upstream updates on $ZGR / $ZLR..."
if [ -z "$ZL_COMMIT" ] || [ "$ZL_COMMIT" == "null" ]; then
    echo "Error: failed to fetch zoolander commit." >&2
    exit 1
fi
if [ -z "$ZOOLAND_COMMIT" ] || [ "$ZOOLAND_COMMIT" == "null" ]; then
    echo "Error: failed to fetch zooland commit." >&2
    exit 1
fi

CURRENT_ZL=$(grep -oP 'Source0:.*archive/\K[0-9a-f]+' "$SPEC_FILE")
CURRENT_ZO=$(grep -E '^%global zooland_commit' "$SPEC_FILE" | awk '{print $3}')

if [ "$CURRENT_ZL" = "$ZL_COMMIT" ] && [ "$CURRENT_ZO" = "$ZOOLAND_COMMIT" ]; then
    echo "Already at latest commits."
    exit 0
fi
echo "New zoolander: ${CURRENT_ZL:0:7} -> ${ZL_COMMIT:0:7}; zooland: ${CURRENT_ZO:0:7} -> ${ZOOLAND_COMMIT:0:7}"

rm -f zoolander-*.tar.gz zooland-*.tar.gz
ZGRL_TARBALL="zoolander-$ZL_COMMIT.tar.gz"
ZOLR_TARBALL="zooland-$ZOOLAND_COMMIT.tar.gz"
curl -fsSL --retry 3 --connect-timeout 30 "https://git.pika-os.com/api/v1/repos/$ZGR/archive/$ZL_COMMIT.tar.gz" -o "$ZGRL_TARBALL" || { echo "Download failed (zoolander)." >&2; exit 1; }
curl -fsSL --retry 3 --connect-timeout 30 "https://git.pika-os.com/api/v1/repos/$ZLR/archive/$ZOOLAND_COMMIT.tar.gz" -o "$ZOLR_TARBALL" || { echo "Download failed (zooland)." >&2; exit 1; }
tar -tzf "$ZGRL_TARBALL" > /dev/null
tar -tzf "$ZOLR_TARBALL" > /dev/null
ZL_SHA=$(sha256sum "$ZGRL_TARBALL" | awk '{print $1}')
ZO_SHA=$(sha256sum "$ZOLR_TARBALL" | awk '{print $1}')
sed -i -E "s/^%global zooland_commit.*/%global zooland_commit   $ZOOLAND_COMMIT/" "$SPEC_FILE"
sed -i -E "s/^%global shortcommit.*/%global shortcommit     ${ZL_COMMIT:0:7}/" "$SPEC_FILE"
sed -i -E "s/^%global gitdate.*/%global gitdate         $ZL_DATE/" "$SPEC_FILE"
sed -i -E "s/^%global base_version.*/%global base_version    ${ZOOLAND_TAG#v}/" "$SPEC_FILE"
sed -i -E "s/^Source0: .*/Source0:        https:\/\/git.pika-os.com\/api\/v1\/repos\/otter-shell\/zoolander\/archive\/$ZL_COMMIT.tar.gz#\/zoolander-$ZL_COMMIT.tar.gz/" "$SPEC_FILE"
sed -i -E "s/^Source1: .*/Source1:        https:\/\/git.pika-os.com\/api\/v1\/repos\/otter-shell\/zooland\/archive\/$ZOOLAND_COMMIT.tar.gz#\/zooland-$ZOOLAND_COMMIT.tar.gz/" "$SPEC_FILE"
python3 - "$SPEC_FILE" "$ZL_SHA" "$ZO_SHA" <<'PYEOF'
import sys
path, zl, zo = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(path).read().splitlines(keepends=True)
seen = 0
for i, line in enumerate(lines):
    if line.startswith("# sha256:"):
        seen += 1
        lines[i] = f"# sha256: {zl if seen == 1 else zo}\n"
open(path, "w").write("".join(lines))
PYEOF
sed -i -E "s/^Release: .*/Release:        1%{?dist}/" "$SPEC_FILE"
DEB_DATE=$(date -u +"%a %b %d UTC %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DEB_DATE $PACKAGER - ${ZOOLAND_TAG#v}+git${ZL_DATE}.${ZL_SHORT}-1"
    echo "- Nightly sync with upstream main branch (Commit: ${ZL_COMMIT:0:7})"
} >> "$SPEC_FILE"
echo "Updated zoolander-git to ${ZL_COMMIT:0:7}; zooland ${ZOOLAND_COMMIT:0:7}"
