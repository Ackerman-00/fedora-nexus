#!/usr/bin/env python3
"""Tests for terra-ref.py's pin helpers and its mapping.

Run: python3 tools/test-terra-ref.py
"""
import importlib.util
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "terra_ref", os.path.join(here, "terra-ref.py"))
sys.modules["terra_ref"] = spec
terra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(terra)

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


check("version_key numeric order",
      terra.version_key("0.20.10") > terra.version_key("0.20.9"), True)
check("version_key text tail",
      terra.version_key("1.7.1") > terra.version_key("1.7.1^20261121git603ba85"),
      True)
check("versions_match exact", terra.versions_match("1.24.3b", "1.24.3b"), True)
check("versions_match suffix",
      terra.versions_match("1.24.3b", "1.24.3"), True)
check("versions_match different",
      terra.versions_match("0.22.1.1", "0.22.2.1"), False)

check("spec_pin version and commit",
      terra.spec_pin(open(terra.spec_path("umbriel-git"),
                          encoding="utf-8").read(), "umbriel-git")[1][:7],
      "3bb6616")
check("spec_pin forge version",
      terra.spec_pin(open(terra.spec_path("protonplus"),
                          encoding="utf-8").read(), "protonplus")[0]
      .startswith("0."), True)

for pkg in terra.TERRA:
    check("mapped spec exists: " + pkg, os.path.isfile(terra.spec_path(pkg)), True)

check("delta same commit", terra.delta(("1.0", "abc"), ("1.0", "abc")), "in-sync")
check("delta different commit",
      terra.delta(("1.0", "abc"), ("1.0", "def")), "diverged")
check("delta newer tag", terra.delta(("1.0", None), ("2.0", None)), "behind")

if FAILS:
    print("\n".join(FAILS))
    sys.exit(1)
print("terra-ref helpers OK")
