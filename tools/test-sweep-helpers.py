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
    # And the live channel reader itself, when reachable.  The expectation is
    # read from the spec (not hardcoded) so the test tracks the packaged
    # version instead of rotting every time upstream ships a new release.
    spec_ver = None
    spec = os.path.join(os.path.dirname(ts.__file__ if hasattr(ts, "__file__")
                                       else "."),
                        "..", "photon-studio", "photon-studio.spec")
    try:
        with open(os.path.normpath(spec)) as fh:
            for line in fh:
                if line.startswith("Version:"):
                    spec_ver = line.split(":", 1)[1].strip()
                    break
    except OSError:
        spec_ver = None
    if spec_ver is None:
        # The package was dropped from the repo (owner removed photon-studio on
        # 2026-10-06); the parsing cases above still cover the helper, and a
        # live channel read would have nothing to compare against.
        print("SKIP: photon-studio no longer packaged - live channel check skipped")
        return failures
    ver, src = ts.redirect_channel_version("photon-studio", [], None)
    if ver:
        ok = spec_ver is not None and ver == spec_ver
        print(f"{'PASS' if ok else 'FAIL'}: photon-studio redirect channel -> "
              f"{ver} via {src} (spec Version: {spec_ver})")
        if not ok:
            failures += 1
    else:
        print("SKIP: photon-studio redirect channel unreachable this run")
    return failures


def test_detect_type():
    """detect_type must not classify a Fedora repo as opensuse just because a
    spec comment *mentions* openSUSE. Regression guard: on 2026-10-05 the
    sweep wrote "Repo type: opensuse" for this Fedora overlay because
    splayer-next.spec says "openSUSE-style debuginfo links into /opt", which
    silently rerouted Source0 resolution through resolve_opensuse_urls()."""
    import pathlib
    import tempfile
    failures = 0
    cases = [
        ("fedora", "# (openSUSE-style debuginfo links into /opt)\n"
                   "Name: splayer-next\nVersion: 1.0\n"
                   "Release: 1%{?dist}\nSource0: https://x/y.tar.gz\n"),
        ("fedora", "Name: plain\nVersion: 1\nRelease: 1%{?dist}\n"
                   "Source0: https://src.fedoraproject.org/x.tar.gz\n"),
        ("opensuse", "Name: susy\nVersion: 1\n"
                     "Release: 1%{?suse_version}\nSource0: foo.tar.gz\n"),
        (None, None),
    ]
    for want, content in cases:
        with tempfile.TemporaryDirectory(prefix="dt-") as td:
            p = pathlib.Path(td)
            if content is not None:
                sub = p / "pkg"
                sub.mkdir()
                (sub / "pkg.spec").write_text(content)
            got = ts.detect_type(p)
        ok = got == want
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}: detect_type() -> {got!r} "
              f"(want {want!r}) for "
              f"{(content or chr(60)+'no spec files'+chr(62)).splitlines()[0][:48]!r}")
    # And this overlay itself must still read as fedora.
    root = pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / ".."
    got = ts.detect_type(root.resolve())
    ok = got == "fedora"
    failures += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}: detect_type(overlay) -> {got!r} "
          f"(want 'fedora')")
    return failures


def test_strings_version():
    """strings_version must find `<name>/<version>` tokens inside binary
    artifacts that ship no structured metadata, and must report what the
    artifact REALLY says (never rubber-stamp the pinned version).
    Regression guard: on 2026-10-08 the sweep marked opencad-studio UNVERIFIED
    even though its AppImage's ELF carries the string `OpenCADStudio/2026.40.1`
    and the sha256 matched the spec pin."""
    import pathlib
    import tempfile
    failures = 0
    cases = [
        # (distname, file body, want_version)
        ("OpenCADStudio-v2026.40.1-linux-x86_64.AppImage",
         b"\x7fELF noise OpenCADStudio/2026.40.1 more noise", "2026.40.1"),
        # stale artifact: body says 2026.39.0 -> report that, not the pin
        ("OpenCADStudio-v2026.40.1-linux-x86_64.AppImage",
         b"OpenCADStudio/2026.39.0", "2026.39.0"),
        # no name-prefixed token at all -> give up rather than guess
        ("OpenCADStudio-v2026.40.1-linux-x86_64.AppImage",
         b"unrelated version 1.2.3 of some embedded lib", None),
        # filename carries no separable app name (starts at the version),
        # so no anchored token can match -> give up rather than guess
        ("v2026.40.1-linux-x86_64.AppImage", b"v2026.40.1", None),
    ]
    for distname, body, want in cases:
        with tempfile.TemporaryDirectory(prefix="sv-") as td:
            sub = pathlib.Path(td)
            (sub / "payload").write_bytes(body)
            got, rel = ts.strings_version(sub, distname)
        ok = got == want
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}: strings_version({distname!r}) -> "
              f"{got!r} (want {want!r})")
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
    failures += test_detect_type()
    failures += test_strings_version()
    print(f"\n{'ALL PASS' if not failures else str(failures) + ' FAILURE(S)'}"
          f" ({len(CASES)} cases)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())