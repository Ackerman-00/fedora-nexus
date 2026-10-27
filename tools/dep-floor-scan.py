#!/usr/bin/env python3
"""Compare the dependency floors a source tree declares with the floors a spec pins.

Downloads each Source0 (when the URL expands without a shell macro), extracts the
build manifest, reads every `dependency('x', version: '>=y')` / `pkg-config` floor
plus the `go` directive of a go.mod, and reports:
  MISSING  - declared upstream, no BuildRequires line for it in the spec
  FLOOR    - BuildRequires carries a lower floor than upstream declares

Usage: dep-floor-scan.py [--skip pkg1,pkg2] [--only pkg1,pkg2] [--tree pkg=dir]
                         [--selftest]
Exit 0 = no finding, 1 = findings printed (the caller decides what to fix).
Coverage is every package whose Source0 expands without a shell macro, plus any
tree passed with --tree (a source that a teardown already unpacked). A spec that
needs a shell macro and has no --tree is proven by its container teardown instead.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("DEP_SCAN_CACHE", "/tmp/dep-floor-scan")
MAXB = 200 * 1024 * 1024

# meson builtins and platform-gated names that are not Fedora pkgconfig packages
IGNORE = {
    "threads", "opengl", "jack", "appleframeworks", "pthreads4w",
    "python", "python3", "windows", "corefoundation", "iokit", "cocoa",
    "x11", "xext", "xrandr",  # reached through libX*-devel, checked via PROVIDER
}

# pkgconfig name -> the Fedora package(s) that satisfy it, so a spec that names the
# package instead of the pc file (or pulls it through a DE toolkit) is not a finding.
PROVIDER = {
    "gl": {"libglvnd-devel", "libglvnd-core-devel", "libglvnd", "mesa-libgl-devel"},
    "glesv2": {"libglvnd-devel", "libglvnd-core-devel", "mesa-libgles-devel"},
    "egl": {"libglvnd-devel", "libglvnd-core-devel", "mesa-libegl-devel"},
    "opengl": {"libglvnd-devel", "mesa-libgl-devel"},
    "epoxy": {"libepoxy-devel", "gtk3-devel", "gtk4-devel"},
    "gio-unix-2.0": {"glib2-devel"}, "gio-2.0": {"glib2-devel"},
    "glib-2.0": {"glib2-devel"}, "gobject-2.0": {"glib2-devel"},
    "gmodule-2.0": {"glib2-devel"},
    "ncursesw": {"ncurses-devel"}, "sdl2": {"sdl2-devel", "sdl2-compat-devel"},
    "sdl3": {"sdl3-devel"}, "wayland-scanner": {"wayland-devel"},
    "libinput": {"libinput-devel"}, "glew": {"glew-devel"},
    "gbm": {"mesa-libgbm-devel"}, "libglvnd": {"libglvnd-core-devel", "libglvnd-devel"},
}


def specs():
    out = []
    for s in sorted(glob.glob(os.path.join(ROOT, "*", "*.spec"))):
        out.append((os.path.basename(os.path.dirname(s)), s))
    return out


def macros(txt):
    m = {}
    for line in txt.splitlines():
        g = re.match(r"\s*%(?:global|define)\s+([A-Za-z0-9_]+)\s+(.+)", line)
        if g:
            m[g.group(1)] = g.group(2).strip()
    for tag, key in (("Name", "name"), ("Version", "version"), ("Release", "release"), ("URL", "url")):
        g = re.search(r"^%s:\s*(\S+)" % tag, txt, re.M)
        if g:
            m.setdefault(key, g.group(1))
    return m


def expand(url, m):
    for _ in range(6):
        new = re.sub(r"%\{([A-Za-z0-9_]+)\}", lambda g: m.get(g.group(1), g.group(0)), url)
        new = re.sub(r"%([A-Za-z][A-Za-z0-9_]*)\b", lambda g: m.get(g.group(1), g.group(0)), new)
        new = new.replace("%%", "%")
        if new == url:
            break
        url = new
    return url


def fetch(url, dest):
    os.makedirs(dest, exist_ok=True)
    f = os.path.join(dest, os.path.basename(url.split("?")[0].split("#")[0]) or "src")
    if os.path.exists(f) and os.path.getsize(f) > 0:
        return f
    r = subprocess.run(["curl", "-sSL", "--max-time", "180", "-o", f, url], capture_output=True)
    if r.returncode != 0 or not os.path.exists(f) or os.path.getsize(f) == 0:
        return None
    if os.path.getsize(f) > MAXB:
        os.unlink(f)
        return None
    return f


def unpack(f, dest):
    x = os.path.join(dest, "x")
    shutil.rmtree(x, ignore_errors=True)
    os.makedirs(x, exist_ok=True)
    try:
        if f.endswith((".tar.gz", ".tgz", ".tar.xz", ".tar.bz2", ".tar.zst", ".crate")):
            if f.endswith(".tar.zst"):
                subprocess.run(["tar", "--zstd", "-xf", f, "-C", x], capture_output=True)
            else:
                with tarfile.open(f) as t:
                    t.extractall(x)
            return x
        if f.endswith(".zip"):
            with zipfile.ZipFile(f) as z:
                z.extractall(x)
            return x
    except Exception:
        return None
    return None


def balanced_calls(txt, head):
    """Yield the argument text of every head(...) call with balanced parens."""
    i = 0
    while True:
        i = txt.find(head, i)
        if i < 0:
            return
        j = i + len(head)
        depth = 1
        start = j
        while j < len(txt) and depth:
            if txt[j] == "(":
                depth += 1
            elif txt[j] == ")":
                depth -= 1
            j += 1
        if depth == 0:
            yield txt[start:j - 1]
        i = j


TESTS_GUARD = re.compile(r"^\s*if\b.*\b(build_tests|tests_option|test_ipc)\b")


def meson_deps(x):
    """(declared, fallback, tests-only, option-gated) dependency floors.

    A dependency assigned inside `if not x.found():` is a fallback for a package
    the spec already provides, so it is reported separately instead of as a miss.
    One behind a tests guard, or declared under a tests/ dir, only counts when
    the spec actually builds the tests. One whose `required:` is a meson feature
    option only counts when the spec enables that option.
    """
    found, fallback, testonly, gated = {}, {}, {}, {}
    for f in glob.glob(os.path.join(x, "**", "meson.build"), recursive=True):
        if "/subprojects/" in f or "/build/" in f:
            continue
        rel = f.replace(os.sep, "/")
        in_tests = "/tests/" in rel or rel.endswith("/tests")
        try:
            txt = open(f, errors="ignore").read()
        except Exception:
            continue
        txt = re.sub(r"#[^\n]*", "", txt)
        stack = []  # (indent, kind) of the enclosing guarded blocks
        for line in txt.splitlines():
            stripped = line.strip()
            if stripped:
                indent = len(line) - len(line.lstrip())
                while stack and indent <= stack[-1][0] and not stripped.startswith("if "):
                    stack.pop()
            m = re.match(r"(\s*)if not (\w+)\.found\(\)\s*:?\s*$", line)
            if m:
                stack.append((len(m.group(1)), "fallback"))
                continue
            if TESTS_GUARD.match(line):
                stack.append((len(line) - len(line.lstrip()), "tests"))
                continue
            if "dependency(" not in line:
                continue
            calls = list(balanced_calls(line, "dependency("))
            if not calls:
                continue
            kind = "tests" if in_tests or any(k == "tests" for _i, k in stack) else (
                "fallback" if stack else "declared")
            for args in calls:
                nm = re.search(r"['\"]([^'\"]+)['\"]", args)
                if not nm:
                    continue
                name = nm.group(1).lower()
                if not re.match(r"^[a-z0-9][a-z0-9_.+-]*$", name):
                    continue
                floor = None
                v = re.search(r"version\s*:\s*['\"]([^'\"]+)['\"]", args)
                if v:
                    vv = re.search(r"(>=\s*|==\s*)([0-9][0-9A-Za-z.\-]*)", v.group(1))
                    if vv:
                        floor = vv.group(2)
                opt = re.search(r"required\s*:\s*get_option\(\s*['\"]([^'\"]+)['\"]", args)
                if opt and not in_tests and not any(k == "tests" for _i, k in stack):
                    gated.setdefault(name, (floor, opt.group(1)))
                    continue
                dest = {"declared": found, "fallback": fallback, "tests": testonly}[kind]
                dest.setdefault(name, floor)
    return found, fallback, testonly, gated


def spec_floors(txt):
    """pkgconfig name -> floor pinned in the spec (None when no floor)."""
    out = {}
    for m in re.finditer(r"^(?:BuildRequires|Requires)\s*:\s*(.+)$", txt, re.M):
        for tok in m.group(1).split(","):
            tok = tok.strip()
            pm = re.match(r"pkgconfig\(([^)]+)\)\s*(?:>=\s*([0-9][0-9A-Za-z.\-]*))?", tok)
            if pm:
                out[pm.group(1).lower()] = pm.group(2)
                continue
            # plain package floors (`golang >= 1.26`) carry the same weight
            gm = re.match(r"([A-Za-z0-9][A-Za-z0-9._+-]*)\s*(?:>=|==|>)\s*([0-9][0-9A-Za-z.\-_]*)", tok)
            if gm:
                out[gm.group(1).lower()] = gm.group(2)
                continue
            out.setdefault(tok.split()[0].lower() if tok else "", None)
    return out


def go_mod_floor(tree):
    """The Go toolchain floor a go.mod declares (`go 1.26.0` / `toolchain go1.26.4`)."""
    path = os.path.join(tree, "go.mod")
    if not os.path.exists(path):
        return None
    floor = None
    try:
        txt = open(path, errors="ignore").read()
    except OSError:
        return None
    m = re.search(r"^go\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)", txt, re.M)
    if m:
        floor = m.group(1)
    m = re.search(r"^toolchain\s+go([0-9]+\.[0-9]+(?:\.[0-9]+)?)", txt, re.M)
    if m and (floor is None or cmp_ver(m.group(1), floor) > 0):
        floor = m.group(1)
    return floor


def cmp_ver(a, b):
    def key(v):
        parts = [int(x) if x.isdigit() else x for x in re.split(r"[.\-]", v)]
        while len(parts) > 1 and parts[-1] in (0, "0"):
            parts.pop()
        return parts
    try:
        return (key(a) > key(b)) - (key(a) < key(b))
    except TypeError:
        return 0


PRERELEASE = re.compile(r"^([0-9][0-9.]*)[.\-~]?(alpha|beta|rc|pre)", re.I)


def numeric_base(v):
    """The numeric head of a version: rpm cannot express a meson pre-release."""
    m = PRERELEASE.match(v) or re.match(r"^([0-9][0-9.]*)", v)
    return (m.group(1) if m else v).rstrip(".")


def floor_finding(upstream, spec_floor, nofloor):
    """The finding code for one dep, or None. NOFLOOR is opt-in: most specs here
    name a pc file without a floor, and upstream's floor is often narrower."""
    if not upstream:
        return None
    if spec_floor is None:
        return "NOFLOOR" if nofloor else None
    if cmp_ver(spec_floor, upstream) < 0:
        # `>= 1.8.alpha` is pinned as `>= 1.8`: same base, rpm-safe form
        if PRERELEASE.match(upstream) and cmp_ver(numeric_base(spec_floor), numeric_base(upstream)) >= 0:
            return None
        return "FLOOR"
    return None


def selftest():
    """Prove the FLOOR comparison fires before trusting a silent run."""
    import tempfile
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "src"))
    with open(os.path.join(d, "src", "meson.build"), "w") as fh:
        fh.write("libinput_dep = dependency('libinput', version: '>=1.27')\n"
                 "glib_dep = dependency('glib-2.0')\n")
    deps, _fb, _to, _g = meson_deps(d)
    sf = spec_floors("BuildRequires: pkgconfig(libinput) >= 1.23\nBuildRequires: glib2-devel\n")
    ok = deps.get("libinput") == "1.27" and sf.get("libinput") == "1.23"
    ok = ok and cmp_ver(sf["libinput"], deps["libinput"]) < 0
    ok = ok and (PROVIDER.get("glib-2.0", set()) & set(sf)) == {"glib2-devel"}
    # go.mod carries a toolchain floor the meson scan cannot see
    with open(os.path.join(d, "src", "go.mod"), "w") as fh:
        fh.write("module example.com/x\n\ngo 1.26.0\n\ntoolchain go1.27.1\n")
    ok = ok and go_mod_floor(os.path.join(d, "src")) == "1.27.1"
    ok = ok and spec_floors("BuildRequires: golang\n") == {"golang": None}
    ok = ok and cmp_ver(spec_floors("BuildRequires: golang >= 1.26\n")["golang"], "1.26.0") == 0
    ok = ok and cmp_ver("1.24", "1.26") < 0
    ok = ok and floor_finding("1.26", None, True) == "NOFLOOR"
    ok = ok and floor_finding("1.26", None, False) is None
    ok = ok and floor_finding("1.26", "1.24", True) == "FLOOR"
    ok = ok and floor_finding("1.26", "1.26", True) is None
    ok = ok and floor_finding("1.8.alpha", "1.8", True) is None
    ok = ok and floor_finding("1.9", "1.8", True) == "FLOOR"
    ok = ok and floor_finding(None, None, True) is None
    # tests-only deps classify apart from the shipped build
    os.makedirs(os.path.join(d, "src", "tests"), exist_ok=True)
    with open(os.path.join(d, "src", "tests", "meson.build"), "w") as fh:
        fh.write("xt = dependency('xcb-xtest')\n")
    with open(os.path.join(d, "src", "meson.build"), "a") as fh:
        fh.write("if build_tests\n  xr = dependency('xcb-render')\nendif\n")
    deps, _fb, to, g = meson_deps(d)
    ok = ok and "xcb-xtest" in to and "xcb-render" in to
    ok = ok and "xcb-xtest" not in deps and "xcb-render" not in deps
    ok = ok and "libinput" in deps
    # an option-gated dep only counts once the spec enables the option
    with open(os.path.join(d, "src", "meson.build"), "a") as fh:
        fh.write("tr = dependency('tracy', required: get_option('tracy'))\n")
    deps2, _fb2, _to2, g = meson_deps(d)
    ok = ok and g.get("tracy") == (None, "tracy") and "tracy" not in deps2
    print("selftest %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--nofloor", action="store_true",
                    help="also report a dep whose spec line carries no floor")
    ap.add_argument("--tree", action="append", default=[], metavar="PKG=DIR",
                    help="scan an already-unpacked source tree (e.g. from a teardown)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    skip = set(filter(None, a.skip.split(",")))
    only = set(filter(None, a.only.split(",")))
    trees = dict(t.split("=", 1) for t in a.tree)
    findings = []
    checked = 0
    for pkg, spec in specs():
        if pkg in skip or (only and pkg not in only):
            continue
        txt = open(spec, errors="ignore").read()
        m = macros(txt)
        src = re.search(r"^Source0?\s*:\s*(\S+)", txt, re.M)
        tree = trees.get(pkg)
        if not src and not tree:
            continue
        first = expand(src.group(1), m) if src else ""
        if not tree and "%" in first:
            continue  # shell macro in Source0: the container build is the proof, not this scan
        urls = [first.split("#")[0]]
        tree = trees.get(pkg)
        for u in ([] if tree else urls):
            if not u.startswith(("http://", "https://", "ftp://")):
                continue
            if not re.search(r"\.(tar\.gz|tgz|tar\.xz|tar\.bz2|tar\.zst|zip|crate)$", u.split("#")[0]):
                continue
            if a.no_fetch and not os.path.exists(os.path.join(CACHE, pkg)):
                continue
            f = fetch(u, os.path.join(CACHE, pkg))
            if not f:
                continue
            tree = unpack(f, os.path.join(CACHE, pkg))
            if tree:
                break
        if not tree:
            continue
        deps, fallbacks, testonly, gated = meson_deps(tree)
        gofloor = go_mod_floor(tree)
        if gofloor:
            deps["golang"] = gofloor
        # A tests-only dep is required exactly when the spec builds the tests.
        tests_built = bool(re.search(r"-Dtests[= ]enabled|--buildtype[= ]debug", txt))
        if tests_built:
            for name, floor in testonly.items():
                deps.setdefault(name, floor)
        sf = spec_floors(txt)
        # An option-gated dep is required exactly when the spec enables its option.
        for name, (floor, opt) in sorted(gated.items()):
            if re.search(r"-D%s[= ](enabled|true)" % re.escape(opt), txt):
                deps.setdefault(name, floor)
                continue
            if name in sf:
                continue
            print("%-32s %-8s %-28s upstream=%-10s spec=%s (optional, -D%s not enabled)"
                  % (pkg, "EXCLUDED", name, floor or "-", "-", opt))
        if not deps:
            continue
        checked += 1
        for name in sorted(testonly):
            if name in deps or name in sf:
                continue
            print("%-32s %-8s %-28s upstream=%-10s spec=%s (tests-only, not built: no -Dtests=enabled)"
                  % (pkg, "EXCLUDED", name, testonly[name] or "-", "-"))
        for name in sorted(fallbacks):
            print("%-32s %-8s %-28s upstream=%-10s spec=%s (only if the primary dep is absent)"
                  % (pkg, "FALLBACK", name, fallbacks[name] or "-", "-"))
        for name, floor in sorted(deps.items()):
            if name in IGNORE:
                continue
            if name not in sf:
                if PROVIDER.get(name, set()) & set(sf):
                    continue
                findings.append((pkg, "MISSING", name, floor or "-", "-"))
                continue
            spec_floor = sf[name]
            code = floor_finding(floor, spec_floor, a.nofloor)
            if code:
                findings.append((pkg, code, name, floor, spec_floor or "-"))
    for f in findings:
        print("%-32s %-8s %-28s upstream=%-10s spec=%s" % f)
    print("scanned %d packages with a build manifest; %d finding(s)" % (checked, len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
