#!/usr/bin/env python3
"""Tests for hunt.py's README/chroot parity helpers.

Run: python3 tools/test-hunt-helpers.py
"""
import importlib.util
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hunt", os.path.join(here, "hunt.py"))
hunt = importlib.util.module_from_spec(spec)
sys.modules["hunt"] = hunt
spec.loader.exec_module(hunt)

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


READMES = [
    ("> **Supported releases:** Fedora 43, 44, 45 and Rawhide (x86_64), exactly the\n"
     "> four chroots this COPR builds.\n>\n", ({43, 44, 45}, True)),
    ("> **Supported releases:** Fedora 44 and Rawhide (x86_64).\n>\n", ({44}, True)),
    ("> **Supported releases:** Fedora 43.\n>\n", ({43}, False)),
    ("no support line here\n", (None, None)),
]
for text, want in READMES:
    check("parse %r" % text[:40], hunt.supported_releases(text), want)

# In sync: no findings.
check("in-sync", hunt.chroot_doc_findings({43, 44, 45}, True, {43, 44, 45}, True), [])
# Drift each way must be detected, otherwise the check cannot fail.
check("undocumented chroot",
      [f[1] for f in hunt.chroot_doc_findings({43, 44, 45}, True, {44, 45}, True)],
      ["F43 chroot builds but README does not list it"])
check("phantom release",
      [f[1] for f in hunt.chroot_doc_findings({44}, True, {43, 44}, True)],
      ["README lists F43 but no chroot builds it"])
check("rawhide drift",
      [f[1] for f in hunt.chroot_doc_findings({44}, False, {44}, True)],
      ["rawhide chroot=False, README rawhide=True"])

if FAILS:
    for f in FAILS:
        print("FAIL " + f)
    sys.exit(1)
print("PASS: hunt chroot-docs helpers (%d readme cases)" % len(READMES))
