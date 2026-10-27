#!/bin/bash
set -u
FORMAT=smoke-first
_args=()
for a in "$@"; do
  case "$a" in
    --probes) FORMAT=probes ;;
    *) _args+=("$a") ;;
  esac
done
set -- ${_args[@]+"${_args[@]}"}
LIST=${1:?usage: teardown-batch.sh <list-file> [jobs] [chroot] [--probes]}
JOBS=${2:-4}
CH=${3:-44}
OUT=${TD_OUTDIR:-/tmp/teardown-batch}
DATE=$(date -u +%F)
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$OUT"
: > "$OUT/tokens.txt"

one() {
  local pkg smoke rpmn _rpmn
  if [ "$FORMAT" = probes ]; then
    IFS='|' read -r pkg _rpmn smoke <<< "$1"
    rpmn=$_rpmn
  else
    IFS='|' read -r pkg smoke rpmn <<< "$1"
  fi
  if [[ "$rpmn" == *" "* || "$rpmn" == /* || "$rpmn" == *=* ]]; then
    echo "TEARDOWN_${pkg}_EXIT=harness"
    echo "docker-teardown: $pkg HARNESS_ERROR list-order (rpm-name field is a command: $rpmn)"
    echo "$pkg rc=harness list-order" >> "$OUT/tokens.txt"
    return 6
  fi
  [ -n "$pkg" ] || return 0
  bash "$R/tools/teardown-fresh.sh" "$pkg" "$CH" "$smoke" "${rpmn:-$pkg}" > "$OUT/$pkg.log" 2>&1
  local rc=$?
  local line fields
  line=$(grep -hF "TEARDOWN_$pkg=" "$OUT/$pkg.log" | tail -1)
  fields=${line#*=}
  if [ -z "$fields" ]; then
    fields="rpmbuild-bb FAIL install FAIL smoke FAIL"
  fi
  echo "TEARDOWN_${pkg}_EXIT=$rc"
  echo "docker-teardown: $pkg $fields | $DATE"
  echo "$pkg rc=$rc $line" >> "$OUT/tokens.txt"
}
export -f one
export R CH OUT DATE FORMAT

tr '\n' '\0' < "$LIST" | xargs -0 -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
echo "logs: $OUT"
