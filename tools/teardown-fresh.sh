#!/bin/bash
# teardown-fresh.sh <pkgdir> [chroot] [smoke-cmd] [rpm-name]
# Build in one container, install + smoke in a second fresh container.
# Local package files must reach SOURCES - spectool fetches URLs only.
# Bash reads this script incrementally - never edit while jobs run.
# Unescaped quotes in the smoke payload truncate the container script.
set -u
PKG=$1
CH=${2:-44}
SMOKE=${3:-}
RPMN=${4:-$PKG}
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SPEC=$(basename "$(ls "$R/$PKG"/*.spec 2>/dev/null | head -1)")
OUTDIR=/tmp/teardown/$PKG
mkdir -p "$OUTDIR"
rm -f "$OUTDIR"/*.rpm "$OUTDIR"/build.log "$OUTDIR"/install.log
[ -z "$SPEC" ] && { echo "TEARDOWN_$PKG=FAIL no-spec"; exit 2; }

build=$(docker run --rm -v "$R:/srv:ro" -v "$OUTDIR:/out" "registry.fedoraproject.org/fedora:$CH" bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core rpm-build rpmdevtools >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
cd /tmp && rm -rf w && cp -r /srv/$PKG ./w && cd w
for bpass in 1 2; do dnf -y --setopt=gpgcheck=0 builddep $SPEC > /tmp/bd.log 2>&1; brc=\$?; [ \$brc -eq 0 ] && break; sleep 5; done
echo BUILDEP_EXIT=\$brc
mkdir -p /root/rpmbuild/{SOURCES,BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
for sp in 1 2 3; do spectool -g -C /root/rpmbuild/SOURCES $SPEC > /tmp/sp.log 2>&1 && break; sleep 5; done
tail -1 /tmp/sp.log
find . -maxdepth 1 -type f -exec cp -f {} /root/rpmbuild/SOURCES/ \;
for pass in 1 2 3; do
  rpmbuild -bb --define '_topdir /root/rpmbuild' $SPEC > /tmp/bb.log 2>&1; rc=\$?
  [ \$rc -eq 0 ] && break
  grep -q '^error: Failed build dependencies:' /tmp/bb.log || break
  nosrc=\$(ls -t /root/rpmbuild/SRPMS/*.buildreqs.nosrc.rpm 2>/dev/null | head -1)
  [ \${#nosrc} -eq 0 ] && break
  echo DYNAMIC_BUILDDEPS: \$nosrc
  dnf -y --setopt=gpgcheck=0 builddep \$nosrc >> /tmp/bb.log 2>&1 || break
done
echo RPMBUILD_EXIT=\$rc
[ \$rc -ne 0 ] && grep -aiE 'error|Error' /tmp/bb.log | tail -5 | sed 's/^/BUILD_ERROR: /'
cp /tmp/bb.log /out/build.log
cp /root/rpmbuild/RPMS/*/*.rpm /out/ 2>/dev/null
echo BUILT=\$(ls /out/*.rpm 2>/dev/null | wc -l)
" 2>&1)
printf '%s\n' "$build"

if ! grep -q 'RPMBUILD_EXIT=0' <<< "$build" || ! ls "$OUTDIR"/*.rpm >/dev/null 2>&1; then
  echo "TEARDOWN_$PKG=FAIL rpmbuild"
  exit 3
fi

inst=$(docker run --rm -v "$OUTDIR:/rpms:ro" "registry.fedoraproject.org/fedora:$CH" bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
echo '--- install ---'
dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install /rpms/*.rpm 2>&1 | tail -2
echo INSTALL_EXIT=\${PIPESTATUS[0]}
rpm -V $RPMN && echo RPMV_OK
echo '--- smoke ---'
( $SMOKE ); echo SMOKE_EXIT=\$?
" 2>&1)
printf '%s\n' "$inst"

iok=FAIL; grep -q 'INSTALL_EXIT=0' <<< "$inst" && grep -q 'RPMV_OK' <<< "$inst" && iok=PASS
sok=FAIL
if [ -z "$SMOKE" ]; then
  # Files-only or library package: no runnable entry point was requested.
  grep -q 'RPMV_OK' <<< "$inst" && sok=SKIP-files-only
elif grep -q 'SMOKE_EXIT=0' <<< "$inst"; then
  sok=PASS
fi
printf '%s\n' "$inst" > "$OUTDIR/install.log"
echo "TEARDOWN_$PKG=chroot:$CH rpmbuild-bb $(grep -q 'RPMBUILD_EXIT=0' <<< "$build" && echo PASS || echo FAIL) install $iok smoke $sok"
[ "$iok" = PASS ] && [ "$sok" != FAIL ] && exit 0
exit 4
