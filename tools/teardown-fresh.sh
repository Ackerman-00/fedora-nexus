#!/bin/bash
# teardown-fresh.sh <pkgdir> [chroot] [smoke-cmd] [rpm-name]
# Build in one container, install + smoke in a second fresh container.
# Local package files must reach SOURCES - spectool fetches URLs only.
# Bash reads this script incrementally - never edit while jobs run.
# The smoke payload travels as a mounted file, so quotes survive verbatim.
# Electron payloads (chrome-sandbox in %files) get the AGENTS.md launch test:
# seccomp=unconfined, non-root user, xvfb, rc 0 or 124, no setuid_sandbox_host.
set -u
PKG=$1
CH=${2:-44}
SMOKE=${3:-}
# probes.txt marks a row with no smoke probe as files-only
[ "$SMOKE" = "files-only" ] && SMOKE=""
RPMN=${4:-$PKG}
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SPEC=$(basename "$(ls "$R/$PKG"/*.spec 2>/dev/null | head -1)")
ELECTRON=0
grep -q 'chrome-sandbox' "$R/$PKG/$SPEC" 2>/dev/null && ELECTRON=1
OUTDIR=/tmp/teardown/$PKG
mkdir -p "$OUTDIR"
rm -f "$OUTDIR"/*.rpm "$OUTDIR"/build.log "$OUTDIR"/install.log
[ -z "$SPEC" ] && { echo "TEARDOWN_$PKG=FAIL no-spec"; exit 2; }

build=$(docker run --rm -v "$R:/srv:ro" -v "$OUTDIR:/out" "registry.fedoraproject.org/fedora:$CH" bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core rpm-build rpmdevtools >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
cd /tmp && rm -rf w && cp -r /srv/$PKG ./w && cd w
for bpass in 1 2 3; do dnf -y --setopt=gpgcheck=0 builddep $SPEC > /tmp/bd.log 2>&1; brc=\$?; [ \$brc -eq 0 ] && break; sleep 10; done
echo BUILDEP_EXIT=\$brc
[ \$brc -ne 0 ] && tail -3 /tmp/bd.log | sed 's/^/BUILDEP_ERROR: /'
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
  # A builddep failure is the repo, not the spec: say which one it was.
  if grep -q 'BUILDEP_EXIT=0' <<< "$build"; then
    echo "TEARDOWN_$PKG=FAIL rpmbuild"
  else
    echo "TEARDOWN_$PKG=FAIL builddep (dependencies unreachable, treat as repo/mirror)"
  fi
  exit 3
fi

SECOPT=""
EXTRAPKG="util-linux ${TD_EXTRAPKG:-}"
# A missing rpm here is a harness fault, not an install verdict: say so.
if ! compgen -G "$OUTDIR/*.rpm" >/dev/null; then
  echo "HARNESS_ERROR no rpm in $OUTDIR after a passing build: $(ls -A "$OUTDIR" | tr '\n' ' ')"
  echo "TEARDOWN_$PKG=chroot:$CH rpmbuild-bb PASS install FAIL smoke FAIL"
  exit 5
fi
# Payload goes through a file: a nested double quote in $SMOKE used to be
# eaten by the bash -lc layer and ran a truncated command.
printf '%s\n' "$SMOKE" > "$OUTDIR/smoke.sh"
SMOKE_RUN="bash /rpms/smoke.sh; echo SMOKE_EXIT=\$?"
if [ "$ELECTRON" = 1 ]; then
  SECOPT="--security-opt seccomp=unconfined"
  EXTRAPKG="util-linux xorg-x11-server-Xvfb ${TD_EXTRAPKG:-}"
  SMOKE_RUN="useradd -m t; su t -c 'timeout 60 xvfb-run -a bash /rpms/smoke.sh' > /tmp/smoke.log 2>&1; s=\$?; tail -5 /tmp/smoke.log; echo SMOKE_EXIT=\$s; echo SANDBOX_FATAL=\$(grep -c setuid_sandbox_host /tmp/smoke.log)"
fi

inst=$(docker run --rm $SECOPT -v "$OUTDIR:/rpms:ro" "registry.fedoraproject.org/fedora:$CH" bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core $EXTRAPKG >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
echo '--- install ---'
dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install /rpms/*.rpm 2>&1 | tail -2
echo INSTALL_EXIT=\${PIPESTATUS[0]}
rpm -V $RPMN && echo RPMV_OK
echo '--- smoke ---'
$SMOKE_RUN
" 2>&1)
printf '%s\n' "$inst"

iok=FAIL; grep -q 'INSTALL_EXIT=0' <<< "$inst" && grep -q 'RPMV_OK' <<< "$inst" && iok=PASS
sok=FAIL
if [ -z "$SMOKE" ]; then
  # Files-only or library package: no runnable entry point was requested.
  grep -q 'RPMV_OK' <<< "$inst" && sok=SKIP-files-only
elif [ "$ELECTRON" = 1 ]; then
  # rc 124 = still alive after the timeout, the correct keep-running answer.
  grep -qE 'SMOKE_EXIT=(0|124)$' <<< "$inst" && grep -q 'SANDBOX_FATAL=0' <<< "$inst" && sok=PASS
elif grep -qE 'SMOKE_EXIT=(0|124)$' <<< "$inst"; then
  # 124 = the smoke was cut by `timeout`: a GUI that stayed up, not a crash.
  sok=PASS
fi
printf '%s\n' "$inst" > "$OUTDIR/install.log"
echo "TEARDOWN_$PKG=chroot:$CH rpmbuild-bb $(grep -q 'RPMBUILD_EXIT=0' <<< "$build" && echo PASS || echo FAIL) install $iok smoke $sok"
[ "$iok" = PASS ] && [ "$sok" != FAIL ] && exit 0
exit 4
