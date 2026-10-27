#!/bin/bash
set -u
PKGDIR=$1; SPEC=$2; SMOKE=$3; RPMVNAME=${4:-}
R=${R:-$PWD}
OUT=$(docker run --rm -v "$R:/srv:ro" registry.fedoraproject.org/fedora:44 bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core rpm-build rpmdevtools >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
cd /tmp && rm -rf w && cp -r /srv/$PKGDIR ./w && cd w
echo '--- builddep ---'
for bpass in 1 2; do
  dnf -y --setopt=gpgcheck=0 builddep $SPEC > /tmp/bd.log 2>&1
  brc=\$?
  [ \$brc -eq 0 ] && break
  echo BUILDEP_RETRY after failure:; tail -3 /tmp/bd.log
  sleep 10
done
echo BUILDEP_EXIT=\$brc; tail -1 /tmp/bd.log
mkdir -p /root/rpmbuild/{SOURCES,BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
echo '--- spectool ---'
for sp in 1 2 3; do
  spectool -g -C /root/rpmbuild/SOURCES $SPEC > /tmp/sp.log 2>&1 && break
  echo SPECTOOL_RETRY pass \$sp:; tail -2 /tmp/sp.log; sleep 5
done
tail -1 /tmp/sp.log
find . -maxdepth 1 -type f -exec cp -f {} /root/rpmbuild/SOURCES/ \;
echo SPECTOOL_FILES=\$(ls /root/rpmbuild/SOURCES | wc -l)
echo '--- rpmbuild ---'
for pass in 1 2 3; do
  rpmbuild -bb --define '_topdir /root/rpmbuild' $SPEC > /tmp/bb.log 2>&1
  rc=\$?
  [ \$rc -eq 0 ] && break
  grep -q '^error: Failed build dependencies:' /tmp/bb.log || break
  nosrc=\$(ls -t /root/rpmbuild/SRPMS/*.buildreqs.nosrc.rpm 2>/dev/null | head -1)
  [ \${#nosrc} -eq 0 ] && break
  echo DYNAMIC_BUILDDEPS: \$nosrc
  dnf -y --setopt=gpgcheck=0 builddep \$nosrc >> /tmp/bb.log 2>&1 || break
done
echo RPMBUILD_EXIT=\$rc; tail -2 /tmp/bb.log
if [ \$rc -ne 0 ]; then grep -ai error /tmp/bb.log | tail -5 | sed 's/^/BUILD_ERROR: /'; fi
if [ \$brc -ne 0 ]; then echo WARNING_BUILDEP_UNRESOLVED rc=\$brc - a later is-needed-by failure is a dependency-resolution artifact, not proof of a broken spec; fi
RPM=\$(ls /root/rpmbuild/RPMS/*/*.rpm 2>/dev/null | head -1); echo BUILT=\$RPM
echo '--- install ---'; dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install \$RPM 2>&1 | tail -1; echo INSTALL_EXIT=\${PIPESTATUS[0]}
if [ -n '$RPMVNAME' ]; then rpm -V $RPMVNAME && echo RPMV_OK; fi
echo '--- smoke ---'; ( $SMOKE ); echo SMOKE_EXIT=\$?
" 2>&1 | grep -aE -- '---|RPMBUILD_EXIT|INSTALL_EXIT|BUILDEP_EXIT|BUILDEP_RETRY|WARNING_BUILDEP_UNRESOLVED|BUILT=|RPMV_OK|SMOKE_EXIT|DYNAMIC_BUILDDEPS|SPECTOOL_RETRY|SPECTOOL_FILES|BUILD_ERROR|Complete!|Error|SMOKE_OK|ELF_OK|WRAPPER_OK|not_found=|help_rc=|version_file=' | head -140)
printf '%s\n' "$OUT"

case "$OUT" in
  *SMOKE_EXIT=*) ;;
  *) echo "HARNESS_TRUNCATED: no SMOKE_EXIT marker in the output above; the container payload was cut short (check for an unescaped quote in this script)" ;;
esac
