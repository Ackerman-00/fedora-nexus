#!/bin/bash
# fresh-container install + rpm -V + probes.txt smoke for an already built RPM
set -u
PKG=$1
CH=${2:-44}
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT=/tmp/teardown/$PKG
SMOKE=$(awk -F'|' -v p="$PKG" '$1==p{print $3}' "$R/tools/probes.txt")
[ "$SMOKE" = "files-only" ] && SMOKE=""
ls "$OUT"/*.rpm >/dev/null 2>&1 || { echo "SMOKE_$PKG=NO_RPM"; exit 2; }
printf '%s\n' "$SMOKE" > "$OUT/smoke.sh"
SECOPT=""; EXTRAPKG=""
if grep -q 'chrome-sandbox' "$R/$PKG"/*.spec 2>/dev/null; then
  SECOPT="--security-opt seccomp=unconfined"
  EXTRAPKG="util-linux xorg-x11-server-Xvfb"
  SMOKE_RUN="useradd -m t; su t -c 'timeout 60 xvfb-run -a bash /rpms/smoke.sh' > /tmp/smoke.log 2>&1; s=\$?; tail -5 /tmp/smoke.log; echo SMOKE_EXIT=\$s; echo SANDBOX_FATAL=\$(grep -c setuid_sandbox_host /tmp/smoke.log)"
else
  SMOKE_RUN="bash /rpms/smoke.sh; echo SMOKE_EXIT=\$?"
fi
[ -z "$SMOKE" ] && SMOKE_RUN="echo SMOKE_EXIT=0"
inst=$(docker run --rm $SECOPT -v "$OUT:/rpms:ro" "registry.fedoraproject.org/fedora:$CH" bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core $EXTRAPKG >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
echo '--- install ---'
dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install /rpms/*.rpm 2>&1 | tail -2
echo INSTALL_EXIT=\${PIPESTATUS[0]}
rpm -V $PKG && echo RPMV_OK
echo '--- smoke ---'
$SMOKE_RUN
" 2>&1)
printf '%s\n' "$inst" > "$OUT/smoke-install.log"
iok=FAIL; grep -q 'INSTALL_EXIT=0' <<< "$inst" && grep -q 'RPMV_OK' <<< "$inst" && iok=PASS
sok=FAIL
if [ -z "$SMOKE" ]; then
  grep -q 'RPMV_OK' <<< "$inst" && sok=SKIP-files-only
elif [ -n "$SECOPT" ]; then
  grep -qE 'SMOKE_EXIT=(0|124)$' <<< "$inst" && grep -q 'SANDBOX_FATAL=0' <<< "$inst" && sok=PASS
elif grep -qE 'SMOKE_EXIT=(0|124)$' <<< "$inst"; then
  sok=PASS
fi
echo "SMOKE_$PKG=$CH install $iok smoke $sok"
[ "$iok" = PASS ] && [ "$sok" != FAIL ] && exit 0
exit 4
