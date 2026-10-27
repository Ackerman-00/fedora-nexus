#!/usr/bin/env bash
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
if python3 tools/workflow-valid.py .github/workflows/*.yml; then
  :
else
  FAIL=1
fi

echo "== gate and verifier agree on the contract =="
python3 - <<'PY' || FAIL=1
import re, sys

def read(p):
    return open(p, encoding="utf-8", errors="replace").read()

gate = read(".github/workflows/opencode-schedule.yml")
ver = read("tools/verify-fedora.sh")

def norm(pattern):
    return re.sub(r"\s+", " ", pattern).strip()

def install_parser(text):
    """The install-table parser: the awk block that knows EXTERNAL."""
    blocks = re.findall(r"awk -F'\|' '(.*?)'\s*\|\s*sort -u", text, re.S)
    for b in blocks:
        if "EXTERNAL" in b:
            return norm(b)
    return ""

def grep_patterns(text):
    """Every grep pattern, whatever flags or quote style precede it."""
    out = set()
    for m in re.finditer(r"grep(?:\s+-[a-zA-Z0-9]+)*\s+(?:'([^']*)'|\"([^\"]*)\")", text):
        out.add(norm(m.group(1) if m.group(1) is not None else m.group(2)))
    return out

bad = 0
g_parser, v_parser = install_parser(gate), install_parser(ver)
if not g_parser or not v_parser:
    print("FAIL: the install-table parser was not found (gate=%d bytes, verifier=%d bytes)"
          % (len(g_parser), len(v_parser)))
    bad = 1
elif g_parser != v_parser:
    print("FAIL: the gate and the verifier parse the install table differently")
    bad = 1
else:
    print("OK   install-table parser identical in gate and verifier (%d bytes)" % len(g_parser))

gp, vp = grep_patterns(gate), grep_patterns(ver)
for pat in (r"^[[:space:]]*defects-found:[[:space:]]*[0-9]+",
            r"^[[:space:]]*defects-fixed:[[:space:]]*[0-9]+",
            r"^[[:space:]]*changed:",
            r"^[[:space:]]*hunt: [a-z0-9-]+"):
    in_gate = norm(pat) in gp
    in_ver = norm(pat) in vp
    if in_gate and in_ver:
        print("OK   contract pattern %r in both" % pat)
    else:
        print("FAIL: contract pattern %r present in gate=%s verifier=%s (both required)"
              % (pat, in_gate, in_ver))
        bad = 1

gap_pat = r"GAP: external.*$ext_pkg"
in_gate = norm(gap_pat) in gp
in_ver = norm(gap_pat) in vp
if in_gate and in_ver:
    print("OK   the EXTERNAL verdict needs a GAP: external line, in both")
else:
    print("FAIL: the EXTERNAL/GAP rule present in gate=%s verifier=%s (both required)"
          % (in_gate, in_ver))
    bad = 1

g_tbl = set(norm(p) for p in gp if "install-test table" in p or "COPR build" in p)
v_tbl = set(norm(p) for p in vp if "install-test table" in p or "COPR build" in p)
if not g_tbl or not v_tbl:
    print("FAIL: the install-test table rule was not found (gate=%d, verifier=%d)" % (len(g_tbl), len(v_tbl)))
    bad = 1
elif g_tbl != v_tbl:
    print("FAIL: the gate and the verifier disagree on the install-test table rule")
    print("      gate:     %s" % sorted(g_tbl))
    print("      verifier: %s" % sorted(v_tbl))
    bad = 1
else:
    print("OK   install-test table rule identical in gate and verifier")

import yaml as _yaml
try:
    _wf = _yaml.safe_load(open(".github/workflows/opencode-schedule.yml", encoding="utf-8"))
    _prompt = ""
    for _job in (_wf.get("jobs") or {}).values():
        for _st in _job.get("steps", []):
            _env = _st.get("env") or {}
            if "PROMPT" in _env:
                _prompt = _env["PROMPT"]
    if not _prompt:
        print("FAIL: the scheduler PROMPT was not found in the workflow")
        bad = 1
    else:
        for word in ("PASS", "FAIL", "EXTERNAL"):
            if word not in _prompt:
                print("FAIL: the PROMPT never mentions the verdict word %r" % word)
                bad = 1
            else:
                print("OK   the PROMPT names the verdict word %r" % word)
except Exception as exc:
    print("FAIL: could not read the scheduler PROMPT: %s" % exc)
    bad = 1
sys.exit(bad)
PY

if [ "$FAIL" -ne 0 ]; then
  echo "WORKFLOW VALIDATION FAILED - do not push"
  exit 1
fi
echo "WORKFLOW VALIDATION PASSED"
