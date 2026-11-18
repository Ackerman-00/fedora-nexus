#!/bin/bash
_update_sh_dir=$(cd "$(dirname "$0")" && pwd) || exit 1
if [ "$(pwd)" != "$_update_sh_dir" ]; then
    echo "FATAL: run update.sh from its package directory:" >&2
    echo "  cd $_update_sh_dir && bash update.sh" >&2
    exit 1
fi

SPEC_FILE="zoolander-settings-git.spec"
API="https://git.pika-os.com/api/v1/repos/otter-shell"
PACKAGER="Ackerman-00 <no-reply>"
MACROS=(zsver geo utils conf render wayland theme ui desktop)
REPOS=(zoolander-settings otter-geo otter-utils otter-conf otter-render otter-wayland otter-theme otter-ui otter-desktop)
TMP=$(mktemp -d) || exit 1
trap 'rm -rf "$TMP"' EXIT

pin_for() {
    python3 - "$SPEC_FILE" "$1" "$2" <<'PYEOF'
import sys
path, repo, sha = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(path).read()
needle = f"/otter-shell/{repo}/archive/"
idx = s.index(needle)
line_end = s.index("\n", idx) + 1
rest = s[line_end:]
if rest.startswith("# sha256:"):
    nl = rest.index("\n") + 1
    rest = f"# sha256: {sha}\n" + rest[nl:]
else:
    rest = f"# sha256: {sha}\n" + rest
open(path, "w").write(s[:line_end] + rest)
PYEOF
}

latest_tag() {
    curl -sSfL --retry 3 --connect-timeout 30 "$API/$1/tags?limit=20" \
        | python3 -c 'import json,re,sys
tags=[t["name"] for t in json.load(sys.stdin)]
sem=[t for t in tags if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
sem.sort(key=lambda t: tuple(int(x) for x in t[1:].split(".")))
print(sem[-1] if sem else "")'
}

changed=0
new=()
for i in "${!REPOS[@]}"; do
    tag=$(latest_tag "${REPOS[$i]}")
    if [ -z "$tag" ]; then
        echo "FATAL: no version tag for ${REPOS[$i]}" >&2
        exit 1
    fi
    ver=${tag#v}
    new+=("$ver")
    cur=$(grep -E "^%global ${MACROS[$i]} " "$SPEC_FILE" | awk '{print $3}')
    [ "$cur" = "$ver" ] || changed=1
    echo "${MACROS[$i]}: ${cur} -> ${ver}"
done

if [ "$changed" -eq 0 ]; then
    echo "Already at the newest tags of all nine Otter sources."
    exit 0
fi

sha=()
for i in "${!REPOS[@]}"; do
    url="$API/${REPOS[$i]}/archive/v${new[$i]}.tar.gz"
    if ! curl -sSfL --retry 3 --connect-timeout 30 "$url" -o "$TMP/$i.tar.gz"; then
        echo "FATAL: download failed: $url" >&2
        exit 1
    fi
    tar -tzf "$TMP/$i.tar.gz" > /dev/null || { echo "FATAL: corrupt archive $url" >&2; exit 1; }
    sha+=("$(sha256sum "$TMP/$i.tar.gz" | awk '{print $1}')")
done

for i in "${!MACROS[@]}"; do
    sed -i -E "s/^%global ${MACROS[$i]} +.*/$(printf '%%global %-9s' "${MACROS[$i]}")${new[$i]}/" "$SPEC_FILE"
done

for i in "${!REPOS[@]}"; do
    pin_for "${REPOS[$i]}" "${sha[$i]}"
done

sed -i -E "s/^Release: .*/Release:        1%{?dist}/" "$SPEC_FILE"
DATE=$(date -u "+%a %b %d %Y")
sed -i '/^%changelog/,$d' "$SPEC_FILE"
{
    echo "%changelog"
    echo "* $DATE $PACKAGER - ${new[0]}-1"
    echo "- Update the Otter sources to their newest tags (settings ${new[0]},"
    echo "  geo ${new[1]}, utils ${new[2]}, conf ${new[3]}, render ${new[4]},"
    echo "  wayland ${new[5]}, theme ${new[6]}, ui ${new[7]}, desktop ${new[8]};"
    echo "  sha256 of every archive verified)"
} >> "$SPEC_FILE"

if ! grep -q "^Name:" "$SPEC_FILE"; then
    echo "FATAL: $SPEC_FILE lost its Name: header during update; restoring" >&2
    git checkout -- "$SPEC_FILE" 2>/dev/null || true
    exit 1
fi
echo "Updated zoolander-settings-git to ${new[0]}"
