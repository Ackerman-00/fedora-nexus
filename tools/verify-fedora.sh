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

  expected=$(find . -mindepth 2 -maxdepth 2 -name '*.spec' -type f -print | wc -l)
  if [[ "$expected" -eq 0 ]]; then
    echo "FAIL: NOT COMPLETE -- no package specs found"
    FAIL=1
  fi

  # version-checked is an honest label for freshness checks without a container
  # teardown (see PROMPT). It counts here only with same-run upstream evidence
  # (checked below); the 11 mains additionally need docker-teardown PASS.
  # Count DISTINCT package names, not matching lines: prose mentioning a
  # status must not satisfy the inventory bar.
  dep_rows=$(grep -oE "^\| [a-zA-Z0-9._+-]+ \|.*\| (deps-verified|deps-fixed|version-checked|retired-stub) \|" "$RELAY" 2>/dev/null | awk -F'|' '{gsub(/ /,"",$2); print $2}' | sort -u | wc -l || true)
  dep_rows=${dep_rows:-0}
  echo "Inventory: $expected specs; strict dependency rows: $dep_rows"
  if [[ "$dep_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- every package needs deps-verified/deps-fixed/version-checked teardown evidence (or retired-stub); found $dep_rows, need $expected"
    FAIL=1
  else
    echo "PASS: strict dependency rows cover inventory"
  fi

  unproven_rows=$(grep -oE "^\| [a-zA-Z0-9._+-]+ \|.*unproven:" "$RELAY" 2>/dev/null | awk -F'|' '{gsub(/ /,"",$2); print $2}' | sort -u | wc -l || true)
  unproven_rows=${unproven_rows:-0}
  echo "Correctness-contract rows: $unproven_rows (need $expected)"
  if [[ "$unproven_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- every dependency row needs an unproven: contract"
    FAIL=1
  else
    echo "PASS: correctness contract covers inventory"
  fi

  # Require a same-run upstream evidence row for every package. The trailing
  # date field must be today or yesterday: this prevents carrying an old
  # upstream conclusion forward as a current audit.
  # (TODAY/YEST are computed in the MAINS block below; precompute here.)
  TODAY=$(date -u +%F)
  YEST=$(date -u -d yesterday +%F 2>/dev/null || date -u -v-1d +%F)
  upstream_rows=$(grep -cE "\| upstream: [^|]+ \|.*($TODAY|$YEST)" "$RELAY" 2>/dev/null || true)
  upstream_rows=${upstream_rows:-0}
  echo "Upstream evidence rows: $upstream_rows (need $expected)"
  if [[ "$upstream_rows" -lt "$expected" ]]; then
    echo "FAIL: NOT COMPLETE -- every package needs a fresh upstream evidence row"
    FAIL=1
  else
    echo "PASS: upstream evidence covers inventory"
  fi

  if ! grep -q "| package | packaged version |" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- version accuracy table missing"
    FAIL=1
  else
    echo "PASS: version accuracy table present"
  fi
  for tool in "rpmspec -P" "dnf builddep" "rpmlint"; do
    if ! grep -qi "$tool.*PASS\|PASS.*$tool" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- missing PASS evidence for $tool"
      FAIL=1
    else
      echo "PASS: $tool evidence present"
    fi
  done
  if ! grep -qi "install-test table" "$RELAY" && ! grep -qiE "\| package \| (chroot \| )?COPR build \|" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- install-test table missing"
    FAIL=1
  else
    echo "PASS: install-test table present"
  fi
  if ! grep -qiE "^teardown-slice:" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- teardown-slice ledger missing"
    FAIL=1
  else
    echo "PASS: teardown-slice ledger present"
  fi

  MAINS="umbriel-git xdg-desktop-portal-umbriel-git helium-browser zen-browser heroic-games-launcher protonplus mangowm noctalia-greeter ly wlroots"
  for pkg in $MAINS; do
    if ! grep -qiE "docker-teardown: $pkg .*PASS" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' lacks fresh docker-teardown PASS"
      FAIL=1
    fi
    if ! grep -qiE "upstream: $pkg .*($TODAY|$YEST)" "$RELAY"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' lacks fresh upstream evidence"
      FAIL=1
    fi
  done
  if ! grep -qiE "docker-teardown:.*PASS" "$RELAY"; then
    echo "FAIL: NOT COMPLETE -- no docker teardown evidence"
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

if [[ "$FAIL" -ne 0 ]]; then
  echo "FAIL: NOT COMPLETE -- agent must continue, repair gaps, and rerun verification"
  exit 1
fi
echo "PASS: VERIFICATION PASSED -- strict dependency, upstream, evidence, and install gates passed"
exit 0
