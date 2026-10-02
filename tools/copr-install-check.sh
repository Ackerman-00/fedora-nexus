#!/bin/bash
# copr-install-check.sh - install the COPR-published RPM (what users get) in a
# fresh container + smoke test. For prebuilt-browser packages that cannot run
# plain `--version` headless/as-root, use these proven smoke commands:
#   helium-browser:       /opt/helium/helium --no-sandbox --headless --disable-gpu --version
#   zen-browser:          MOZ_HEADLESS=1 /opt/zen/zen --version
#   heroic-games-launcher: ls /opt/Heroic/resources/app.asar   (note capital H)
#
# usage: copr-install-check.sh <pkg> <rpm-name> <smoke-cmd> [chroot-number]
# The chroot argument rotates the install test onto a secondary Fedora release
# (e.g. 45, 43, or "rawhide"); it defaults to 44. Hardcoding one release hid
# secondary-chroot regressions, so the release is a parameter now.
set -u
PKG=$1; PAT=$2; SMOKE=$3; CHROOT=${4:-44}
docker run --rm registry.fedoraproject.org/fedora:$CHROOT bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
echo '--- install ---'; dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install $PKG 2>&1 | tail -1
rpm -q $PAT && echo INSTALLED_OK
rpm -V $PKG && echo RPMV_OK
echo '--- smoke ---'; $SMOKE; echo SMOKE_EXIT=\$?
" 2>&1 | grep -aE -- '---|INSTALLED_OK|RPMV_OK|SMOKE_EXIT|Complete!|Error' | head -12
