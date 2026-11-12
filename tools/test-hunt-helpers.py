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
    ("> **Supported releases:** Fedora 43, 44, 45 and Rawhide (x86_64). Fedora 45 is\n"
     "> current stable; Rawhide is Fedora 46 (`fedora-release-46-0.1`).\n>\n",
     ({43, 44, 45}, True)),
    ("> **Supported releases:** Fedora 44 and Rawhide (x86_64). Rawhide is Fedora 45.\n>\n",
     ({44}, True)),
]
for text, want in READMES:
    check("parse %r" % text[:40], hunt.supported_releases(text), want)

check("in-sync", hunt.chroot_doc_findings({43, 44, 45}, True, {43, 44, 45}, True), [])
check("undocumented chroot",
      [f[1] for f in hunt.chroot_doc_findings({43, 44, 45}, True, {44, 45}, True)],
      ["F43 chroot builds but README does not list it"])
check("phantom release",
      [f[1] for f in hunt.chroot_doc_findings({44}, True, {43, 44}, True)],
      ["README lists F43 but no chroot builds it"])
check("rawhide drift",
      [f[1] for f in hunt.chroot_doc_findings({44}, False, {44}, True)],
      ["rawhide chroot=False, README rawhide=True"])

check("hold detected", hunt.live_hold_reason("%global live_hold_reason upstream deleted lang/gjs in 9b67eb5\n"), "upstream deleted lang/gjs in 9b67eb5")
check("hold absent", hunt.live_hold_reason("%global commit abc\n"), None)
check("hold case-insensitive-flag, spaced", hunt.live_hold_reason("%GLOBAL  live_hold_reason   spaced out reason  \n"), "spaced out reason")

check("feed url", hunt.feed_url_from_update_sh('FEED="https://download.example/x/latest-linux.yml"\n'),
      "https://download.example/x/latest-linux.yml")
check("feed unquoted", hunt.feed_url_from_update_sh("FEED=https://a/b/latest.yaml\n"), "https://a/b/latest.yaml")
check("feed non-yml", hunt.feed_url_from_update_sh('FEED="https://a/b.json"\n'), None)
check("feed absent", hunt.feed_url_from_update_sh("SPEC_FILE=x.spec\n"), None)

check("in-flight build is not settled", hunt.build_settled("running"), False)
check("pending build is not settled", hunt.build_settled("pending"), False)
check("succeeded build is settled", hunt.build_settled("succeeded"), True)
check("failed build is settled, so it is reported", hunt.build_settled("failed"), True)

if FAILS:
    for f in FAILS:
        print("FAIL " + f)
    sys.exit(1)
print("PASS: hunt chroot-docs helpers (%d readme cases)" % len(READMES))
