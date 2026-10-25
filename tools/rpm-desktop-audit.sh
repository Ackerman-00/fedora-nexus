#!/bin/bash
# rpm-desktop-audit.sh <rpm> [chroot]
# Installs one built RPM in a fresh container and checks that every shipped
# .desktop entry resolves: Icon= has a matching icon file, Exec= has a binary.
# Report-only per entry; exit 1 when any entry is unresolved.
set -u
RPM=${1:?usage: rpm-desktop-audit.sh <rpm> [chroot]}
CH=${2:-44}
DIR=$(cd "$(dirname "$RPM")" && pwd)
FILE=$(basename "$RPM")
docker run --rm -e FILE="$FILE" -v "$DIR:/rpms:ro" "registry.fedoraproject.org/fedora:$CH" bash -lc '
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 install "/rpms/$FILE" >/tmp/i.log 2>&1 || {
  echo "INSTALL_FAIL: $(tail -2 /tmp/i.log | tr "\n" " ")"
  exit 2
}
name=$(rpm -qp --qf "%{NAME}" "/rpms/$FILE")
rc=0
found=0
for d in $(rpm -ql "$name" | grep "\.desktop$"); do
  found=$((found+1))
  icon=$(sed -n "s/^Icon=//p" "$d" | head -1)
  if [ -n "$icon" ]; then
    hit=$(find /usr/share/icons /usr/share/pixmaps -name "$icon.*" -print -quit 2>/dev/null)
    if [ -n "$hit" ]; then
      echo "ICON_OK: $d Icon=$icon -> $hit"
    else
      echo "ICON_MISSING: $d Icon=$icon (no icon file shipped or installed)"
      rc=1
    fi
  fi
  exe=$(sed -n "s/^Exec=//p" "$d" | head -1 | awk "{print \$1}")
  case "$exe" in
    /*) [ -x "$exe" ] || { echo "EXEC_MISSING: $d Exec=$exe"; rc=1; } ;;
    "") : ;;
  esac
done
echo "DESKTOP_ENTRIES=$found"
exit $rc'
