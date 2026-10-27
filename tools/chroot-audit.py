#!/usr/bin/env python3
"""Audit the published repodata: every spec must carry its version in every chroot.

`build/list` rows cannot prove chroot coverage (a failed task hides, and one build
row only lists that build's chroots), so this reads each chroot's primary.xml.
Exit 0 = every package present with the spec's version in every chroot.
"""
import glob
import gzip
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = os.environ.get("COPR_OWNER", "ackerman")
PROJECT = os.environ.get("COPR_PROJECT", "nexus")
BASE = "https://download.copr.fedorainfracloud.org/results/%s/%s/%s/repodata/" % (OWNER, PROJECT, "%s")


def chroots():
    out = subprocess.run(["curl", "-sL", "--max-time", "60",
                          "https://copr.fedorainfracloud.org/api_3/project?ownername=%s&projectname=%s"
                          % (OWNER, PROJECT)], capture_output=True, text=True).stdout
    names = re.findall(r'"chroot_repos"\s*:\s*\{([^}]*)\}', out)
    if not names:
        return []
    return sorted(set(re.findall(r'"([a-z0-9_\-x86]+)"\s*:', names[0])))


def spec_nvrs():
    """{rpm name: version} for every spec, with rpm macros expanded.

    Specs carry %{commit}/%{gitdate} style versions, so the text in the spec is not
    comparable with a published NVR - only the expanded one is.
    """
    script = (
        "cd /srv\n"
        "for s in $(find . -mindepth 2 -maxdepth 2 -name '*.spec' | sort); do\n"
        "  rpmspec -q --srpm --qf '%{NAME}|%{VERSION}|%{RELEASE}\\n' \"$s\" 2>/dev/null | head -1\n"
        "done\n")
    def run_host():
        return subprocess.run(["bash", "-s"], input=script, cwd=ROOT,
                              capture_output=True, text=True).stdout

    def run_docker():
        return subprocess.run(
            ["docker", "run", "--rm", "-i", "-v", ROOT + ":/srv:ro",
             "registry.fedoraproject.org/fedora:44", "bash", "-lc",
             "dnf -y -q --setopt=gpgcheck=0 install rpm-build go-srpm-macros forge-srpm-macros "
             ">/dev/null 2>&1; bash -s"],
            input=script, capture_output=True, text=True).stdout

    out = ""
    if subprocess.run(["bash", "-lc", "command -v rpmspec"], capture_output=True).returncode == 0:
        out = run_host()
    if out.count("|") < 2 * len(glob.glob(os.path.join(ROOT, "*", "*.spec"))):
        out = run_docker()
    nv = {}
    for line in out.splitlines():
        if line.count("|") == 2:
            n, v, _r = line.split("|")
            nv[n] = v
    return nv


def primary(ch):
    md = subprocess.run(["curl", "-sL", "--max-time", "60", BASE % ch + "repomd.xml"],
                        capture_output=True, text=True).stdout
    m = re.search(r"repodata/[a-z0-9]+-primary\.xml\.gz", md)
    if not m:
        return {}
    blob = subprocess.run(["curl", "-sL", "--max-time", "180", BASE % ch + m.group(0).split("/", 1)[1]],
                          capture_output=True).stdout
    try:
        x = gzip.decompress(blob).decode("utf-8", "ignore")
    except OSError:
        return {}
    rows = re.findall(r'<name>([^<]+)</name>\s*<arch>[^<]+</arch>\s*'
                      r'<version epoch="[^"]*" ver="([^"]+)" rel="([^"]+)"', x)
    out = {}
    for n, v, r in rows:
        out.setdefault(n, set()).add(v)
    return out


def main():
    specs = sorted(glob.glob(os.path.join(ROOT, "*", "*.spec")))
    if not specs:
        print("no specs")
        return 2
    chs = chroots()
    if not chs:
        print("could not read the project's chroot list")
        return 2
    meta = spec_nvrs()
    if not meta:
        print("could not expand the specs' versions")
        return 2
    bad = 0
    for ch in chs:
        pub = primary(ch)
        miss = []
        for pkg, ver in sorted(meta.items()):
            if pkg not in pub:
                miss.append("%s: absent" % pkg)
            elif ver and ver not in pub[pkg]:
                miss.append("%s: spec %s, repo %s" % (pkg, ver, ",".join(sorted(pub[pkg]))[:60]))
        print("%-24s %3d names, %d spec(s) not at the spec version" % (ch, len(pub), len(miss)))
        for m in miss:
            print("   ", m)
        bad += len(miss)
    print("%d chroot x package checks, %d mismatch(es)" % (len(chs) * len(meta), bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
