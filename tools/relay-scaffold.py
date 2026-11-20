#!/usr/bin/env python3
"""Build the mechanical relay tables from live data.

Rows are derived here; verdicts are not. A package lands in
`deps-verified` only when its name is passed with --verified, which the
agent may do only after it ran a same-run container teardown.
"""
import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hunt as H  # noqa: E402


def changelog_version(sp):
    """The version this spec last shipped, read from its newest NVR.

    A Version field built from shell or forge macros (%{fileref}) does not
    expand outside rpmbuild, and a half-expanded cell reads as a wrong
    version. The changelog NVR is the value the repo authored and COPR built.
    """
    txt = open(sp, encoding="utf-8", errors="replace").read()
    m = re.search(r"^%changelog\s*\n\s*\*\s+\w+\s+\w+\s+\d+\s+\d{4}\s+.+?\s+-\s+(\S+)\s*$",
                  txt, re.M)
    if not m:
        return None
    nvr = m.group(1)
    if "%{" in nvr:
        return None
    return re.sub(r"-\d+$", "", nvr)


def version_table():
    rows = ["| package | packaged version | upstream latest | status |",
            "| --- | --- | --- | --- |"]
    for sp in H.specs():
        pkg = os.path.basename(os.path.dirname(sp))
        ver = changelog_version(sp) or H.strip_packaging(
            H.resolve_version(sp, H.spec_field(sp, "Version")).lstrip("v"))
        _p, ref, ok, _cmd, err = H.probe_safe(sp)
        if ok is None:
            rows.append("| %s | %s | unprobed (%s) | needs-build |" % (pkg, ver, err))
        elif ok is True:
            rows.append("| %s | %s | %s | up-to-date |" % (pkg, ver, ref))
        elif ok == "held":
            rows.append("| %s | %s | %s | held (live_hold_reason) |" % (pkg, ver, ref))
        elif ok == "cadence":
            rows.append("| %s | %s | %s | held (updater cadence) |" % (pkg, ver, ref))
        else:
            rows.append("| %s | %s | %s | needs-build |" % (pkg, ver, ref))
    return "\n".join(rows)


def upstream_rows():
    """Relay-ready live-check row per package: what was probed and when."""
    today = time.strftime("%Y-%m-%d", time.gmtime())
    rows = []
    for sp in H.specs():
        pkg, ref, ok, cmd, err = H.probe_safe(sp)
        if ok is True:
            state = "%s == spec" % ref
        elif ok is False:
            state = "%s != spec (behind)" % ref
        elif ok == "held":
            state = "%s held (live_hold_reason)" % ref
        elif ok == "cadence":
            state = "%s held (updater cadence)" % ref
        else:
            state = "unprobed (%s)" % (err or "no feed")
        rows.append("upstream: %s %s | %s | %s" % (pkg, state, cmd or "no probe", today))
    return "\n".join(rows)


def dep_table(verified, fixed, notes):
    rows = ["| package | upstream deps found | in spec | missing | extra/dropped | unproven | status |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for sp in H.specs():
        pkg = os.path.basename(os.path.dirname(sp))
        txt = open(sp, encoding="utf-8", errors="replace").read()
        nbr = len([l for l in txt.splitlines() if l.startswith("BuildRequires")])
        if pkg in notes:
            rows.append(notes[pkg])
            continue
        if pkg in verified:
            status = "deps-fixed" if pkg in fixed else "deps-verified"
            rows.append("| %s | build files of the pinned Source0, consumed by this run's "
                        "container build | %d BuildRequires | none: builddep resolved every "
                        "one and rpmbuild -bb + install PASS (smoke where a binary ships) | unused-BR rot not "
                        "re-derived (build proof only) | unproven: 0 missing (a missing "
                        "BR cannot compile); unused-BR rot unproven on extras | %s |" % (pkg, nbr, status))
        else:
            rows.append("| %s | Source0 artifact (version-checked only) | %d BuildRequires | none found | n/a "
                        "| unproven: dependency list not re-derived this run (outside the "
                        "re-tear slice); version proven against this run's upstream row | version-checked |" % (pkg, nbr))
    return "\n".join(rows)


def install_table(rows_paths):
    """Install-test rows from every install-sweep rows.txt, with the COPR build id.

    rows.txt is the sweep's own log: pkg|chroot|nvr|smoke|verdict|why. The build
    id comes from COPR so a row can be traced to the build users download. One
    sweep per chroot means the caller passes several files.
    """
    builds = {name: v[3] for name, v in H.newest_builds().items()}
    out = ["| package | COPR build | chroot | installed NVR | verdict |",
           "| --- | --- | --- | --- | --- |"]
    seen = {}
    for rows_path in rows_paths:
        for line in open(rows_path, encoding="utf-8"):
            parts = line.rstrip("\n").split("|")
            if len(parts) < 5:
                continue
            # a smoke command may carry a pipe; the last two fields are fixed
            head, verdict = line.rstrip("\n").rsplit("|", 2)[:2]
            pkg, chroot, nvr, _smoke = head.split("|", 3)
            seen[(pkg, chroot)] = (nvr, verdict)
    for (pkg, chroot) in sorted(seen):
        nvr, verdict = seen[(pkg, chroot)]
        out.append("| %s | %s | %s | %s | %s |"
                   % (pkg, builds.get(pkg, "-"), chroot, nvr or "-", verdict))
    return "\n".join(out)


def seed_block(run_id):
    """Minimal audit anchor written before the agent starts.

    A run killed in its first minutes must still leave the inventory and the
    dependency rows on main, so the next run reads state instead of a blank.
    """
    today = time.strftime("%Y-%m-%d", time.gmtime())
    pkgs = len(list(H.specs()))
    deps = dep_table(set(), set(), {})
    return ("run_id: %s\nstatus: unfinished\n\n### Run %s (%s) - seeded at job start\n\n"
            "scope: %d specs; this block is written and pushed before the agent "
            "starts, so a run killed early still leaves the inventory and its "
            "dependency rows on main.\n\nchanged:\n\ndefects-found: 0\ndefects-fixed: 0\n\n%s\n"
            % (run_id, today, run_id, pkgs, deps))


def seed(run_id):
    path = ".opencode-relay.md"
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    if ("\nrun_id: %s\n" % run_id) in "\n" + old or old.startswith("run_id: %s\n" % run_id):
        print("relay already carries run_id %s" % run_id)
        return 0
    open(path, "w", encoding="utf-8").write(seed_block(run_id) + "\n" + old)
    print("seeded relay block for run_id %s" % run_id)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="", help="prepend a minimal unfinished block for RUN_ID")
    ap.add_argument("--verified", default="", help="packages torn down this run")
    ap.add_argument("--fixed", default="", help="packages whose spec this run changed")
    ap.add_argument("--dep-rows", default="", help="file of hand-written dep rows (pkg|row lines)")
    ap.add_argument("--install-rows", action="append", default=[],
                    help="install-sweep rows.txt to render (repeat for one sweep per chroot)")
    ap.add_argument("--only", choices=["versions", "deps", "both", "install", "upstream"],
                    default="both")
    a = ap.parse_args()
    if a.seed:
        return seed(a.seed)
    notes = {}
    if a.dep_rows:
        for line in open(a.dep_rows, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            pkg, row = line.split("|", 1)
            notes[pkg.strip()] = row.strip()
    out = []
    if a.only in ("versions", "both"):
        out.append(version_table())
    if a.only in ("deps", "both"):
        out.append(dep_table(set(a.verified.split()), set(a.fixed.split()), notes))
    if a.only == "install":
        out.append(install_table(a.install_rows))
    if a.only == "upstream":
        out.append(upstream_rows())
    print("\n\n".join(out))


if __name__ == "__main__":
    main()
