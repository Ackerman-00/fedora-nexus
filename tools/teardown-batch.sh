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
  local pkg smoke rpmn _rpmn pch row rest
  pch=$CH
  if [ "$FORMAT" = probes ]; then
    # split on the first two pipes only: a smoke command carries shell pipes
    row=$1
    pkg=${row%%|*}; rest=${row#*|}
    _rpmn=${rest%%|*}; smoke=${rest#*|}
    case "${smoke##*|}" in
      4[3-9]|rawhide)
        if [ "${smoke%|*}" != "$smoke" ]; then pch=${smoke##*|}; smoke=${smoke%|*}; fi ;;
    esac
    rpmn=$_rpmn
    if [ -z "$_rpmn" ] || [ -z "$smoke" ]; then
      echo "docker-teardown: $pkg HARNESS_ERROR list-not-probes-format (need pkg|dnf-name|smoke)"
      echo "$pkg rc=harness list-format" >> "$OUT/tokens.txt"
      return 6
    fi
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
  bash "$R/tools/teardown-fresh.sh" "$pkg" "$pch" "$smoke" "${rpmn:-$pkg}" > "$OUT/$pkg.log" 2>&1
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

# preflight: refuse a list whose columns are not readable in the chosen format
first=$(grep -m1 -v '^[[:space:]]*$' "$LIST" || true)
IFS='|' read -r _f1 _f2 _f3 <<< "$first"
if [ "$FORMAT" = probes ]; then
  if [ -z "${_f2:-}" ] || [ -z "${_f3:-}" ]; then
    echo "FATAL: $LIST is not pkg|dnf-name|smoke; probes lists need 3 columns" >&2
    exit 2
  fi
elif [[ "${_f3:-}" == *" "* || "${_f3:-}" == /* || "${_f3:-}" == *=* ]]; then
  echo "FATAL: $LIST is pkg|dnf-name|smoke; re-run with --probes" >&2
  exit 2
fi

tr '\n' '\0' < "$LIST" | xargs -0 -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
echo "logs: $OUT"
