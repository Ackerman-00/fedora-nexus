#!/usr/bin/env python3
"""Build the mechanical relay tables from live data.

Rows are derived here; verdicts are not. A package lands in
`deps-verified` only when its name is passed with --verified, which the
agent may do only after it ran a same-run container teardown.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hunt as H  # noqa: E402


def version_table():
    rows = ["| package | packaged version | upstream latest | status |",
            "| --- | --- | --- | --- |"]
    for sp in H.specs():
        pkg = os.path.basename(os.path.dirname(sp))
        ver = H.strip_packaging(H.resolve_version(sp, H.spec_field(sp, "Version")).lstrip("v"))
        _p, ref, ok, _cmd, err = H.probe_upstream(sp)
        if ok is None:
            rows.append("| %s | %s | unprobed (%s) | needs-build |" % (pkg, ver, err))
        elif ok:
            rows.append("| %s | %s | %s | up-to-date |" % (pkg, ver, ref))
        else:
            rows.append("| %s | %s | %s | needs-build |" % (pkg, ver, ref))
    return "\n".join(rows)


def dep_table(verified, fixed, notes):
    rows = ["| package | upstream deps found | in spec | missing | extra/dropped | status | correctness |",
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
                        "one and rpmbuild -bb + install + smoke PASS | unused-BR rot not "
                        "re-derived (build proof only) | %s | unproven: 0 missing (a missing "
                        "BR cannot compile); unused-BR rot unproven on extras |" % (pkg, nbr, status))
        else:
            rows.append("| %s | Source0 artifact (version-checked only) | %d BuildRequires | none found | n/a "
                        "| version-checked | unproven: dependency list not re-derived this run (outside the "
                        "re-tear slice); version proven against this run's upstream row |" % (pkg, nbr))
    return "\n".join(rows)


def install_table(rows_path):
    """Install-test rows from install-sweep's rows.txt, with the COPR build id.

    rows.txt is the sweep's own log: pkg|chroot|nvr|smoke|verdict|why. The build
    id comes from COPR so a row can be traced to the build users download.
    """
    # newest_builds: name -> (nvr, built_id, state, newest_id)
    builds = {name: v[3] for name, v in H.newest_builds().items()}
    out = ["| package | COPR build | chroot | installed NVR | verdict |",
           "| --- | --- | --- | --- | --- |"]
    for line in open(rows_path, encoding="utf-8"):
        parts = line.rstrip("\n").split("|")
        if len(parts) < 5:
            continue
        pkg, chroot, nvr, _smoke, verdict = parts[:5]
        out.append("| %s | %s | %s | %s | %s |"
                   % (pkg, builds.get(pkg, "-"), chroot, nvr or "-", verdict))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", default="", help="packages torn down this run")
    ap.add_argument("--fixed", default="", help="packages whose spec this run changed")
    ap.add_argument("--dep-rows", default="", help="file of hand-written dep rows (pkg|row lines)")
    ap.add_argument("--install-rows", default="", help="install-sweep rows.txt to render")
    ap.add_argument("--only", choices=["versions", "deps", "both", "install"], default="both")
    a = ap.parse_args()
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
    print("\n\n".join(out))


if __name__ == "__main__":
    main()
