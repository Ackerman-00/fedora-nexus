#!/usr/bin/env bash
# Negative tests for the scheduler's evidence contract
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
FAIL=0
PASS=0

# check <name> <regex> <input> <expect: hit|miss>
check() {
  local name=$1 re=$2 input=$3 expect=$4 got
  if printf '%s\n' "$input" | grep -qiE "$re"; then got=hit; else got=miss; fi
  if [ "$got" = "$expect" ]; then
    PASS=$((PASS + 1))
  else
    echo "FAIL $name: expected $expect, got $got"
    FAIL=$((FAIL + 1))
  fi
}

SKILLS='skills: web-research linux-packaging rpm-copr security-audit code-review systematic-debugging verification-before-completion github-ops container-validation python-tooling writing-for-agents fedora-triage repo-improvement why-from-record'
SKILLS_SHORT='skills: web-research linux-packaging rpm-copr security-audit'
count_skills() { printf '%s\n' "$1" | grep -oE '\b(web-research|linux-packaging|rpm-copr|security-audit|code-review|systematic-debugging|verification-before-completion|github-ops|container-validation|python-tooling|writing-for-agents|fedora-triage|repo-improvement|why-from-record)\b' | sort -u | wc -l; }
[ "$(count_skills "$SKILLS")" -eq 14 ] && PASS=$((PASS+1)) || { echo 'FAIL skills: 14 ids expected'; FAIL=$((FAIL+1)); }
[ "$(count_skills "$SKILLS_SHORT")" -lt 14 ] && PASS=$((PASS+1)) || { echo 'FAIL skills: short list must fail'; FAIL=$((FAIL+1)); }

check 'websearch with URL' 'https?://' 'websearch: 12 queries, 9 sources, 2026-11-16 https://copr.fedorainfracloud.org/api_3/project' hit
check 'websearch without URL' 'https?://' 'websearch: 12 queries, 9 sources, 2026-11-16' miss
check 'websearch date' 'websearch: .*(2026-11-16|2026-11-15)' 'websearch: 12 queries https://example.org 2026-11-16' hit
check 'websearch stale date' 'websearch: .*(2026-11-16|2026-11-15)' 'websearch: 12 queries https://example.org 2026-01-01' miss

check 'improve with commit' 'landed:[[:space:]]*[0-9a-f]{7,40}|issue[[:space:]]*#[0-9]+' 'improve: 7 - guard - landed: 7dc8e4b9' hit
check 'improve with issue' 'landed:[[:space:]]*[0-9a-f]{7,40}|issue[[:space:]]*#[0-9]+' 'improve: 7 - guard - issue #107' hit
check 'improve empty landing' 'landed:[[:space:]]*[0-9a-f]{7,40}|issue[[:space:]]*#[0-9]+' 'improve: 7 - guard - landed:' miss
n_good=$(printf '%s\n' 'improve: 7 - guard - landed: 7dc8e4b9' | sed -E 's/^[[:space:]]*improve: ([0-9]+).*/\1/')
n_bad=$(printf '%s\n' 'improve: 3 - guard - landed: 7dc8e4b9' | sed -E 's/^[[:space:]]*improve: ([0-9]+).*/\1/')
[ "$n_good" -ge 5 ] && PASS=$((PASS+1)) || { echo 'FAIL improve: 7 candidates must pass'; FAIL=$((FAIL+1)); }
[ "$n_bad" -lt 5 ] && PASS=$((PASS+1)) || { echo 'FAIL improve: 3 candidates must fail'; FAIL=$((FAIL+1)); }

check 'why with source' '^[[:space:]]*why: .*source:' 'why: payload - source: AGENTS.md#buildroot - inference: none' hit
check 'why no source' '^[[:space:]]*why: .*source:' 'why: payload - seems obvious' miss
check 'why source token' '[0-9a-f]{7,40}|AGENTS\.md#|issue[[:space:]]*#[0-9]+|relay[[:space:]]+[0-9]+' 'why: payload - source: AGENTS.md#buildroot' hit
check 'why fake source token' '[0-9a-f]{7,40}|AGENTS\.md#|issue[[:space:]]*#[0-9]+|relay[[:space:]]+[0-9]+' 'why: payload - source: my gut' miss

check 'plan per changed pkg' '^[[:space:]]*plan: otr ' 'plan: otr - hypothesis A and B - repoquery probe' hit
check 'plan missing pkg' '^[[:space:]]*plan: otr ' 'plan: other - hypothesis - probe' miss

check 'deps per changed pkg' '^[[:space:]]*deps: otr ' 'deps: otr - source: meson.build - 3 missing BR' hit
check 'deps missing pkg' '^[[:space:]]*deps: otr ' 'deps: other - source: meson.build - none' miss
DEPS_SRC='^[[:space:]]*deps: .*(Cargo\.toml|meson\.build|CMakeLists\.txt|go\.mod|pyproject\.toml|https?://|\.spec)'
check 'deps with real source' "$DEPS_SRC" 'deps: otr - source: Cargo.toml - compared' hit
check 'deps with spec URL' "$DEPS_SRC" 'deps: otr - source: https://src.fedoraproject.org/rpms/otr/raw/main/f/otr.spec - compared' hit
check 'deps with fake source' "$DEPS_SRC" 'deps: otr - source: my memory - none' miss

check 'artifact per changed pkg' '^[[:space:]]*artifact: otr ' 'artifact: otr - upstream: https://example.org/x.deb - format: deb' hit
check 'artifact missing pkg' '^[[:space:]]*artifact: otr ' 'artifact: other - upstream: https://example.org - format: deb' miss
for art_field in 'https?://' 'format:' 'fedora-deps:' 'improvements:'; do
  good="artifact: otr - upstream: https://example.org/a.deb - format: deb - torn: control+ELF - fedora-deps: repoquery - improvements: 7"
  bad='artifact: otr - guessed from the filename'
  check "artifact field $art_field present" "^[[:space:]]*artifact: .*$art_field" "$good" hit
  check "artifact field $art_field missing" "^[[:space:]]*artifact: .*$art_field" "$bad" miss
done

check 'hunt category' '^[[:space:]]*hunt: builds ' 'hunt: builds - 73 newest builds - 0 failed' hit
check 'hunt missing category' '^[[:space:]]*hunt: published-nvr ' 'hunt: builds - 73 newest builds - 0 failed' miss

check 'GAP external with probe' '^[[:space:]]*([-*][[:space:]]*)?(GAP|HOLD): external.*\[probe:' 'GAP: external - chroot [probe: builder log 11334913]' hit
check 'HOLD external with probe' '^[[:space:]]*([-*][[:space:]]*)?(GAP|HOLD): external.*\[probe:' 'HOLD: external - upstream [probe: release API 404]' hit
check 'GAP external no probe' '^[[:space:]]*([-*][[:space:]]*)?(GAP|HOLD): external.*\[probe:' 'GAP: external - chroot broken' miss
check 'HOLD external no probe' '^[[:space:]]*([-*][[:space:]]*)?(GAP|HOLD): external.*\[probe:' 'HOLD: external - upstream not released' miss
check 'external no reason' '^[[:space:]]*([-*][[:space:]]*)?((GAP|HOLD)[[:space:]]*:[[:space:]]*external|not verified\b.*\bexternal\b)[[:space:]]*:?[[:space:]]*$' 'GAP: external' hit
check 'external with reason' '^[[:space:]]*([-*][[:space:]]*)?((GAP|HOLD)[[:space:]]*:[[:space:]]*external|not verified\b.*\bexternal\b)[[:space:]]*:?[[:space:]]*$' 'GAP: external - chroot [probe: log]' miss

OWNER='needs[[:space:]]*-?[[:space:]]*owner|wait(ing)? for (the )?owner|ask(ing)? (the )?owner|owner.{0,20}(approv|decid|permission)|(approv|permission).{0,20}from (the )?owner|owner declined'
check 'owner ask anchored' '^[[:space:]]*([-*][[:space:]]*)?(needs-owner|waiting for (the )?owner|owner approval)' 'needs-owner: refresh token' hit
check 'owner ask mid-line' "$OWNER" 'closing note: owner declined to pursue' hit
check 'clean relay line' "$OWNER" 'all 73 packages verified, published NVR matches' miss

echo "verifier self-test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
