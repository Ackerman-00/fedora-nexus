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
#  4. Print INSTALL_EXIT explicitly. `tail -1` of dnf hides the result when the
#     RPM is already installed (it prints "Nothing to do." instead of
#     "Complete!"), which made an install step look like it produced no output.
#     With INSTALL_EXIT there is no ambiguity; session 5 of run 37006623550 hit
#     exactly this on astal-gjs.
#  5. Retry rpmbuild after "Failed build dependencies" (added 2026-10-04, hit on
#     all five python-* packages in run 37154151210): %generate_buildrequires
#     specs stop the FIRST rpmbuild pass with the dynamic deps it just
#     discovered (e.g. python3dist(setuptools) >= 40.8). mock/COPR install those
#     and retry automatically, so a one-shot local rpmbuild reports a false
#     failure. The loop below runs `dnf builddep` on the generated
#     *.buildreqs.nosrc.rpm (holds the exact dynamic dep set, including
#     versioned and boolean forms a naive parse mangles) and retries, up to
#     3 passes, exactly like mock does.
#
# usage: container-teardown.sh <pkgdir> <spec> <smoke-cmd> [rpmV-name]
set -u
PKGDIR=$1; SPEC=$2; SMOKE=$3; RPMVNAME=${4:-}
R=${R:-$PWD}
OUT=$(docker run --rm -v "$R:/srv:ro" registry.fedoraproject.org/fedora:44 bash -lc "
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core rpm-build rpmdevtools >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
cd /tmp && rm -rf w && cp -r /srv/$PKGDIR ./w && cd w
echo '--- builddep ---'
# A failed builddep used to be invisible: the harness only echoed the last line
# of dnf, so a transient metadata/download error left the BuildRequires
# uninstalled and rpmbuild then failed with \"patchelf is needed by ...\",
# which reads exactly like a broken spec (hit on zen-browser 2026-10-04).
# Print the exit code and retry once, so that class of failure is provably a
# harness/network artifact instead of a packaging bug.
for bpass in 1 2; do
  dnf -y --setopt=gpgcheck=0 builddep $SPEC > /tmp/bd.log 2>&1
  brc=\$?
  [ \$brc -eq 0 ] && break
  echo BUILDEP_RETRY after failure:; tail -3 /tmp/bd.log
  sleep 10
done
echo BUILDEP_EXIT=\$brc; tail -1 /tmp/bd.log
mkdir -p /root/rpmbuild/{SOURCES,BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
echo '--- spectool ---'; spectool -g -C /root/rpmbuild/SOURCES $SPEC 2>&1 | tail -1
find . -maxdepth 1 -type f -exec cp -f {} /root/rpmbuild/SOURCES/ \;
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
# If the static builddep pass never resolved, say so before rpmbuild's
# is-needed-by line is mistaken for a spec bug.
if [ \$brc -ne 0 ]; then echo WARNING_BUILDEP_UNRESOLVED rc=\$brc - a later is-needed-by failure is a dependency-resolution artifact, not proof of a broken spec; fi
RPM=\$(ls /root/rpmbuild/RPMS/*/*.rpm 2>/dev/null | head -1); echo BUILT=\$RPM
echo '--- install ---'; dnf -y --setopt=gpgcheck=0 --setopt=install_weak_deps=False install \$RPM 2>&1 | tail -1; echo INSTALL_EXIT=\${PIPESTATUS[0]}
if [ -n '$RPMVNAME' ]; then rpm -V $RPMVNAME && echo RPMV_OK; fi
echo '--- smoke ---'; ( $SMOKE ); echo SMOKE_EXIT=\$?
" 2>&1 | grep -aE -- '---|RPMBUILD_EXIT|INSTALL_EXIT|BUILDEP_EXIT|BUILDEP_RETRY|WARNING_BUILDEP_UNRESOLVED|BUILT=|RPMV_OK|SMOKE_EXIT|DYNAMIC_BUILDDEPS|Complete!|Error|SMOKE_OK|ELF_OK|WRAPPER_OK|not_found=|help_rc=|version_file=' | head -80)
printf '%s\n' "$OUT"

# 6. The whole container payload lives inside ONE outer double-quoted string, so
#    an unescaped quote in a payload line silently truncates the script the
#    container receives: the run stops at the previous echo and every later
#    marker (INSTALL_EXIT, SMOKE_EXIT) simply goes missing, which reads like a
#    package that "printed nothing". Hit on 2026-10-04 while adding the
#    builddep diagnostics. Guard it loudly instead of guessing afterwards.
# 7. The smoke command runs in a SUBSHELL (line 73). A smoke that starts with
#    `set -e` used to take the whole payload down with it: the first false
#    condition killed the container shell before `echo SMOKE_EXIT=$?` ran, which
#    the guard above reported as "payload truncated" - a true negative wearing a
#    misleading label. The subshell keeps the verdict line printable either way
#    (hit on cliphist 2026-10-04, where `test -f /usr/share/doc/cliphist/version.txt`
#    correctly failed and the marker went missing with it).
case "$OUT" in
  *SMOKE_EXIT=*) ;;
  *) echo "HARNESS_TRUNCATED: no SMOKE_EXIT marker in the output above; the container payload was cut short (check for an unescaped quote in this script)" ;;
esac
