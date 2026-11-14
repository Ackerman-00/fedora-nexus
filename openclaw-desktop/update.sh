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

SPEC_FILE="openclaw-desktop.spec"
MANIFEST_URL="https://github.com/openclaw/openclaw/releases/latest/download/latest.json"

echo "Checking for upstream companion-app updates..."

LATEST_JSON=$(curl -fsSL -m 60 "$MANIFEST_URL") || {
    echo "Error: failed to fetch $MANIFEST_URL" >&2
    exit 1
}

read LATEST_VERSION LATEST_SHA < <(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
v = d['version']
sha = next((a['sha256'] for a in d.get('linuxPublication', {}).get('assets', []) if a['name'] == f'OpenClaw-{v}-amd64.deb'), '')
print(v, sha)
" "$LATEST_JSON")

if [ -z "$LATEST_VERSION" ] || [ -z "$LATEST_SHA" ]; then
    echo "No linux x86_64 .deb in the companion manifest (version=$LATEST_VERSION sha=$LATEST_SHA)."
    echo "Upstream shipped a macOS-only release; keeping the current pin."
    exit 0
fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    CURRENT_SHA=$(grep -E "^# sha256:" "$SPEC_FILE" | head -1 | awk '{print $3}')
    if [ "$CURRENT_SHA" != "$LATEST_SHA" ]; then
        echo "Upstream respinned $LATEST_VERSION (sha256 $CURRENT_SHA -> $LATEST_SHA); re-pinning."
        sed -i -E "s|^# sha256:.*|# sha256:  $LATEST_SHA|" "$SPEC_FILE"
    else
        echo "Already up to date ($CURRENT_VERSION)."
    fi
    exit 0
fi

DEB_URL="https://github.com/openclaw/openclaw/releases/download/v$LATEST_VERSION/OpenClaw-$LATEST_VERSION-amd64.deb"
HTTP=$(curl -s -o /dev/null -w '%{http_code}' -I -L --max-time 60 "$DEB_URL")
if [ "$HTTP" != "200" ]; then
    echo "Asset returns HTTP $HTTP; not bumping."
    exit 0
fi

echo "Update: $CURRENT_VERSION -> $LATEST_VERSION"

sed -i -E "s/^Version:.*/Version:        $LATEST_VERSION/" "$SPEC_FILE"
sed -i -E "s/^Release:.*/Release:        1%{?dist}/" "$SPEC_FILE"
sed -i -E "s|^# sha256:.*|# sha256:  $LATEST_SHA|" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE Ackerman-00 <no-reply> - $LATEST_VERSION-1"
    echo "- Update to upstream release $LATEST_VERSION"
} >> "$SPEC_FILE"

echo "Successfully updated to $LATEST_VERSION (sha256 $LATEST_SHA)."
