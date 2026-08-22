#!/usr/bin/env bash
set -euo pipefail
# 2026 battle-tested verifier -- fedora-nexus. Returns 0 only if agent truly finished.
RUN_ID="${RUN_ID:-}"
RELAY=".opencode-relay.md"
FAIL=0
echo "----- VERIFICATION REPORT -----"
if [[ -f "$RELAY" ]]; then
  if [[ -n "$RUN_ID" ]] && ! grep -qx "run_id: $RUN_ID" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- relay is not for this run (expected run_id: $RUN_ID)"
    FAIL=1
  else
    echo "PASS: relay run_id matches this run"
  fi
  rows=$(grep -cE "^\| [a-z0-9_-]+ \|" "$RELAY" 2>/dev/null || echo 0)
  dep_rows=$(grep -c "deps-verified\|deps-fixed" "$RELAY" 2>/dev/null || echo 0)
  echo "Dependency table rows: $dep_rows (need >=82, found $rows total pipe-rows)"
  if [[ "$dep_rows" -lt 82 ]]; then
    echo "FAIL: NOT COMPLETE -- dependency audit table has $dep_rows rows, need 82"
    FAIL=1
  else
    echo "PASS: Dependency table: $dep_rows rows"
  fi
  for tool in "rpmspec -P" "dnf builddep" "rpmlint"; do
    if ! grep -qi "$tool.*PASS\|PASS.*$tool" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- relay missing fresh evidence for $tool (2026 h. checks, with PASS result)"
      FAIL=1
    fi
  done
  if ! grep -qi "install-test table" "$RELAY" && ! grep -qi "| package | COPR build |" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- install-test table missing in relay"
    FAIL=1
  else
    echo "PASS: Install-test table present"
  fi
else
  echo "FAIL: NOT COMPLETE -- $RELAY missing"
  FAIL=1
fi
bad_specs=0
for spec in */*.spec; do
  [[ -f "$spec" ]] || continue
  if ! grep -q "^Name:" "$spec" 2>/dev/null; then
    echo "FAIL: Spec $spec missing Name:"
    bad_specs=$((bad_specs+1))
  fi
done
if [[ "$bad_specs" -gt 0 ]]; then
  echo "FAIL: NOT COMPLETE -- $bad_specs specs malformed"
  FAIL=1
fi
if [[ "$FAIL" -ne 0 ]]; then
  echo "FAIL: NOT COMPLETE -- agent must continue working"
  exit 1
fi
echo "PASS: VERIFICATION PASSED -- all 82 deps rows, evidence, install table present"
exit 0
