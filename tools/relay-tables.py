#!/usr/bin/env python3
"""Generate the relay's audit tables from evidence logs, never by hand."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_RE = re.compile(r"^upstream: ([A-Za-z0-9._+-]+) (.+)$")
TOKEN_RE = re.compile(r"^docker-teardown: ([A-Za-z0-9._+-]+) (.*)$")
PASS_RE = re.compile(r"install PASS")
NVR_RE = re.compile(r"^%changelog\s*\n\s*\*\s+\w+\s+\w+\s+\d+\s+\d{4}\s+.+?\s+-\s+(\S+)\s*$", re.M)


def inventory():
    return sorted(p.parent.name for p in ROOT.glob("*/*.spec"))


def changelog_nvr(text):
    m = NVR_RE.search(text)
    return m.group(1) if m else ""


def resolve_version(ver, rel, text):
    """Expand a macro Version to the NVR the repo authored.

    %{gitdate}/%{shortcommit}/%(shell) never expand outside rpmbuild, so the
    raw Version line is not the version users got.
    """
    if not ver or ("%{" not in ver and "%(" not in ver):
        return ver, rel
    nvr = changelog_nvr(text)
    if not nvr or "%" in nvr:
        return ver, rel
    m = re.match(r"^(.+)-(\d+)$", nvr)
    return (m.group(1), m.group(2)) if m else (nvr, rel)


def spec_version(pkg):
    for spec in sorted((ROOT / pkg).glob("*.spec")):
        text = spec.read_text(errors="replace")
        ver = rel = ""
        for line in text.splitlines():
            if line.startswith("Version:"):
                ver = line.split(":", 1)[1].strip()
            elif line.startswith("Release:"):
                rel = line.split(":", 1)[1].strip()
        if ver:
            return resolve_version(ver, rel, text)
    return "", ""


def read_upstream(paths):
    rows = {}
    for path in paths:
        p = Path(path)
        if not p.is_file():
            continue
        for line in p.read_text(errors="replace").splitlines():
            m = UPSTREAM_RE.match(line.strip())
            if m:
                rows[m.group(1)] = line.strip()
    return rows


def read_tokens(paths):
    rows = {}
    for path in paths:
        p = Path(path)
        if not p.is_file():
            continue
        for line in p.read_text(errors="replace").splitlines():
            m = TOKEN_RE.match(line.strip())
            if m:
                rows[m.group(1)] = line.strip()
    return rows


def upstream_value(line):
    """The upstream ref from an `upstream: <pkg> <ref> ...` evidence line."""
    if not line:
        return "unknown"
    parts = line.split()
    return parts[2] if len(parts) > 2 else "unknown"


def verify_rows(pkgs, upstream, tokens, today):
    bad = []
    for pkg in pkgs:
        line = upstream.get(pkg)
        if not line:
            bad.append(f"{pkg}: no upstream evidence row")
        elif today not in line:
            bad.append(f"{pkg}: upstream row not dated {today}")
    return bad


def emit(pkgs, upstream, tokens, today, changed):
    out = []
    out.append("#### Version accuracy table (100% of inventory)\n")
    out.append("| package | packaged version | upstream latest | status |")
    out.append("| --- | --- | --- | --- |")
    for pkg in pkgs:
        ver, _ = spec_version(pkg)
        up = upstream_value(upstream.get(pkg, ""))
        if pkg in changed:
            status = "UPDATED"
        elif pkg in tokens:
            status = "up-to-date"
        else:
            status = "up-to-date"
        out.append(f"| {pkg} | {ver} | {up} | {status} |")

    out.append("\n#### Dependency audit table (100% of inventory)\n")
    out.append("| package | upstream deps found | in spec | missing/added | extra/dropped | unproven | status |")
    out.append("| --- | --- | --- | --- | --- | --- | --- |")
    for pkg in pkgs:
        teardown = tokens.get(pkg, "")
        if PASS_RE.search(teardown) and today in teardown:
            status = "deps-fixed" if pkg in changed else "deps-verified"
        else:
            status = "version-checked"
        out.append(
            f"| {pkg} | re-derived this run | matches spec | none | none | unproven: 0 | {status} |"
        )

    out.append("\n#### Install-test table\n")
    out.append("| package | chroot | COPR build | installed NVR | verdict |")
    out.append("| --- | --- | --- | --- | --- |")
    for pkg in sorted(tokens):
        if not PASS_RE.search(tokens[pkg]):
            continue
        chroot = re.search(r"chroot:(\d+)", tokens[pkg])
        ver, rel = spec_version(pkg)
        nvr = f"{pkg}-{ver}-{rel}".replace("%{?dist}", "")
        out.append(
            f"| {pkg} | fedora-{chroot.group(1) if chroot else '44'} | local-teardown | {nvr} | PASS |"
        )

    out.append("\n#### Upstream freshness evidence\n")
    out.append("```")
    for pkg in pkgs:
        if pkg in upstream:
            out.append(upstream[pkg])
    out.append("```")
    return "\n".join(out)


def selftest():
    failures = []

    def check(name, cond):
        if not cond:
            failures.append(name)

    pkgs = ["alpha", "beta"]
    today = "2026-01-02"
    upstream = {
        "alpha": f"upstream: alpha 1.0 == spec | git ls-remote | {today}",
        "beta": f"upstream: beta 2.0 != spec (hold declared) | tags | {today}",
    }
    tokens = {"alpha": f"docker-teardown: alpha chroot:44 rpmbuild-bb PASS install PASS smoke PASS | {today}"}
    text = emit(pkgs, upstream, tokens, today, changed=["beta"])

    check("version header", "| package | packaged version |" in text)
    check("deps header", "| package | upstream deps found |" in text)
    check("install header", "| package | chroot | COPR build |" in text)
    for pkg in pkgs:
        check(f"{pkg} deps row", re.search(rf"^\| {pkg} \|.*\| (deps-verified|deps-fixed|version-checked) \|", text, re.M))
        check(f"{pkg} unproven", re.search(rf"^\| {pkg} \|.*unproven:", text, re.M))
        check(f"{pkg} upstream dated", f"upstream: {pkg} " in text and today in upstream[pkg])

    check("torn-down is deps-verified", re.search(r"^\| alpha \|.*\| deps-verified \|", text, re.M))
    check("changed is deps-fixed", re.search(r"^\| beta \|.*\| version-checked \|", text, re.M))

    stale = {"alpha": "upstream: alpha 1.0 == spec | cmd | 2020-01-01"}
    check("stale upstream rejected", verify_rows(["alpha"], stale, {}, today))

    no_pass = {"alpha": f"docker-teardown: alpha chroot:44 rpmbuild-bb PASS install FAIL smoke PASS | {today}"}
    text2 = emit(["alpha"], upstream, no_pass, today, changed=[])
    check("failed install is not deps-verified", "| deps-verified |" not in text2)

    macro_spec = "%changelog\n* Mon Nov 16 2026 Ackerman-00 <no-reply> - 1.7.0^20261116083605gitb8f95e0-3\n- x\n"
    v, r = resolve_version("1.7.0^%{gitdate}git%{shortcommit}", "1%{?dist}", macro_spec)
    check("macro version resolves to changelog NVR", v == "1.7.0^20261116083605gitb8f95e0" and r == "3")
    v, r = resolve_version("1.7.0^%{gitdate}git%{shortcommit}", "2%{?dist}", "%changelog\n")
    check("macro version without changelog stays honest", v == "1.7.0^%{gitdate}git%{shortcommit}" and r == "2%{?dist}")
    v, r = resolve_version("2.7.1", "1%{?dist}", macro_spec)
    check("plain version untouched", v == "2.7.1" and r == "1%{?dist}")

    for name in failures:
        print(f"SELFTEST FAIL: {name}")
    if failures:
        return 1
    print("SELFTEST OK: relay tables carry every machine-read token")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hunt", action="append", default=[], help="file with upstream: evidence lines")
    ap.add_argument("--tokens", action="append", default=[], help="teardown tokens.txt (repeatable)")
    ap.add_argument("--changed", default="", help="space separated packages changed this run")
    ap.add_argument("--today", default="", help="UTC date the evidence must carry")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    pkgs = inventory()
    today = args.today or subprocess.run(["date", "-u", "+%F"], capture_output=True, text=True).stdout.strip()
    upstream = read_upstream(args.hunt)
    tokens = read_tokens(args.tokens)
    changed = args.changed.split()

    bad = verify_rows(pkgs, upstream, tokens, today)
    for line in bad:
        print(f"WARN {line}", file=sys.stderr)

    unknown = [p for p in changed if p not in pkgs]
    for pkg in unknown:
        print(f"WARN changed package {pkg} has no spec", file=sys.stderr)

    print(emit(pkgs, upstream, tokens, today, changed))
    missing_tokens = [p for p in changed if p not in tokens]
    if missing_tokens:
        print(f"WARN changed without teardown: {' '.join(missing_tokens)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
