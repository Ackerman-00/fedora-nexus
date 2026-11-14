#!/bin/bash

# owner 2026-11-14: auto-update disabled; updates are published by Ackerman-00
if [ -z "${NEXUS_OWNER_UPDATE:-}" ]; then
    echo "auto-update disabled (owner rule 2026-11-14); updates are published manually by Ackerman-00"
    exit 0
fi
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="freebuff-desktop.spec"
PACKAGER="Ackerman-00 <no-reply>"
API_URL="https://freebuff.com/api/desktop/download/linux"

echo "Checking for Freebuff desktop updates..."

EFFECTIVE_URL=$(curl -sI --max-time 60 -o /dev/null -w '%{redirect_url}' "$API_URL")
if [ -z "$EFFECTIVE_URL" ]; then echo "Error: upstream redirect unavailable."; exit 1; fi

LATEST_VERSION=$(echo "$EFFECTIVE_URL" | grep -oP 'freebuff-desktop-v\K[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [ -z "$LATEST_VERSION" ]; then echo "Error: could not parse version from $EFFECTIVE_URL"; exit 1; fi

DEB_URL=$(echo "$EFFECTIVE_URL" | grep -oP '\S*Freebuff-[^/]+-linux-amd64\.deb')
if [ -z "$DEB_URL" ]; then echo "Error: redirect did not land on a Freebuff amd64 .deb ($EFFECTIVE_URL)"; exit 1; fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')
CURRENT_SHA=$(grep -E "^# sha256:" "$SPEC_FILE" | head -1 | awk '{print $3}')

WORKDIR=$(mktemp -d) || exit 1
trap 'rm -rf "$WORKDIR"' EXIT

echo "Fetching $DEB_URL"
if ! curl -fsSL --retry 3 --retry-all-errors --max-time 1800 -o "$WORKDIR/pkg.deb" "$DEB_URL"; then
    echo "Error: could not download $DEB_URL; keeping $CURRENT_VERSION." >&2
    exit 1
fi
SHA=$(sha256sum "$WORKDIR/pkg.deb" | awk '{print $1}')

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ] && [ "$SHA" = "$CURRENT_SHA" ]; then
    echo "Package is already at $LATEST_VERSION. No update needed."
    exit 0
fi

DATA_MEMBER=$(ar t "$WORKDIR/pkg.deb" | grep -E '^data\.tar' | head -1)
# explicit pipe decoder
case "$DATA_MEMBER" in
    data.tar.xz)  DEC=(-J) ;;
    data.tar.zst) DEC=(--zstd) ;;
    data.tar.gz)  DEC=(-z) ;;
    *) echo "Error: unexpected data.tar compression in upstream DEB ($DATA_MEMBER)." >&2; exit 1 ;;
esac
if ! ar p "$WORKDIR/pkg.deb" "$DATA_MEMBER" | tar "${DEC[@]}" -tf - > "$WORKDIR/list.txt"; then
    echo "Error: could not list the .deb payload; keeping $CURRENT_VERSION." >&2
    exit 1
fi

# required payload
for member in \
    ./opt/Freebuff/freebuff \
    ./opt/Freebuff/chrome-sandbox \
    ./opt/Freebuff/LICENSE.electron.txt \
    ./usr/share/applications/freebuff.desktop \
    ./usr/share/doc/freebuff/changelog.gz
do
    if ! grep -qx "$member" "$WORKDIR/list.txt"; then
        echo "Error: $LATEST_VERSION no longer ships '$member'; re-derive %install/%files before bumping. Keeping $CURRENT_VERSION." >&2
        exit 1
    fi
done
if ! grep -qE '^\./usr/share/icons/hicolor/[^/]+/apps/freebuff\.png$' "$WORKDIR/list.txt"; then
    echo "Error: $LATEST_VERSION ships no hicolor freebuff.png; the desktop entry would have a dangling Icon=. Keeping $CURRENT_VERSION." >&2
    exit 1
fi

# no payload usr/bin
if grep -qE '^\./usr/bin/' "$WORKDIR/list.txt"; then
    echo "Error: $LATEST_VERSION now ships usr/bin entries; /usr/bin/freebuff belongs to the freebuff CLI package. Re-derive the spec before bumping. Keeping $CURRENT_VERSION." >&2
    exit 1
fi
if grep -E '^\./usr/' "$WORKDIR/list.txt" \
    | grep -vE '^\./usr/(share/?)?$' \
    | grep -vE '^\./usr/share/(applications|doc|icons)(/|$)' \
    | grep -q .; then
    echo "Error: $LATEST_VERSION ships usr/ paths the spec does not install. Re-derive %install/%files before bumping. Keeping $CURRENT_VERSION." >&2
    exit 1
fi

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo "Upstream respinned $CURRENT_VERSION (sha256 $CURRENT_SHA -> $SHA); re-pinning and bumping Release."
    NEW_REL=$(( $(grep -E "^Release:" "$SPEC_FILE" | awk '{print $2}' | sed 's/%.*//') + 1 ))
    NEW_ENTRY="- Re-pin .deb (upstream respinned the tag)"
else
    echo "Update found: $CURRENT_VERSION -> $LATEST_VERSION"
    NEW_REL=1
    NEW_ENTRY="- Update to upstream release $LATEST_VERSION"
fi

sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s|^Source0:.*|Source0:        $DEB_URL|" "$SPEC_FILE"
sed -i -E "s|^# sha256:.*|# sha256: $SHA|" "$SPEC_FILE"
sed -i -E "s|^Release:.*|Release:        ${NEW_REL}%{?dist}|" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $LATEST_VERSION-$NEW_REL"
    echo "$NEW_ENTRY"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."

if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
if ! grep -q "^# sha256: $SHA" "$SPEC_FILE" \
   || ! grep -qE "^Version:[[:space:]]+$LATEST_VERSION$" "$SPEC_FILE" \
   || ! grep -q "^Source0:        $DEB_URL$" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE does not carry the new version/pin/Source0; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi