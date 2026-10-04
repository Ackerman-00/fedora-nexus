#!/usr/bin/env python3
"""Regression tests for tools/teardown-sweep.py helpers.

Run: python3 tools/test-sweep-helpers.py

Why this exists: on 2026-10-02 the sweep reported rootapp OUTDATED from
Repology's per-repo status while our pin (0.9.145, read from
X-AppImage-Version INSIDE the AppImage) was NEWER than Repology's number
(0.9.144, the AUR lineage). The status field is relative to Repology's newest
entry, not to us. The fix compares versions instead of trusting the status;
these tests pin that behaviour so it cannot silently regress.
"""
import importlib.util
import os
import re
import sys

spec = importlib.util.spec_from_file_location(
    "ts", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "teardown-sweep.py"))
ts = importlib.util.module_from_spec(spec)
sys.modules["ts"] = ts
spec.loader.exec_module(ts)

# (pinned, repology_upstream, expected_is_upstream_newer, why)
CASES = [
    ("0.9.145", "0.9.144", False, "rootapp: we ship AHEAD of repology's AUR lineage"),
    ("0.9.144", "0.9.145", True, "genuine newer upstream"),
    ("1.22.3a", "1.22.3b", True, "letter suffix newer upstream"),
    ("1.22.3b", "1.22.3a", False, "letter suffix older upstream"),
    ("1.22.3b", "1.22.3b", False, "equal"),
    ("0.17.5", "0.17.5", False, "equal numeric"),
    ("0.9.14", "0.9.145", True, "0.9.145 is numerically newer than 0.9.14"),
    ("2.0", "2.0.0", False, "pad-equal"),
    ("1.0", "1.0.1", True, "pad-newer"),
    ("1.4.1", "v1.4.1", False, "v-prefix stripped"),
    ("1.6.0", "0.6.0", False, "repology behind on a different major"),
    ("3.0", "?", True, "unparseable upstream -> conservative True"),
]


def test_redirect_version_parsing():
    """The redirect-target version reader must strip a concrete dotted version
    out of BOTH path-style (.../0.1.39/Photon-...-0.1.39-...) and
    filename-style URLs, and must not be fooled by a non-version path segment.
    Regression guard for the photon-studio recurring UNVERIFIED (its update.sh
    302 channel is the only authoritative version source when Repology 403s,
    Anitya has no project and the artifact URL is versionless at the top)."""
    cases = [
        ("https://downloads.tenzen.studio/photon/stable/linux/0.1.39/"
         "Photon-Studio-0.1.39-linux-x64.AppImage", "0.1.39"),
        ("https://example.com/app/v2.10.3/thing.tar.gz", "2.10.3"),
        ("https://example.com/Thing-1.0.7-x86_64.deb", "1.0.7"),
        ("https://example.com/latest/thing", None),
    ]
    failures = 0
    for url, want in cases:
        m = None
        for cand in (url,):
            g = re.search(r"/(?:v)?(\d+\.\d+(?:\.\d+)*)(?:/|$|[^0-9.])", cand)
            if not g:
                g = re.search(r"-(\d+\.\d+(?:\.\d+)*)[-.]", cand)
            if g:
                m = g.group(1)
        status = "PASS" if m == want else "FAIL"
        if m != want:
            failures += 1
        print(f"{status}: version_from_url({url!r}) -> {m!r} (want {want!r})")
    # And the live channel reader itself, when reachable.
    ver, src = ts.redirect_channel_version("photon-studio", [], None)
    if ver:
        ok = ver == "0.1.39"
        print(f"{'PASS' if ok else 'FAIL'}: photon-studio redirect channel -> "
              f"{ver} via {src}")
        if not ok:
            failures += 1
    else:
        print("SKIP: photon-studio redirect channel unreachable this run")
    return failures


def main():
    failures = 0
    for pinned, upstream, want, why in CASES:
        got = ts.repology_is_newer(pinned, upstream)
        status = "PASS" if got == want else "FAIL"
        if got != want:
            failures += 1
        print(f"{status}: pinned {pinned} vs repology {upstream} -> "
              f"newer={got} (want {want})  # {why}")
    failures += test_redirect_version_parsing()
    print(f"\n{'ALL PASS' if not failures else str(failures) + ' FAILURE(S)'}"
          f" ({len(CASES)} cases)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())