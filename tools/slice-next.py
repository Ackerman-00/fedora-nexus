#!/usr/bin/env python3
"""Compute the next fleet teardown slice from the relay ledger.

Rotation must cover the whole inventory within four runs, so a slice is at
least ceil(specs / 4). The relay records where the last slice stopped as
`teardown-slice: <pkgs> | next-start: <pkg>`. Deriving the next slice from
that line by hand is the step that silently repeats or skips packages, so it
is computed here instead: start at the recorded next-start, walk the
inventory in order, wrap at the end, and print the next-start for the run
after this one.
"""
import argparse
import glob
import os
import re
import sys

RUNS_PER_FLEET = 4


def inventory(root):
    """Package directories that hold a spec named after the directory."""
    pkgs = []
    for spec in sorted(glob.glob(os.path.join(root, "*", "*.spec"))):
        pkg = os.path.basename(os.path.dirname(spec))
        if os.path.basename(spec) == pkg + ".spec":
            pkgs.append(pkg)
    return pkgs


def ledger(text):
    """The newest teardown-slice line: (packages, next-start)."""
    last = None
    for line in text.splitlines():
        if line.startswith("teardown-slice:"):
            last = line
    if last is None:
        return [], None
    body = last.split(":", 1)[1]
    pkgs, _sep, tail = body.partition("|")
    match = re.search(r"next-start:\s*([A-Za-z0-9._+-]+)", tail)
    return pkgs.split(), (match.group(1) if match else None)


def min_slice(total):
    return (total + RUNS_PER_FLEET - 1) // RUNS_PER_FLEET


def next_slice(pkgs, start, size):
    if not pkgs:
        return []
    index = pkgs.index(start) if start in pkgs else 0
    return [pkgs[(index + step) % len(pkgs)] for step in range(min(size, len(pkgs)))]


def following(pkgs, slice_pkgs):
    if not slice_pkgs:
        return None
    return pkgs[(pkgs.index(slice_pkgs[-1]) + 1) % len(pkgs)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--relay", default=".opencode-relay.md")
    ap.add_argument("--root", default=".")
    ap.add_argument("--start", default="", help="override the recorded next-start")
    ap.add_argument("--size", type=int, default=0, help="defaults to ceil(specs/4)")
    ap.add_argument("--list", action="store_true", help="one package per line")
    ap.add_argument("--check", default="", help="comma or space separated slice to validate")
    a = ap.parse_args(argv)

    pkgs = inventory(a.root)
    if not pkgs:
        print("no package specs under %s" % a.root, file=sys.stderr)
        return 2

    recorded = None
    if os.path.exists(a.relay):
        _prev, recorded = ledger(open(a.relay, encoding="utf-8").read())

    if a.check:
        proposed = [p for p in re.split(r"[,\s]+", a.check.strip()) if p]
        unknown = [p for p in proposed if p not in pkgs]
        if unknown:
            print("FAIL: not in the inventory: %s" % " ".join(unknown), file=sys.stderr)
            return 1
        need = min_slice(len(pkgs))
        if len(set(proposed)) < need:
            print("FAIL: slice has %d packages, need >= %d" % (len(set(proposed)), need),
                  file=sys.stderr)
            return 1
        print("PASS: slice of %d covers the fleet in %d runs" % (len(set(proposed)), RUNS_PER_FLEET))
        return 0

    start = a.start or recorded or pkgs[0]
    size = a.size or min_slice(len(pkgs))
    slice_pkgs = next_slice(pkgs, start, size)
    if a.list:
        print("\n".join(slice_pkgs))
    else:
        print("teardown-slice: %s | next-start: %s"
              % (" ".join(slice_pkgs), following(pkgs, slice_pkgs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
