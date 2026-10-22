#!/bin/bash
# electron-launch.sh <list> [jobs] [chroot]
# List lines: pkg|binary ("auto" picks the first shipped /usr/bin ELF).
# AGENTS.md chrome-sandbox rule: non-root xvfb launch under
# seccomp=unconfined; PASS = rc 0/124 and zero setuid_sandbox_host lines.
set -u
LIST=${1:?usage: electron-launch.sh <list> [jobs] [chroot]}
JOBS=${2:-2}
CH=${3:-44}
OUT=${EL_OUTDIR:-/tmp/electron-launch}
mkdir -p "$OUT"
: > "$OUT/rows.txt"

one() {
  IFS='|' read -r pkg bin <<< "$1"
  case "$pkg" in ''|\#*) return 0 ;; esac
  local log="$OUT/$pkg.log"
  docker run --rm --security-opt seccomp=unconfined -e PKG="$pkg" -e BIN="$bin" \
    "registry.fedoraproject.org/fedora:$CH" bash -lc '
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 install util-linux xorg-x11-server-Xvfb "$PKG" >/dev/null 2>&1
echo INSTALL_EXIT=$?
echo NVR=$(rpm -q --qf "%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}" "$PKG" 2>/dev/null)
if [ "$BIN" = auto ]; then
  BIN=$(rpm -ql "$PKG" | grep -E "^/usr/bin/[^/]+$" | head -1)
  [ -n "$BIN" ] || BIN=$(rpm -ql "$PKG" | grep -E "^/opt/[^/]+/[^/]+$" | grep -vE "\.(so|json|asar|png|svg|pak|bin)$" | head -1)
fi
echo LAUNCH_BIN=$BIN
useradd -m t
chown -R t /home/t
su t -c "timeout 45 xvfb-run -a $BIN" >/tmp/l.log 2>&1
s=$?
echo SMOKE_EXIT=$s
echo SANDBOX_FATAL=$(grep -c setuid_sandbox_host /tmp/l.log)
tail -3 /tmp/l.log
' >"$log" 2>&1
  local nvr iex sex fat verdict
  nvr=$(grep -m1 '^NVR=' "$log" | cut -d= -f2-)
  iex=$(grep -m1 '^INSTALL_EXIT=' "$log" | cut -d= -f2)
  sex=$(grep -m1 '^SMOKE_EXIT=' "$log" | cut -d= -f2)
  fat=$(grep -m1 '^SANDBOX_FATAL=' "$log" | cut -d= -f2)
  verdict=FAIL
  { [ "$iex" = 0 ] && { [ "$sex" = 0 ] || [ "$sex" = 124 ]; } && [ "${fat:-1}" = 0 ]; } && verdict=PASS
  printf '%s|%s|%s|%s|%s|%s\n' "$pkg" "$CH" "${nvr:-?}" "$(grep -m1 '^LAUNCH_BIN=' "$log" | cut -d= -f2-)" "sandbox_fatal=${fat:-?}" "$verdict" >> "$OUT/rows.txt"
  echo "LAUNCH $pkg $CH ${nvr:-?} rc=${sex:-?} sandbox_fatal=${fat:-?} $verdict"
}
export -f one
export OUT CH
tr '\n' '\0' < "$LIST" | xargs -0 -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
sort "$OUT/rows.txt"
