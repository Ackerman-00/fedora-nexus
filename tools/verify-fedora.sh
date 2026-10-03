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
  # teardown (see PROMPT). It counts here only with a same-run same-package
  # upstream evidence row; the 10 mains additionally need a dated
  # docker-teardown PASS. EVERY check below is scoped to this run's block
  # (run_id: to the next run_id:) so accumulated history can satisfy nothing.
  scope=$(awk -v id="run_id: $RUN_ID" '$0==id{f=1;next} f&&/^run_id: /{exit} f' "$RELAY")

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
    if ! printf '%s' "$scope" | grep -qE "upstream: $pkg .*($TODAY|$YEST)"; then
      echo "FAIL: NOT COMPLETE -- $pkg is version-checked with no same-run upstream row"
      FAIL=1
    fi
  done

  if ! printf '%s' "$scope" | grep -q "| package | packaged version |"; then
    echo "FAIL: NOT COMPLETE -- version accuracy table missing from THIS run's block"
    FAIL=1
  else
    echo "PASS: version accuracy table present"
  fi
  for tool in "rpmspec -P" "dnf builddep" "rpmlint"; do
    if ! printf '%s' "$scope" | grep -qi "$tool.*PASS\|PASS.*$tool"; then
      echo "FAIL: NOT COMPLETE -- missing PASS evidence for $tool in THIS run's block"
      FAIL=1
    else
      echo "PASS: $tool evidence present"
    fi
  done
  if ! printf '%s' "$scope" | grep -qi "install-test table" && ! printf '%s' "$scope" | grep -qiE "\| package \| (chroot \| )?COPR build \|"; then
    echo "FAIL: NOT COMPLETE -- install-test table missing from THIS run's block"
    FAIL=1
  else
    echo "PASS: install-test table present"
  fi

  slice_line=$(printf '%s' "$scope" | grep -m1 -E "^teardown-slice:" || true)
  if [[ -z "$slice_line" ]]; then
    echo "FAIL: NOT COMPLETE -- teardown-slice ledger missing from THIS run's block"
    FAIL=1
  else
    slice_pkgs=$(printf '%s' "$slice_line" | sed -E 's/^teardown-slice: *//; s/ *\|.*$//')
    slice_n=$(printf '%s\n' $slice_pkgs | grep -c . || true)
    min_slice=$(( (expected + 7) / 8 ))
    if [[ "$slice_n" -lt "$min_slice" ]]; then
      echo "FAIL: NOT COMPLETE -- teardown slice has $slice_n packages, need >= $min_slice (fleet rotates within 8 runs)"
      FAIL=1
    else
      echo "PASS: teardown slice size $slice_n >= $min_slice"
    fi
    for pkg in $slice_pkgs; do
      if ! printf '%s' "$scope" | grep -qiE "docker-teardown: $pkg .*PASS.*($TODAY|$YEST)"; then
        echo "FAIL: NOT COMPLETE -- slice package '$pkg' lacks a fresh dated docker-teardown PASS"
        FAIL=1
      fi
    done
  fi

  MAINS="umbriel-git xdg-desktop-portal-umbriel-git helium-browser zen-browser heroic-games-launcher protonplus mangowm noctalia-greeter ly wlroots"
  for pkg in $MAINS; do
    if ! printf '%s' "$scope" | grep -qiE "docker-teardown: $pkg .*PASS.*($TODAY|$YEST)"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' lacks fresh dated docker-teardown PASS"
      FAIL=1
    fi
    if ! printf '%s' "$scope" | grep -qiE "upstream: $pkg .*($TODAY|$YEST)"; then
      echo "FAIL: NOT COMPLETE -- main package '$pkg' lacks fresh upstream evidence"
      FAIL=1
    fi
  done
  if ! printf '%s' "$scope" | grep -qiE "docker-teardown:.*PASS.*($TODAY|$YEST)"; then
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

if [[ "$FAIL" -ne 0 ]]; then
  echo "FAIL: NOT COMPLETE -- agent must continue, repair gaps, and rerun verification"
  exit 1
fi
echo "PASS: VERIFICATION PASSED -- strict dependency, upstream, evidence, and install gates passed"
exit 0
