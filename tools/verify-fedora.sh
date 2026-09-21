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
  expected=$(ls */*.spec 2>/dev/null | wc -l)
  if [[ "$expected" -eq 0 ]]; then
    echo "FAIL: NOT COMPLETE -- no */*.spec found (run from repo root)"
    FAIL=1
  fi
  rows=$(grep -cE "^\| [a-z0-9_-]+ \|" "$RELAY" 2>/dev/null || true)
  rows=${rows:-0}
  dep_rows=$(grep -c "deps-verified\|deps-fixed\|version-checked\|retired-stub" "$RELAY" 2>/dev/null || true)
  dep_rows=${dep_rows:-0}
  echo "Inventory: $expected specs; dependency table rows: $dep_rows (found $rows total pipe-rows)"
  echo "(statuses: deps-verified = docker teardown this run; version-checked = update.sh/tags/API only; retired-stub rows for niri-git/noctalia-git count as valid — retired 2026-09-14 to Fedora official)"
  if [[ "$dep_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- dependency audit table has $dep_rows rows, need $expected (one per spec)"
    FAIL=1
  else
    echo "PASS: Dependency table: $dep_rows rows (>= $expected)"
  fi
  unproven_rows=$(grep -c "unproven:" "$RELAY" 2>/dev/null || true)
  unproven_rows=${unproven_rows:-0}
  echo "Correctness-contract rows: $unproven_rows (need $expected)"
  if [[ "$unproven_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- $unproven_rows audit rows carry the unproven: contract, need $expected (one per spec)"
    FAIL=1
  else
    echo "PASS: Correctness contract present on $unproven_rows rows"
  fi
  if ! grep -q "| package | packaged version |" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- version accuracy table (priority 2 deliverable) missing in relay"
    FAIL=1
  else
    echo "PASS: Version accuracy table present"
  fi
  for tool in "rpmspec -P" "dnf builddep" "rpmlint"; do
    if ! grep -qi "$tool.*PASS\|PASS.*$tool" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- relay missing fresh evidence for $tool (2026 h. checks, with PASS result)"
      FAIL=1
    fi
  done
  if ! grep -qi "install-test table" "$RELAY" && ! grep -qiE "\| package \| (chroot \| )?COPR build \|" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- install-test table missing in relay"
    FAIL=1
  else
    echo "PASS: Install-test table present"
  fi
  # TEARDOWN SLICE (2026-09-21): rows are cheap, container teardowns are proof.
  # The run must name its rotating slice AND paste one docker-teardown PASS
  # token per slice package. A deps-verified claim without teardown is theater.
  if ! grep -qiE "^teardown-slice:" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- relay missing 'teardown-slice:' line (rotating full-teardown slice + next-start package)"
    FAIL=1
  else
    echo "PASS: teardown-slice line present"
  fi
  # MAINS (2026-09-22): these 11 packages move fast and break silently.
  # Skipping their teardown while passing the gate on easy packages is the
  # exact failure this verifier exists to prevent. Every main MUST carry a
  # fresh docker-teardown PASS token every run. No carry-over, no exceptions
  # (a main that cannot be torn down this run keeps the relay `unfinished`).
  MAINS="xwayland-satellite-git umbriel-git xdg-desktop-portal-umbriel-git helium-browser zen-browser heroic-games-launcher protonplus mangowm noctalia-greeter ly wlroots"
  missing_mains=0
  for pkg in $MAINS; do
    if ! grep -qiE "docker-teardown: $pkg .*PASS" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' has no docker-teardown PASS token (full re-tear + rpmbuild + install + smoke, fresh container)"
      missing_mains=$((missing_mains+1))
    fi
  done
  if [[ "$missing_mains" -gt 0 ]]; then
    FAIL=1
  else
    echo "PASS: all 11 mains carry docker-teardown PASS"
  fi
  # ALWAYS-LIVE (2026-09-22): a teardown without a same-run upstream check is
  # stale work. Every main must ALSO carry a fresh `upstream: <pkg> ...` line
  # proving its pin/version was re-verified live this run (ls-remote / tags
  # API / Codeberg / GitLab output). Carried-over conclusions fail here: the
  # line must contain THIS run's UTC date (today or yesterday, to survive
  # midnight crossings) - an old date (or none) means recycled evidence.
  TODAY=$(date -u +%F); YEST=$(date -u -d yesterday +%F 2>/dev/null || date -u -v-1d +%F)
  missing_upstream=0
  for pkg in $MAINS; do
    if ! grep -qiE "upstream: $pkg .*($TODAY|$YEST)" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' has no fresh 'upstream: $pkg ... <today-UTC-date>' live-check line this run (upstream checks must run live every run, never carried over)"
      missing_upstream=$((missing_upstream+1))
    fi
  done
  if [[ "$missing_upstream" -gt 0 ]]; then
    FAIL=1
  else
    echo "PASS: all 11 mains carry fresh upstream live-check lines"
  fi
  teardown_pass=$(grep -cE "docker-teardown: [a-z0-9_.-]+ .*PASS" "$RELAY" 2>/dev/null || true)
  teardown_pass=${teardown_pass:-0}
  echo "Docker teardown evidence tokens: $teardown_pass (11 mains + rotating slice)"
  # Every package named in the slice must have its own PASS token.
  # Slice line format: teardown-slice: <pkg> <pkg> ... | next-start: <pkg>
  slice_seg=$(grep -iE "^teardown-slice:" "$RELAY" | head -n 1 | sed -e 's/^[Tt]eardown-slice:[[:space:]]*//' -e 's/|.*//' || true)
  missing_teardown=0
  for pkg in $slice_seg; do
    case "$pkg" in
      pkgs|slice|next-start|next|start) continue ;;
    esac
    if ! grep -qiE "docker-teardown: $pkg .*PASS" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- slice package '$pkg' has no docker-teardown PASS token"
      missing_teardown=$((missing_teardown+1))
    fi
  done
  if [[ "$missing_teardown" -gt 0 ]]; then
    FAIL=1
  else
    echo "PASS: every slice package carries docker-teardown PASS"
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
echo "PASS: VERIFICATION PASSED -- all $expected deps rows, version table, evidence, install table present"
exit 0
