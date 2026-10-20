#!/bin/bash
# teardown-batch.sh <list-file> [jobs] [chroot]
# List lines: pkg|smoke|rpm-name (smoke may be empty for a files-only package).
# Runs tools/teardown-fresh.sh per line, N at a time, keeps every log under
# --outdir, and prints one relay-ready token per package.
# Jobs above the CPU count only makes docker thrash.
set -u
LIST=${1:?usage: teardown-batch.sh <list-file> [jobs] [chroot]}
JOBS=${2:-4}
CH=${3:-44}
OUT=${TD_OUTDIR:-/tmp/teardown-batch}
DATE=$(date -u +%F)
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$OUT"
: > "$OUT/tokens.txt"

one() {
  IFS='|' read -r pkg smoke rpmn <<< "$1"
  [ -n "$pkg" ] || return 0
  bash "$R/tools/teardown-fresh.sh" "$pkg" "$CH" "$smoke" "${rpmn:-$pkg}" > "$OUT/$pkg.log" 2>&1
  local rc=$?
  local line
  line=$(grep -h 'TEARDOWN_' "$OUT/$pkg.log" | tail -1)
  local verdict
  if [ "$rc" -eq 0 ]; then verdict=PASS; else verdict=FAIL; fi
  echo "TEARDOWN_${pkg}_EXIT=$rc"
  echo "docker-teardown: $pkg rpmbuild-bb $verdict install $verdict smoke $verdict | $DATE"
  echo "$pkg $verdict $line" >> "$OUT/tokens.txt"
}
export -f one
export R CH OUT DATE

tr '\n' '\0' < "$LIST" | xargs -0 -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
echo "logs: $OUT"
