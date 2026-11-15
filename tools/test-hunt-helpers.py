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

import tempfile as _tf
import calendar as _cal
import time as _time
_want = _cal.timegm(_time.strptime("20261113162906", "%Y%m%d%H%M%S"))
with _tf.TemporaryDirectory() as _d:
    _p = os.path.join(_d, "p.spec")
    open(_p, "w").write("Name: p\n%global gitdate 20261113162906\nVersion: 1\n")
    _stamp = hunt.pinned_epoch(_p)
check("14-digit gitdate keeps the hour", _stamp, _want)
with _tf.TemporaryDirectory() as _d:
    _p = os.path.join(_d, "p.spec")
    open(_p, "w").write("Name: p\n%global gitdate 20261113\nVersion: 1\n")
    _stamp = hunt.pinned_epoch(_p)
check("8-digit gitdate parses at midnight", _stamp, _cal.timegm(_time.strptime("20261113", "%Y%m%d")))
with _tf.TemporaryDirectory() as _d:
    _p = os.path.join(_d, "p.spec")
    open(_p, "w").write("Name: p\nVersion: 0.0.0\nRelease: 31.20261115giteb909f8\n")
    _stamp = hunt.pin_stamp(_p)
check("date-only Release stamp is readable", _stamp, "20261115")
with _tf.TemporaryDirectory() as _d:
    _p = os.path.join(_d, "p.spec")
    open(_p, "w").write("Name: p\nVersion: 1.0\nRelease: 3\n")
    _stamp = hunt.pin_stamp(_p)
check("tag-pinned spec carries no snapshot stamp", _stamp, "")

_rx = hunt.asset_regex("OpenClaw-%{version}-amd64.deb")
check("asset regex accepts the release asset", bool(_rx.match("OpenClaw-2026.11.2-amd64.deb")), True)
check("asset regex rejects another platform", bool(_rx.match("OpenClaw-2026.11.3-arm64.dmg")), False)
check("asset regex handles a literal version", bool(hunt.asset_regex(
    "omnirush-linux-amd64-3.8.4.deb").match("omnirush-linux-amd64-3.8.4.deb")), True)

class _Resp:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

_calls = {"n": 0}
_real_urlopen = hunt.urllib.request.urlopen

def _flaky(req, timeout=None):
    _calls["n"] += 1
    if _calls["n"] < 3:
        raise OSError("transient")
    return _Resp(b"<html>ok</html>")

hunt.urllib.request.urlopen = _flaky
check("get_text retries a transient failure", hunt.get_text("https://example.invalid/"), "<html>ok</html>")
check("get_text retried three times", _calls["n"], 3)

_calls["n"] = 0

def _dead(req, timeout=None):
    _calls["n"] += 1
    raise OSError("down")

hunt.urllib.request.urlopen = _dead
check("get_text reports empty after every attempt fails", hunt.get_text("https://example.invalid/"), "")
check("get_text stops at the attempt cap", _calls["n"], 3)
hunt.urllib.request.urlopen = _real_urlopen

with _tf.TemporaryDirectory() as _d:
    _p = os.path.join(_d, "p.spec")
    open(_p, "w").write("Name: p\n%global commit abcdef1234567890\nVersion: 0.0.0\n")
    _label = hunt.pinned_label(_p, "0.0.0")
check("pinned label reports the pinned commit", _label, "abcdef1")
with _tf.TemporaryDirectory() as _d:
    _p = os.path.join(_d, "p.spec")
    open(_p, "w").write("Name: p\nVersion: 1.2.3\n")
    _label = hunt.pinned_label(_p, "1.2.3")
check("pinned label falls back to the version", _label, "1.2.3")

check("changelog NVR exact match",
      hunt.nvr_matches("* Sun Nov 15 2026 Ackerman-00 <no-reply> - 2.7.2-2", "2.7.2", "2"), True)
check("changelog NVR one release behind",
      hunt.nvr_matches("* Sun Nov 15 2026 Ackerman-00 <no-reply> - 2.7.2-1", "2.7.2", "2"), False)
check("changelog NVR epoch prefix",
      hunt.nvr_matches("* Sun Nov 15 2026 Ackerman-00 <no-reply> - 2:1.24.2b-2", "1.24.2b", "2", "2"), True)
check("changelog NVR epoch implied by version digits",
      hunt.nvr_matches("* Sun Nov 15 2026 Ackerman-00 <no-reply> - 2.7.2-1", "2.7.2", "2", "0"), False)

TAGGED_SPEC = "Name: p\nSource0: https://github.com/o/r/archive/refs/tags/v1.tar.gz\n"
GIT_SPEC = "Name: p\nSource0: %{url}/archive/%{commit}/p-%{shortcommit}.tar.gz\n"
check("updater: broken shebang flagged",
      len(hunt.updater_findings("#!/usr/bin/env bashset -u\necho nothing\n", TAGGED_SPEC)), 2)
check("updater: stub on a tag-tracked spec",
      hunt.updater_findings("#!/bin/bash\necho manual\n", TAGGED_SPEC)[0][:12].strip(),
      "update.sh is")
check("updater: stub on a commit-pinned spec is legal",
      hunt.updater_findings("#!/bin/bash\necho manual\n", GIT_SPEC), [])
check("updater: real updater is clean",
      hunt.updater_findings("#!/bin/bash\nset -u\nsed -i \"s/^Version:.*/Version: 2/\" p.spec\n"
                            "curl -sL https://api.github.com/repos/o/r/releases/latest\n", TAGGED_SPEC), [])

if FAILS:
    for f in FAILS:
        print("FAIL " + f)
    sys.exit(1)
print("PASS: hunt chroot-docs helpers (%d readme cases)" % len(READMES))
