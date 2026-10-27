#!/bin/bash
set -u
PKG=$1; PAT=$2; SMOKE=$3; CHROOT=${4:-44}
docker run --rm registry.fedoraproject.org/fedora:$CHROOT bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
echo '--- install ---'; dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install $PKG 2>&1 | tail -1
echo INSTALLED_NVR=\$(rpm -q --qf '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}' $PAT 2>/dev/null)
rpm -q $PAT >/dev/null 2>&1 && echo INSTALLED_OK
rpm -V $PKG && echo RPMV_OK
echo '--- smoke ---'; $SMOKE; echo SMOKE_EXIT=\$?
" 2>&1 | grep -aE -- '---|INSTALLED_NVR|INSTALLED_OK|RPMV_OK|SMOKE_EXIT|Complete!|Error' | head -12
