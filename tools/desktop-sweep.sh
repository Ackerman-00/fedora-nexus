#!/bin/bash
# Install published packages in a clean container and resolve every .desktop they ship:
# menu entries (XDG dirs) must resolve Icon= and Exec=; a bundle copy under /opt only
# needs its Exec binary inside the payload; a session entry needs its Exec in PATH.
# usage: desktop-sweep.sh "<pkg> <pkg> ..." [chroot]
set -u
PKGS=${1:?usage: desktop-sweep.sh "<pkg> <pkg> ..." [chroot]}
CH=${2:-45}
docker run --rm -i -e PKGS="$PKGS" "registry.fedoraproject.org/fedora:$CH" bash -s <<'EOS'
set -u
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
for p in $PKGS; do
  dnf -y -q --setopt=gpgcheck=0 install "$p" >/tmp/i.log 2>&1 || echo "INSTALL_FAIL $p"
done
# icon names the loader can see, symlinks included (a bundled icon is often a symlink)
: > /tmp/icons
find /usr/share/icons -type f -o -type l 2>/dev/null | sed -n 's#.*/\([^/]*\)\.\(png\|svg\|xpm\)$#\1#p' >> /tmp/icons
sort -u /tmp/icons -o /tmp/icons
rc=0; menu=0; bundle=0; session=0
for p in $PKGS; do
  rpm -q "$p" >/dev/null 2>&1 || continue
  for f in $(rpm -ql "$p" 2>/dev/null | grep '\.desktop$'); do
    [ -e "$f" ] || { echo "DESKTOP_MISSING $p $f"; rc=1; continue; }
    icon=$(sed -n 's/^Icon=//p' "$f" | head -1)
    exec_line=$(sed -n 's/^Exec=//p' "$f" | head -1)
    exec_bin=${exec_line%% *}
    case "$f" in
      /usr/share/applications/*.desktop)
        menu=$((menu+1))
        case "$icon" in
          "") echo "MENU_ICON_UNSET $p $(basename "$f")" ;;
          /*) [ -e "$icon" ] || { echo "MENU_ICON_MISSING $p $(basename "$f") icon=$icon"; rc=1; } ;;
          *) grep -qxF "$icon" /tmp/icons || { echo "MENU_ICON_MISSING $p $(basename "$f") icon=$icon"; rc=1; } ;;
        esac
        case "$exec_bin" in
          "") : ;;
          /*) [ -x "$exec_bin" ] || { echo "MENU_EXEC_MISSING $p $(basename "$f") exec=$exec_bin"; rc=1; } ;;
          *) command -v "$exec_bin" >/dev/null 2>&1 || { echo "MENU_EXEC_MISSING $p $(basename "$f") exec=$exec_bin"; rc=1; } ;;
        esac
        echo "MENU $p $(basename "$f") icon=${icon:--} exec=${exec_bin:--}" ;;
      /usr/share/wayland-sessions/*.desktop|/usr/share/xsessions/*.desktop)
        session=$((session+1))
        case "$exec_bin" in
          "") : ;;
          /*) [ -x "$exec_bin" ] || { echo "SESSION_EXEC_MISSING $p $(basename "$f") exec=$exec_bin"; rc=1; } ;;
          *) command -v "$exec_bin" >/dev/null 2>&1 || { echo "SESSION_EXEC_MISSING $p $(basename "$f") exec=$exec_bin"; rc=1; } ;;
        esac
        echo "SESSION $p $(basename "$f") exec=${exec_bin:--}" ;;
      *)
        bundle=$((bundle+1))
        case "$exec_bin" in
          "") : ;;
          /*) [ -x "$exec_bin" ] || { echo "BUNDLE_EXEC_MISSING $p $f exec=$exec_bin"; rc=1; } ;;
          *) find /opt -maxdepth 4 -name "$exec_bin" -type f -perm -u+x 2>/dev/null | grep -q . \
               || { echo "BUNDLE_EXEC_MISSING $p $f exec=$exec_bin"; rc=1; } ;;
        esac
        echo "BUNDLE $p $(basename "$f") exec=${exec_bin:--}" ;;
    esac
  done
done
echo "MENU_ENTRIES=$menu SESSION_ENTRIES=$session BUNDLE_FILES=$bundle ICON_NAMES=$(grep -c . /tmp/icons)"
echo "AUDIT_EXIT=$rc"
EOS
