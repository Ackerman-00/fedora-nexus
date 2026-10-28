#!/bin/bash
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
menu=0
for d in $(rpm -ql "$name" | grep "\.desktop$"); do
  found=$((found+1))
  icon=$(sed -n "s/^Icon=//p" "$d" | head -1)
  exe=$(sed -n "s/^Exec=//p" "$d" | head -1 | awk "{print \$1}")
  case "$d" in
    /usr/share/applications/*|/usr/local/share/applications/*|/usr/share/wayland-sessions/*|/usr/share/xsessions/*|/etc/xdg/autostart/*) ;;
    *)
      # bundle metadata: no XDG lookup, the bundle launcher supplies the PATH
      b=$(dirname "$d")
      case "$exe" in
        /*) if [ -x "$exe" ]; then echo "BUNDLE_EXEC_OK: $d Exec=$exe"
            else echo "BUNDLE_EXEC_MISSING: $d Exec=$exe"; rc=1; fi ;;
        "") : ;;
        *) hit=""
           for c in "$b/$exe" "$b/bin/$exe" "$b/usr/bin/$exe"; do
             [ -x "$c" ] && { hit="$c"; break; }
           done
           if [ -n "$hit" ]; then echo "BUNDLE_EXEC_OK: $d Exec=$exe -> $hit"
           else echo "BUNDLE_EXEC_MISSING: $d Exec=$exe (not in $b, bin or usr/bin)"; rc=1; fi ;;
      esac
      echo "BUNDLE_META: $d (not an XDG entry, not rendered in a menu)"
      continue ;;
  esac
  menu=$((menu+1))
  if [ -n "$icon" ]; then
    hit=$(find /usr/share/icons /usr/share/pixmaps -name "$icon.*" -print -quit 2>/dev/null)
    if [ -n "$hit" ]; then
      echo "ICON_OK: $d Icon=$icon -> $hit"
    else
      echo "ICON_MISSING: $d Icon=$icon (no icon file shipped or installed)"
      rc=1
    fi
  fi
  case "$exe" in
    /*) if [ -x "$exe" ]; then
          echo "EXEC_OK: $d Exec=$exe"
          if head -1 "$exe" 2>/dev/null | grep -q '^#!'; then
            for t in $(sed -n 's/^exec \([^ ]*\).*/\1/p' "$exe" 2>/dev/null); do
              case "$t" in
                /*) if [ -e "$t" ]; then echo "WRAPPER_TARGET_OK: $exe -> $t"
                    else echo "WRAPPER_TARGET_MISSING: $exe -> $t"; rc=1; fi ;;
              esac
            done
          fi
        else echo "EXEC_MISSING: $d Exec=$exe"; rc=1; fi ;;
    "") : ;;
    *) if command -v "$exe" >/dev/null 2>&1; then echo "EXEC_OK: $d Exec=$exe -> $(command -v "$exe")"
       else echo "EXEC_MISSING: $d Exec=$exe (not in PATH)"; rc=1; fi ;;
  esac
done
echo "DESKTOP_ENTRIES=$found MENU_ENTRIES=$menu"
exit $rc'
