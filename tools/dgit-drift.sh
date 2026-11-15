#!/bin/bash
# Compare the spec COPR last built (copr-dist-git) with the spec in this checkout.
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BASE=${DGIT_BASE:-https://copr-dist-git.fedorainfracloud.org/git/ackerman/nexus}
WORK=${DGIT_WORK:-/tmp/dgit-drift}
rm -rf "$WORK"; mkdir -p "$WORK"
same=0; drifted=0; noclone=0
for d in "$R"/*/; do
  p=$(basename "$d")
  spec=$(ls "$d"*.spec 2>/dev/null | head -1)
  [ -n "$spec" ] || continue
  spec=$(basename "$spec")
  copr=$(sed -n 's/^Name:[[:space:]]*//p' "$d$spec" | head -1)
  for cand in "$p" "$copr"; do
    git clone -q --no-checkout --depth 1 "$BASE/$cand.git" "$WORK/$p" 2>/dev/null && break
  done
  if [ ! -d "$WORK/$p/.git" ]; then
    echo "DRIFT_NO_REPO $p"; noclone=$((noclone+1)); continue
  fi
  ( cd "$WORK/$p" && git checkout -q HEAD -- "$spec" 2>/dev/null ) || { echo "DRIFT_NO_SPEC $p"; noclone=$((noclone+1)); continue; }
  if diff -q "$WORK/$p/$spec" "$d$spec" >/dev/null 2>&1; then
    same=$((same+1)); continue
  fi
  drifted=$((drifted+1))
  if [ -z "$(diff -wB "$WORK/$p/$spec" "$d$spec")" ]; then
    echo "DRIFT_WHITESPACE $p"
  else
    echo "DRIFT_CONTENT $p"
    diff -u "$WORK/$p/$spec" "$d$spec" | sed -n '3,20p' | sed 's/^/    /'
  fi
done
echo "DRIFT_SUMMARY identical=$same whitespace_only_or_content=$drifted no_repo=$noclone"
