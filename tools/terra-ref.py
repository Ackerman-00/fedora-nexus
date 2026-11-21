#!/usr/bin/env python3
"""Print the relay-ready terra-ref line per priority package.

Terra (terrapkg/packages, branch frawhide) packages the same Wayland stack.
The comparison is read live: Terra's spec comes from the GitHub contents API
(token-safe), ours from the checkout. The delta is a claim about the pin, not
about quality; kept-improvements lists the BuildRequires Terra lacks.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hunt as H  # noqa: E402

REPO = "terrapkg/packages"
REF = "frawhide"

TERRA = {
    "umbriel-git": "anda/desktops/umbriel/nightly/umbriel-nightly.spec",
    "xdg-desktop-portal-umbriel-git":
        "anda/desktops/umbriel/xdg-desktop-portal-umbriel-nightly/"
        "xdg-desktop-portal-umbriel-nightly.spec",
    "noctalia-greeter": "anda/desktops/noctalia/greeter/noctalia-greeter.spec",
    "mangowm": "anda/desktops/mangowm/mangowm.spec",
    "helium-browser": "anda/apps/helium-browser-bin/helium-browser-bin.spec",
    "heroic-games-launcher":
        "anda/games/heroic-games-launcher/heroic-games-launcher.spec",
    "protonplus": "anda/games/protonplus/protonplus.spec",
    "zen-browser": "anda/apps/zen-browser/zen-browser.spec",
}


def gh(args, timeout=60):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          timeout=timeout)


def fetch(path):
    """Terra spec text, or None when the API does not serve it."""
    r = gh(["api", "repos/%s/contents/%s?ref=%s" % (REPO, path, REF),
            "--jq", ".content"])
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return base64.b64decode(r.stdout.strip()).decode("utf-8", "replace")
    except (ValueError, base64.binascii.Error):
        return None


def last_sha(path):
    r = gh(["api", "repos/%s/commits?path=%s&per_page=1" % (REPO, path),
            "--jq", ".[0].sha"])
    sha = r.stdout.strip()
    return sha[:8] if r.returncode == 0 and sha else "unknown"


def spec_path(pkg):
    """The package's own spec inside this checkout."""
    return os.path.join(H.ROOT, pkg, pkg + ".spec")


def version_key(v):
    """Sort key for rpm-ish versions; a ^snapshot sorts before its base."""
    base, caret, _ = v.partition("^")
    key = tuple((0, int(x)) if x.isdigit() else (1, x)
                for x in re.split(r"[._+~-]", base) if x)
    return (key, 0 if caret else 1)


def versions_match(a, b):
    """True when one version is the other with a build or letter tail."""
    def norm(v):
        v = re.sub(r"[+~^].*$", "", v)
        return re.sub(r"([0-9])[a-z]$", r"\1", v)
    a, b = norm(a), norm(b)
    return a == b or a.startswith(b + ".") or b.startswith(a + ".")


def spec_pin(text, pkg=None):
    """(version, commit) as the spec declares them; either may be None."""
    ver = re.search(r"^Version:\s*(\S+)", text, re.M)
    com = re.search(r"^%global\s+commit\s+(\S+)", text, re.M)
    value = ver.group(1) if ver else None
    if value and "%{" in value and pkg:
        value = H.resolve_version(spec_path(pkg), value)
    if value and "%{" in value:
        tag = re.search(r"^%global\s+tag\s+(\S+)", text, re.M)
        if tag:
            value = tag.group(1).lstrip("v")
    return (value, com.group(1) if com else None)


def brs(text):
    return {m.group(1).strip() for m in
            re.finditer(r"^BuildRequires:\s*(.+?)\s*$", text, re.M)}


def delta(ours, theirs):
    """ahead/behind/in-sync from the pins the two specs carry."""
    over, ocom = ours
    tver, tcom = theirs
    if ocom and tcom:
        if ocom == tcom:
            return "in-sync"
        return "diverged"
    if over and tver:
        if over == tver:
            return "in-sync"
        if versions_match(over, tver):
            return "in-sync"
        return "behind" if version_key(tver) > version_key(over) else "ahead"
    return "unknown"


def line(pkg, ours_text, terra_text, sha):
    ours = spec_pin(ours_text, pkg)
    pin = ours[1][:8] if ours[1] else (ours[0] or "?")
    if terra_text is None:
        return ("terra-ref: n/a (Terra spec not served for this package) | "
                "ours: %s | delta: n/a | kept-improvements: n/a" % pin)
    theirs = spec_pin(terra_text)
    extra = sorted(brs(ours_text) - brs(terra_text))
    kept = ", ".join(extra[:4]) + (" ..." if len(extra) > 4 else "")
    return ("terra-ref: %s@%s | ours: %s | delta: %s | "
            "kept-improvements: %s" % (TERRA[pkg], sha, pin,
                                       delta(ours, theirs), kept or "none"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pkgs", nargs="*", help="default: every mapped package")
    ap.add_argument("--offline", action="store_true",
                    help="skip the network and print the mapping only")
    a = ap.parse_args()
    pkgs = a.pkgs or list(TERRA)
    for pkg in pkgs:
        if pkg == "wlroots":
            print("terra-ref: n/a (gitlab-forge) | ours: %s | delta: n/a | "
                  "kept-improvements: n/a" % spec_pin(
                      open(spec_path(pkg), encoding="utf-8").read())[0])
            continue
        path = TERRA.get(pkg)
        if not path:
            print("terra-ref: n/a (no Terra mapping) | ours: ? | "
                  "delta: n/a | kept-improvements: n/a")
            continue
        ours_text = open(spec_path(pkg), encoding="utf-8").read()
        if a.offline:
            print("terra-ref: %s@offline | ours: %s | delta: n/a | "
                  "kept-improvements: n/a"
                  % (path, spec_pin(ours_text, pkg)[1][:8]
                     if spec_pin(ours_text, pkg)[1]
                     else spec_pin(ours_text, pkg)[0]))
            continue
        print(line(pkg, ours_text, fetch(path), last_sha(path)))
        time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
