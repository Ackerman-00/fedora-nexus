#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
REPO="sonorahq/sonora"
SPEC_FILE="sonora.spec"
PACKAGER="Ackerman-00 <no-reply>"
LATEST_TAG=$(git ls-remote --tags https://github.com/$REPO.git 2>/dev/null | awk '{print $2}' | sed 's|refs/tags/||;s/\^{}//' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)
LATEST_VERSION=$(echo "$LATEST_TAG" | sed 's/^v//')
echo "Checking for upstream updates on $REPO..."
if [ -z "$LATEST_VERSION" ]; then
    echo "Error: failed to fetch latest tag." >&2
    exit 1
fi
CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')
echo "Latest upstream: $LATEST_TAG"
if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo "Package already at $LATEST_VERSION. No update needed."
    exit 0
fi
BINARY_URL="https://github.com/$REPO/releases/download/$LATEST_TAG/sonora-$LATEST_TAG-x86_64-unknown-linux-gnu"
SRC_URL="https://github.com/$REPO/archive/refs/tags/$LATEST_TAG.tar.gz"
if ! curl --output /dev/null --silent --location --head --fail "$BINARY_URL"; then
    echo "No prebuilt binary for $LATEST_TAG (skip)."
    exit 0
fi
if ! curl --output /dev/null --silent --location --head --fail "$SRC_URL"; then
    echo "No source tarball for $LATEST_TAG (skip)."
    exit 0
fi
BINARY_SHA256=$(curl -fsSL --retry 3 --connect-timeout 30 "$BINARY_URL" | sha256sum | awk '{print $1}')
SRC_SHA256=$(curl -fsSL --retry 3 --connect-timeout 30 "$SRC_URL" | sha256sum | awk '{print $1}')
sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "0,/^# sha256: .*/{s/^# sha256: .*/# sha256: $BINARY_SHA256/}" "$SPEC_FILE"
python3 - "$SPEC_FILE" "$SRC_SHA256" <<'PYEOF'
import sys
path, sha = sys.argv[1], sys.argv[2]
lines = open(path).read().splitlines(keepends=True)
seen = 0
for i, line in enumerate(lines):
    if line.startswith("# sha256:"):
        seen += 1
        if seen == 2:
            lines[i] = f"# sha256: {sha}\n"
open(path, "w").write("".join(lines))
PYEOF
DEB_DATE=$(date -u +"%a %b %d UTC %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DEB_DATE $PACKAGER - $LATEST_VERSION-1"
    echo "- Repackage the upstream prebuilt x86_64 binary"
} >> "$SPEC_FILE"
echo "Updated sonora to $LATEST_VERSION"
