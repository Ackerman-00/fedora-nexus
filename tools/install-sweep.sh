#!/bin/bash
# install-sweep.sh <list> [jobs] [chroot]
# List lines: pkg|dnf-name|smoke-cmd
# One fresh container per line: enable the live COPR repo, install, rpm -V,
# ldd the entry points, then the smoke when one is given (empty = files-only).
# A row is PASS only when install, rpm -V, ldd and the smoke all agree.
set -u
LIST=${1:?usage: install-sweep.sh <list> [jobs] [chroot]}
JOBS=${2:-4}
CH=${3:-44}
OUT=${IS_OUTDIR:-/tmp/install-sweep}
DATE=$(date -u +%F)
mkdir -p "$OUT"
: > "$OUT/rows.txt"

one() {
  IFS='|' read -r pkg dnf smoke <<< "$1"
  [ -n "$pkg" ] || return 0
  local out="$OUT/$pkg.log"
  docker run --rm -i -e PKG="$pkg" -e DNFN="$dnf" -e SMOKE="$smoke" \
    "registry.fedoraproject.org/fedora:$CH" bash -s >"$out" 2>&1 <<'EOS'
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
echo '--- install ---'
dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install "$DNFN" 2>&1 | tail -3
echo INSTALL_EXIT=${PIPESTATUS[0]}
name=$DNFN
rpm -q "$name" >/dev/null 2>&1 || name=$(rpm -q --whatprovides "$DNFN" 2>/dev/null | head -1)
rpm -q "$name" >/dev/null 2>&1 || name=$PKG
echo NVR=$(rpm -q --qf '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}' "$name" 2>/dev/null)
rpm -V "$name" >/tmp/v.log 2>&1 && echo RPMV_OK || { echo RPMV_DIRTY; head -3 /tmp/v.log; }
echo '--- ldd ---'
# Entry points only: a bundled payload lib is dlopen'd by the app, so the
# smoke owns that closure. /opt bundles resolve against their own lib dir.
files=$(rpm -ql "$name" 2>/dev/null)
optlib=$(printf '%s\n' "$files" | grep -oE '^/opt/[^/]+/lib' | sort -u | paste -sd:)
shipped=$(printf '%s\n' "$files" | awk -F/ '{print $NF}' | sort -u)
targets=$(printf '%s\n' "$files" | grep -E '^/usr/(bin|libexec)/')
[ -z "$targets" ] && targets=$(printf '%s\n' "$files" | grep -E '^/usr/lib64/[^/]+\.so')
miss=0
for f in $targets; do
  [ -f "$f" ] || continue
  head -c4 "$f" 2>/dev/null | grep -q ELF || continue
  for soname in $(LD_LIBRARY_PATH="$optlib" ldd "$f" 2>/dev/null | awk '/not found/{print $1}'); do
    printf '%s\n' "$shipped" | grep -qx "$soname" && continue
    echo LDD_MISSING "$f" "$soname"; miss=$((miss+1))
  done
done
echo LDD_MISSING_COUNT=$miss
echo '--- smoke ---'
if [ -n "$SMOKE" ]; then bash -c "$SMOKE"; else true; fi
echo SMOKE_EXIT=$?
EOS
  local nvr iex rv lddc sex
  nvr=$(grep -m1 '^NVR=' "$out" | cut -d= -f2-)
  iex=$(grep -m1 '^INSTALL_EXIT=' "$out" | cut -d= -f2)
  rv=$(grep -c 'RPMV_OK' "$out")
  lddc=$(grep -m1 '^LDD_MISSING_COUNT=' "$out" | cut -d= -f2)
  sex=$(grep -m1 '^SMOKE_EXIT=' "$out" | cut -d= -f2)
  local verdict=PASS why=""
  [ "$iex" = "0" ] || { verdict=FAIL; why="install rc=$iex"; }
  [ "$rv" = "1" ] || { verdict=FAIL; why="$why rpm -V dirty"; }
  [ "${lddc:-0}" = "0" ] || { verdict=FAIL; why="$why ldd missing=$lddc"; }
  [ "$sex" = "0" ] || { verdict=FAIL; why="$why smoke rc=$sex"; }
  printf '%s|%s|%s|%s|%s|%s\n' "$pkg" "$CH" "$nvr" "${smoke:-files-only}" "$verdict" "$why" >> "$OUT/rows.txt"
  echo "ROW $pkg $CH ${nvr:-?} $verdict $why"
}
export -f one
export OUT CH

tr '\n' '\0' < "$LIST" | xargs -0 -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
echo "date: $DATE"
echo "rows: $OUT/rows.txt"
sort "$OUT/rows.txt"
