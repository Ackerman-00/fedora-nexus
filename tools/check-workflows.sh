#!/usr/bin/env bash
# check-workflows.sh - validate .github/workflows/*.yml before pushing them.
#
# A workflow file that GitHub rejects kills every run of it: the push creates
# a failed run with no jobs and the schedule dies silently. That happened on
# 2026-09-09 (commit ad69ca3 added the invalid scope `workflows: write`) and
# again on 2026-10-20 (the scopes `code-quality` and `vulnerability-alerts` are
# NOT valid in a permissions block, even though the docs table lists them).
# actionlint is the authority on the accepted scope list, not the docs prose.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
FAIL=0

echo "== YAML parse =="
python3 - <<'PY' || FAIL=1
import glob, sys, yaml
for f in sorted(glob.glob(".github/workflows/*.yml")):
    try:
        yaml.safe_load(open(f))
        print(f"OK   {f}")
    except Exception as e:
        print(f"FAIL {f}: {e}")
        sys.exit(1)
PY

echo "== actionlint =="
# -shellcheck= disables shellcheck integration: its style infos are not
# workflow validity and would otherwise fail a valid file.
if command -v actionlint >/dev/null 2>&1; then
  actionlint -shellcheck= -no-color .github/workflows/*.yml && echo "OK   actionlint clean" || FAIL=1
else
  if [ -x /tmp/opencode/actionlint ]; then
    /tmp/opencode/actionlint -shellcheck= -no-color .github/workflows/*.yml && echo "OK   actionlint clean" || FAIL=1
  else
    echo "SKIP actionlint not installed - install it with:"
    echo "  bash <(curl -sL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)"
  fi
fi

echo "== permission scopes =="
python3 - <<'PY' || FAIL=1
import glob, sys, yaml
# The scopes GitHub accepts in a permissions block (actionlint's list).
VALID = {"actions","artifact-metadata","attestations","checks","contents",
         "deployments","discussions","id-token","issues","models","packages",
         "pages","pull-requests","repository-projects","security-events",
         "statuses"}
VALUES = {"read","write","none"}
bad = 0
for f in sorted(glob.glob(".github/workflows/*.yml")):
    d = yaml.safe_load(open(f)) or {}
    blocks = []
    if isinstance(d.get("permissions"), dict):
        blocks.append(("top", d["permissions"]))
    for jn, j in (d.get("jobs") or {}).items():
        if isinstance(j.get("permissions"), dict):
            blocks.append((jn, j["permissions"]))
    for where, perm in blocks:
        for k, v in perm.items():
            if k not in VALID:
                print(f"FAIL {f} [{where}]: unknown scope {k}")
                bad = 1
            elif v not in VALUES:
                print(f"FAIL {f} [{where}]: {k}={v} not in read/write/none")
                bad = 1
        if perm:
            print(f"OK   {f} [{where}]: {len(perm)} scope(s)")
sys.exit(bad)
PY

echo "== gate and verifier agree on the contract =="
python3 - <<'PY' || FAIL=1
import re, sys

def read(p):
    return open(p, encoding="utf-8", errors="replace").read()

gate = read(".github/workflows/opencode-schedule.yml")
ver = read("tools/verify-fedora.sh")

def awk_block(text):
    m = re.search(r"awk -F'\|' '(.*?)'\s*\|\s*sort -u", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

def norm(pattern):
    return re.sub(r"\s+", " ", pattern).strip()

bad = 0
if awk_block(gate) != awk_block(ver):
    print("FAIL: the gate and the verifier parse the install table differently")
    bad = 1
else:
    print("OK   install-table parser identical in gate and verifier")

for pat in (r"^[[:space:]]*defects-found:[[:space:]]*[0-9]+",
            r"^[[:space:]]*defects-fixed:[[:space:]]*[0-9]+",
            r"^[[:space:]]*changed:",
            r"^[[:space:]]*hunt: [a-z0-9-]+"):
    in_gate = any(norm(p) == norm(pat) for p in re.findall(r"grep -[a-zA-Z]+E?\s+'([^']+)'", gate))
    in_ver = any(norm(p) == norm(pat) for p in re.findall(r"grep -[a-zA-Z]+E?\s+'([^']+)'", ver))
    if in_gate != in_ver:
        print("FAIL: contract pattern %r present in gate=%s verifier=%s" % (pat, in_gate, in_ver))
        bad = 1
    else:
        print("OK   contract pattern %r in both" % pat)
sys.exit(bad)
PY

if [ "$FAIL" -ne 0 ]; then
  echo "WORKFLOW VALIDATION FAILED - do not push"
  exit 1
fi
echo "WORKFLOW VALIDATION PASSED"
