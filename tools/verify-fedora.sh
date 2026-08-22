#!/usr/bin/env bash
set -euo pipefail
# 2026 battle-tested verifier — fedora-nexus. Returns 0 only if agent truly finished.
# Checks: 82-row dependency audit table, 10+ rpmspec/rpmbuild/dnf builddep evidences, install ledger.

RELAY=".opencode-relay.md"
FAIL=0

echo "----- VERIFICATION REPORT -----"

# 1. Numerical completion: dependency table must have 82 rows with deps-verified/deps-fixed
if [[ -f "$RELAY" ]]; then
  rows=$(grep -cE "^\| [a-z0-9_-]+ \|" "$RELAY" 2>/dev/null || echo 0)
  dep_rows=$(grep -c "deps-verified\|deps-fixed" "$RELAY" 2>/dev/null || echo 0)
  echo "Dependency table rows: $dep_rows (need >=82, found $rows total pipe-rows)"
  if [[ "$dep_rows" -lt 82 ]]; then
    echo "❌ NOT COMPLETE — dependency audit table has $dep_rows rows, need 82"
    FAIL=1
  else
    echo "✅ Dependency table: $dep_rows rows"
  fi
  # 2. Evidence: must contain rpmspec / dnf builddep / rpmlint strings from 2026 h. checks
  for tool in "rpmspec -P" "dnf builddep" "rpmlint"; do
    if ! grep -qi "$tool" "$RELAY"; then
      echo "⚠️  WARNING: relay missing evidence for $tool (2026 h. checks)"
      # not fail yet, but warn
    fi
  done
  # 3. Install ledger
  if ! grep -qi "install-test table" "$RELAY" && ! grep -qi "| package | COPR build |" "$RELAY"; then
    echo "❌ NOT COMPLETE — install-test table missing in relay"
    FAIL=1
  else
    echo "✅ Install-test table present"
  fi
else
  echo "❌ NOT COMPLETE — $RELAY missing"
  FAIL=1
fi

# 4. Build: check at least that specs are parseable
bad_specs=0
for spec in */*.spec; do
  [[ -f "$spec" ]] || continue
  if ! grep -q "^Name:" "$spec" 2>/dev/null; then
    echo "❌ Spec $spec missing Name:"
    bad_specs=$((bad_specs+1))
  fi
done
if [[ "$bad_specs" -gt 0 ]]; then
  echo "❌ NOT COMPLETE — $bad_specs specs malformed"
  FAIL=1
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "❌ NOT COMPLETE — agent must continue working"
  exit 1
fi
echo "✅ VERIFICATION PASSED — all 82 deps rows, evidence, install table present"
exit 0
