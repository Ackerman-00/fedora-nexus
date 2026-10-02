#!/bin/bash
# container-teardown.sh - fresh-container rpmbuild + install + smoke harness
# (repo-persistent version of the autonomous-run teardown; see .opencode-relay.md
# run 36984729835 for the three harness bugs this fixes).
#
# Lessons encoded here (do NOT regress):
#  1. Copy ALL repo-local files into SOURCES (Patch/Source1+ desktop files,
#     icons, metainfo - e.g. stoat .desktop/.png, ly/wlroots .patch). COPR
#     builds from a full SCM checkout; spectool -g alone only fetches URLs.
#  2. Glob built RPMs across RPMS/* (noarch packages like waypaper land in
#     RPMS/noarch, not RPMS/x86_64).
#  3. Never `set -e` around, never edit this file while jobs run (bash reads
#     the script incrementally; a mid-run edit corrupts running jobs).
#
# usage: container-teardown.sh <pkgdir> <spec> <smoke-cmd> [rpmV-name]
set -u
PKGDIR=$1; SPEC=$2; SMOKE=$3; RPMVNAME=${4:-}
R=${R:-$PWD}
docker run --rm -v "$R:/srv:ro" registry.fedoraproject.org/fedora:44 bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core rpm-build rpmdevtools >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
cd /tmp && rm -rf w && cp -r /srv/$PKGDIR ./w && cd w
echo '--- builddep ---'; dnf -y --setopt=gpgcheck=0 builddep $SPEC 2>&1 | tail -1
mkdir -p /root/rpmbuild/{SOURCES,BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
echo '--- spectool ---'; spectool -g -C /root/rpmbuild/SOURCES $SPEC 2>&1 | tail -1
find . -maxdepth 1 -type f -exec cp -f {} /root/rpmbuild/SOURCES/ \;
echo '--- rpmbuild ---'; rpmbuild -bb --define '_topdir /root/rpmbuild' $SPEC > /tmp/bb.log 2>&1; echo RPMBUILD_EXIT=\$?; tail -2 /tmp/bb.log
RPM=\$(ls /root/rpmbuild/RPMS/*/*.rpm 2>/dev/null | head -1); echo BUILT=\$RPM
echo '--- install ---'; dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install \$RPM 2>&1 | tail -1
if [ -n '$RPMVNAME' ]; then rpm -V $RPMVNAME && echo RPMV_OK; fi
echo '--- smoke ---'; $SMOKE; echo SMOKE_EXIT=\$?
" 2>&1 | grep -aE -- '---|RPMBUILD_EXIT|BUILT=|RPMV_OK|SMOKE_EXIT|Complete!|Error' | head -20
