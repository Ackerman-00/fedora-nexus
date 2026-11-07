#!/bin/bash

_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="qoder.spec"
PACKAGER="Ackerman-00 <quietcraft@gmail.com>"
FEED="https://download.qoder.com.cn/qoder-app/releases/latest-linux.yml"

echo "Checking for Qoder updates on $FEED..."

if ! YML=$(curl -fsSL --retry 3 --connect-timeout 30 --max-time 60 "$FEED" 2>/dev/null); then
    echo "Error: upstream feed unavailable."
    exit 1
fi

read -r NEW_VER DEB_URL NEW_SHA < <(printf '%s\n' "$YML" | python3 -c "
import sys, re
y = sys.stdin.read()
ver = re.search(r'^version:\s*(\S+)', y, re.M)
debs = re.findall(r'url:\s*(\S*Qoder-linux-amd64\.deb)', y)
shas = re.findall(r'sha256:\s*([0-9a-f]{64})', y)
ver = ver.group(1) if ver else ''
deb = debs[0] if debs else ''
deb_sha = ''
for m in re.finditer(r'- url:\s*(\S+).*?sha256:\s*([0-9a-f]{64})', y, re.S):
    if m.group(1) == deb:
        deb_sha = m.group(2)
        break
print(ver or '-', deb or '-', deb_sha or '-')
")

if [ -z "$NEW_VER" ] || [ "$NEW_VER" = "-" ]; then echo "Error: no version in feed."; exit 1; fi
if [ -z "$DEB_URL" ] || [ "$DEB_URL" = "-" ]; then echo "Error: no x86_64 .deb URL in feed."; exit 1; fi
if [ -z "$NEW_SHA" ] || [ "$NEW_SHA" = "-" ]; then echo "Error: no sha256 for the x86_64 .deb in feed."; exit 1; fi

CURRENT_VERSION=$(grep -E "^Version:" "$SPEC_FILE" | awk '{print $2}')

if [ "$CURRENT_VERSION" = "$NEW_VER" ]; then
    CURRENT_SHA=$(grep -E "^# sha256:" "$SPEC_FILE" | head -1 | awk '{print $3}')
    if [ "$CURRENT_SHA" = "$NEW_SHA" ]; then
        echo "Package is already at $NEW_VER. No update needed."
        exit 0
    fi
    echo "Upstream respinned $CURRENT_VERSION (sha256 $CURRENT_SHA -> $NEW_SHA); re-pinning and bumping Release."
    sed -i -E "s|^# sha256:.*|# sha256: $NEW_SHA|" "$SPEC_FILE"
    OLD_REL=$(grep -E "^Release:" "$SPEC_FILE" | awk '{print $2}' | sed 's/%.*//')
    NEW_REL=$((OLD_REL + 1))
    sed -i -E "s|^Release:.*|Release:        ${NEW_REL}%{?dist}|" "$SPEC_FILE"
    DATE=$(LC_ALL=C date +"%a %b %d %Y")
    sed -i '/^%changelog/,$d' "$SPEC_FILE"
    {
        echo "%changelog"
        echo "* $DATE $PACKAGER - $NEW_VER-$NEW_REL"
        echo "- Re-pin .deb (upstream respinned the tag)"
    } >> "$SPEC_FILE"
    if ! grep -q "^Name:" "$SPEC_FILE"; then
        echo "FATAL: $SPEC_FILE lost its Name: header; restoring" >&2
        git checkout -- "$SPEC_FILE" 2>/dev/null || true
        exit 1
    fi
    exit 0
fi

echo "Update found: $CURRENT_VERSION -> $NEW_VER"

sed -i -E "s/^Version:.*/Version:        $NEW_VER/" "$SPEC_FILE"
sed -i -E "s|^Source0:.*|Source0:        $DEB_URL|" "$SPEC_FILE"
sed -i -E "s|^# sha256:.*|# sha256: $NEW_SHA|" "$SPEC_FILE"

DATE=$(LC_ALL=C date +"%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - $NEW_VER-0"
    echo "- Update to upstream release $NEW_VER"
} >> "$SPEC_FILE"

echo "Successfully patched $SPEC_FILE."

if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
