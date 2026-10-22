#!/bin/bash
# spec-lint.sh [chroot] [spec ...] - rpmspec/rpmlint/builddep for every spec.
# Criteria: rpmspec -P rc 0; rpmlint summary "0 errors"; dnf builddep output
# free of the no-provider markers (its exit code is 1 whenever a transaction
# would run, which is the normal case). Exit 1 when any spec fails.
set -u
CH=${1:-44}
shift || true
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if [ "$#" -eq 0 ]; then
  set -- $(cd "$R" && find . -mindepth 2 -maxdepth 2 -name '*.spec' -type f | sed 's|^\./||' | sort)
fi
printf '%s\n' "$@" > /tmp/spec-lint-list.txt
docker run --rm -v "$R:/srv:ro" -v /tmp/spec-lint-list.txt:/list.txt:ro "registry.fedoraproject.org/fedora:$CH" bash -lc '
dnf -y -q --setopt=gpgcheck=0 install dnf-plugins-core rpm-build rpmlint >/dev/null 2>&1
dnf -y -q --setopt=gpgcheck=0 copr enable ackerman/nexus >/dev/null 2>&1
okp=0; badp=0; okl=0; badl=0; okd=0; badd=0
while read -r rel; do
  s=/srv/$rel; p=$(basename "$rel" .spec)
  if rpmspec -P --define "_topdir /tmp" "$s" >/tmp/one.spec 2>/tmp/rp.err; then okp=$((okp+1)); else badp=$((badp+1)); echo "RPMSPEC_FAIL $p: $(head -2 /tmp/rp.err | tr "\n" " ")"; fi
  if rpmlint "$s" >/tmp/rl.out 2>&1; then
    if grep -qE "^[0-9]+ packages and [0-9]+ specfiles checked; [1-9][0-9]* errors" /tmp/rl.out; then
      badl=$((badl+1)); echo "RPMLINT_E $p: $(grep -m2 "^E: " /tmp/rl.out | tr "\n" " ")"
    else okl=$((okl+1)); fi
  else badl=$((badl+1)); echo "RPMLINT_RC $p: $(tail -1 /tmp/rl.out)"; fi
  if [ -s /tmp/one.spec ] && dnf -y -q --setopt=gpgcheck=0 builddep --assumeno /tmp/one.spec >/tmp/bd.out 2>&1; then okd=$((okd+1)); else
    if grep -qE "no package matched|nothing provides|no match for argument|failed to solve" /tmp/bd.out; then
      badd=$((badd+1)); echo "BUILDEP_FAIL $p: $(grep -m1 -E "no package matched|nothing provides|no match for argument|failed to solve" /tmp/bd.out)"
    else okd=$((okd+1)); fi
  fi
done < /list.txt
echo "rpmspec -P PASS: $okp specs, $badp fail"
echo "rpmlint PASS: $okl specs (0 errors), $badl fail"
echo "dnf builddep PASS: $okd specs, $badd fail"
[ $((badp+badl+badd)) -eq 0 ] || exit 1
' 2>&1
