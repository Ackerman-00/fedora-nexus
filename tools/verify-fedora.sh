#!/usr/bin/env bash
set -euo pipefail
# Strict completion verifier for fedora-nexus.
if [[ "${1:-}" == "--print-mains" ]]; then
  echo "umbriel-git xdg-desktop-portal-umbriel-git helium-browser zen-browser heroic-games-launcher protonplus mangowm noctalia-greeter ly wlroots"
  exit 0
fi
RUN_ID="${RUN_ID:-}"
RELAY=".opencode-relay.md"
FAIL=0
# One source for the mains list: the workflow gate calls --print-mains, so a
# second literal here could check a different set than the gate.
MAINS="$(bash "${BASH_SOURCE[0]}" --print-mains)"

echo "----- VERIFICATION REPORT -----"
if [[ -f "$RELAY" ]]; then
  if [[ -z "$RUN_ID" ]]; then
    echo "FAIL: NOT COMPLETE -- RUN_ID not set, cannot verify relay ownership"
    FAIL=1
  elif ! grep -qx "run_id: $RUN_ID" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- relay is not for this run (expected run_id: $RUN_ID)"
    FAIL=1
  else
    echo "PASS: relay run_id matches this run"
  fi

  # Mirror gate_passes() in opencode-schedule.yml
  expected=$(find . -mindepth 2 -maxdepth 2 -name '*.spec' -type f -print | wc -l)
  if [[ "$expected" -eq 0 ]]; then
    echo "FAIL: NOT COMPLETE -- no package specs found"
    FAIL=1
  fi

  scope=$(awk -v id="run_id: $RUN_ID" '$0==id{f=1;next} f&&/^run_id: /{exit} f' "$RELAY")

  if ! grep -qix "status: complete" <<< "$scope"; then
    echo "FAIL: NOT COMPLETE -- this run's block does not carry status: complete"
    FAIL=1
  else
    echo "PASS: status complete in this run's block"
  fi
  if ! grep -q "| package | upstream deps found |" <<< "$scope"; then
    echo "FAIL: NOT COMPLETE -- dependency audit table header missing from THIS run's block (gate requires '| package | upstream deps found |')"
    FAIL=1
  else
    echo "PASS: dependency audit table header present"
  fi

  dep_rows=$(printf '%s' "$scope" | grep -oE "^\| [a-zA-Z0-9._+-]+ \|.*\| (deps-verified|deps-fixed|version-checked|retired-stub) \|" | awk -F'|' '{gsub(/ /,"",$2); print $2}' | sort -u | wc -l || true)
  dep_rows=${dep_rows:-0}
  echo "Inventory: $expected specs; strict dependency rows: $dep_rows"
  if [[ "$dep_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- every package needs deps-verified/deps-fixed/version-checked teardown evidence (or retired-stub) in THIS run's block; found $dep_rows, need $expected"
    FAIL=1
  else
    echo "PASS: strict dependency rows cover inventory"
  fi

  unproven_rows=$(printf '%s' "$scope" | grep -oE "^\| [a-zA-Z0-9._+-]+ \|.*unproven:" | awk -F'|' '{gsub(/ /,"",$2); print $2}' | sort -u | wc -l || true)
  unproven_rows=${unproven_rows:-0}
  echo "Correctness-contract rows: $unproven_rows (need $expected)"
  if [[ "$unproven_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- every dependency row needs an unproven: contract in THIS run's block"
    FAIL=1
  else
    echo "PASS: correctness contract covers inventory"
  fi

  TODAY=$(date -u +%F)
  YEST=$(date -u -d yesterday +%F 2>/dev/null || date -u -v-1d +%F)
  upstream_rows=$(printf '%s' "$scope" | grep -E "upstream: [a-zA-Z0-9._+-]+ .*($TODAY|$YEST)" | grep -oE "upstream: [a-zA-Z0-9._+-]+" | awk '{print $2}' | sort -u | wc -l || true)
  upstream_rows=${upstream_rows:-0}
  echo "Upstream evidence rows (distinct packages): $upstream_rows (need $expected)"
  if [[ "$upstream_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- every package needs a fresh upstream evidence row in THIS run's block"
    FAIL=1
  else
    echo "PASS: upstream evidence covers inventory"
  fi
  for pkg in $(printf '%s' "$scope" | grep -oE "^\| [a-zA-Z0-9._+-]+ \|.*\| version-checked \|" | awk -F'|' '{gsub(/ /,"",$2); print $2}' | sort -u); do
    if ! grep -qE "upstream: $pkg .*($TODAY|$YEST)" <<< "$scope"; then
      echo "FAIL: NOT COMPLETE -- $pkg is version-checked with no same-run upstream row"
      FAIL=1
    fi
  done

  if ! grep -q "| package | packaged version |" <<< "$scope"; then
    echo "FAIL: NOT COMPLETE -- version accuracy table missing from THIS run's block"
    FAIL=1
  else
    echo "PASS: version accuracy table present"
  fi
  for tool in "rpmspec -P" "dnf builddep" "rpmlint"; do
    if ! grep -qi "$tool.*PASS\|PASS.*$tool" <<< "$scope"; then
      echo "FAIL: NOT COMPLETE -- missing PASS evidence for $tool in THIS run's block"
      FAIL=1
    else
      echo "PASS: $tool evidence present"
    fi
  done
  if ! grep -qi "install-test table" <<< "$scope" && ! grep -qiE "\| package \| (chroot \| )?COPR build \|" <<< "$scope"; then
    echo "FAIL: NOT COMPLETE -- install-test table missing from THIS run's block"
    FAIL=1
  else
    echo "PASS: install-test table present"
  fi
  # Install-test verdicts are TRUTH, not decoration. A FAIL row means the
  # package is broken right now, and a FAIL row next to a same-run
  # "install PASS" teardown is self-contradicting. Both fail the run.
  IT=$(printf '%s' "$scope" | awk -F'|' '
    /^\|/ {
      n = split($0, a, "|");
      if (n != 6 && n != 7) next;
      pkg = a[2];
      if (n == 6) { build = "n/a"; v = a[5]; } else { build = a[3]; v = a[6]; }
      gsub(/^[ \t]+|[ \t]+$/, "", pkg); gsub(/^[ \t]+|[ \t]+$/, "", build); gsub(/^[ \t]+|[ \t]+$/, "", v);
      if (n == 7 && build !~ /^([0-9]+|n\/a)$/) next;
      if (toupper(v) == "PASS" || toupper(v) == "FAIL" || toupper(v) == "EXTERNAL") printf "%s %s\n", pkg, toupper(v);
    }' | sort -u)
  it_fail=$(grep -c ' FAIL$' <<< "$IT" || true)
  it_pass=$(grep -c ' PASS$' <<< "$IT" || true)
  if [[ "$it_fail" -gt 0 ]]; then
    echo "FAIL: NOT COMPLETE -- install-test table has $it_fail FAIL row(s): $(grep ' FAIL$' <<< "$IT" | awk '{printf "%s ", $1}')"
    FAIL=1
  fi
  if [[ $(( it_fail + it_pass )) -lt 10 ]]; then
    echo "FAIL: NOT COMPLETE -- install-test table has $(( it_fail + it_pass )) machine-readable rows, need >= 10"
    FAIL=1
  fi
  for pkg in $MAINS; do
    if ! grep -qx "$pkg PASS" <<< "$IT"; then
      if grep -qx "$pkg EXTERNAL" <<< "$IT" && grep -qiE "GAP: external.*$pkg" <<< "$scope"; then
        continue
      fi
      echo "FAIL: NOT COMPLETE -- main package '$pkg' has no PASS install-test row"
      FAIL=1
    fi
  done
  for pkg in $(awk '{print $1}' <<< "$IT"); do
    if grep -qE "docker-teardown: $pkg .*install PASS" <<< "$scope" && grep -qx "$pkg FAIL" <<< "$IT"; then
      echo "FAIL: NOT COMPLETE -- $pkg says install FAIL but has a same-run docker-teardown install PASS"
      FAIL=1
    fi
  done
  for pkg in $(awk '$2=="EXTERNAL"{print $1}' <<< "$IT"); do
    if ! grep -qiE "GAP: external.*$pkg" <<< "$scope"; then
      echo "FAIL: NOT COMPLETE -- $pkg install verdict is EXTERNAL without a GAP: external line naming it"
      FAIL=1
    fi
  done

  slice_line=$(printf '%s' "$scope" | grep -m1 -E "^teardown-slice:" || true)
  if [[ -z "$slice_line" ]]; then
    echo "FAIL: NOT COMPLETE -- teardown-slice ledger missing from THIS run's block"
    FAIL=1
  else
    slice_pkgs=$(printf '%s' "$slice_line" | sed -E 's/^teardown-slice: *//; s/ *\|.*$//')
    slice_n=$(printf '%s\n' $slice_pkgs | grep -c . || true)
    min_slice=$(( (expected + 3) / 4 ))
    if [[ "$slice_n" -lt "$min_slice" ]]; then
      echo "FAIL: NOT COMPLETE -- teardown slice has $slice_n packages, need >= $min_slice (fleet rotates within 4 runs)"
      FAIL=1
    else
      echo "PASS: teardown slice size $slice_n >= $min_slice"
    fi
    for pkg in $slice_pkgs; do
      if ! grep -qiE "docker-teardown: $pkg .*PASS.*($TODAY|$YEST)" <<< "$scope"; then
        echo "FAIL: NOT COMPLETE -- slice package '$pkg' lacks a fresh dated docker-teardown PASS"
        FAIL=1
      fi
    done
  fi

  for pkg in $MAINS; do
    if ! grep -qiE "docker-teardown: $pkg .*PASS.*($TODAY|$YEST)" <<< "$scope"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' lacks fresh dated docker-teardown PASS"
      FAIL=1
    fi
    if ! grep -qiE "upstream: $pkg .*($TODAY|$YEST)" <<< "$scope"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' lacks fresh upstream evidence"
      FAIL=1
    fi
  done
  # GAP/HOLD classification
  g_decl=$(grep -ciE "^[[:space:]]*([-*][[:space:]]*)?((GAP|HOLD)[[:space:]]*:|not verified\b)" <<< "$scope" || true)
  g_head=$(grep -ciE "^[[:space:]]*([-*][[:space:]]*)?((GAP|HOLD)[[:space:]]*:|not verified\b)[^:]*:[[:space:]]*$" <<< "$scope" || true)
  g_cls=$(grep -ciE "^[[:space:]]*([-*][[:space:]]*)?((GAP|HOLD)[[:space:]]*:[[:space:]]*(external|actionable)|not verified\b.*\b(external|actionable)\b|(GAP|HOLD)[[:space:]]*:[[:space:]]*(none|nothing|n/a)\b|not verified\b[ 	]*:?[ 	]*(none|nothing|n/a)\b)" <<< "$scope" || true)
  g_act=$(grep -ciE "^[[:space:]]*([-*][[:space:]]*)?((GAP|HOLD)[[:space:]]*:[[:space:]]*actionable|not verified\b.*\bactionable\b)" <<< "$scope" || true)
  g_noreason=$(grep -ciE "^[[:space:]]*([-*][[:space:]]*)?((GAP|HOLD)[[:space:]]*:[[:space:]]*external|not verified\b.*\bexternal\b)[[:space:]]*:?[[:space:]]*$" <<< "$scope" || true)
  g_need=$(( g_decl - g_head ))
  g_unclass=$(( g_need - g_cls ))
  [ "$g_unclass" -lt 0 ] && g_unclass=0
  if [[ "$g_act" -gt 0 ]]; then
    echo "FAIL: NOT COMPLETE -- $g_act actionable gap(s)/HOLD(s) in this run's block; they must be FIXED, not named"
    FAIL=1
  fi
  if [[ "$g_unclass" -gt 0 ]]; then
    echo "FAIL: NOT COMPLETE -- $g_unclass gap(s)/HOLD(s) with no classification; use 'GAP: external - <reason>' or 'GAP: actionable - <what>'"
    FAIL=1
  fi
  if [[ "$g_noreason" -gt 0 ]]; then
    echo "FAIL: NOT COMPLETE -- $g_noreason 'external' gap(s)/HOLD(s) with no reason after the marker"
    FAIL=1
  fi
  if ! grep -qiE "docker-teardown:.*PASS.*($TODAY|$YEST)" <<< "$scope"; then
    echo "FAIL: NOT COMPLETE -- no docker teardown evidence in THIS run's block"
    FAIL=1
  fi
else
  echo "FAIL: NOT COMPLETE -- $RELAY missing"
  FAIL=1
fi

bad_specs=0
while IFS= read -r spec; do
  if ! grep -q '^Name:' "$spec" 2>/dev/null; then
    echo "FAIL: spec $spec missing Name:"
    bad_specs=$((bad_specs+1))
  fi
done < <(find . -mindepth 2 -maxdepth 2 -name '*.spec' -type f -print)
if [[ "$bad_specs" -gt 0 ]]; then
  FAIL=1
fi

# Defect accounting: every defect found this run is either fixed (counted)
# or proven external (a GAP/HOLD line carrying the probe). Finding none is
# allowed - leaving one unfixed and uncounted is not.
d_found=$(grep -oE '^[[:space:]]*defects-found:[[:space:]]*[0-9]+' <<< "$scope" | tail -1 | grep -oE '[0-9]+' || true)
d_fixed=$(grep -oE '^[[:space:]]*defects-fixed:[[:space:]]*[0-9]+' <<< "$scope" | tail -1 | grep -oE '[0-9]+' || true)
if [[ -z "$d_found" || -z "$d_fixed" ]]; then
  echo "FAIL: NOT COMPLETE -- defects-found/defects-fixed accounting missing from THIS run's block"
  FAIL=1
elif [[ $(( d_fixed + ${g_decl:-0} )) -lt $d_found ]]; then
  echo "FAIL: NOT COMPLETE -- defects-found: $d_found but defects-fixed: $d_fixed with ${g_decl:-0} external gap(s)"
  FAIL=1
else
  echo "PASS: defect accounting ($d_found found, $d_fixed fixed, ${g_decl:-0} external)"
fi
hunt_cats=$(grep -oE '^[[:space:]]*hunt: [a-z0-9-]+' <<< "$scope" | sort -u | wc -l || true)
if [[ "$hunt_cats" -lt 5 ]]; then
  echo "FAIL: NOT COMPLETE -- only $hunt_cats hunt categories recorded, need >= 5"
  FAIL=1
else
  echo "PASS: hunt categories $hunt_cats >= 5"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "FAIL: NOT COMPLETE -- agent must continue, repair gaps, and rerun verification"
  exit 1
fi
echo "PASS: VERIFICATION PASSED -- strict dependency, upstream, evidence, and install gates passed"
exit 0
