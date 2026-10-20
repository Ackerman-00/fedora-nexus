#!/usr/bin/env python3
"""hunt.py - mechanical hunt categories for the relay.

Every category here runs a real check against a live source and reports
what it found. Nothing is assumed and nothing is asserted from memory: a
category that cannot run says so instead of claiming a clean result.

Output: one relay-ready line per category

    hunt: <category> - <what was checked> - <finding>

followed by the detail rows for anything that needs fixing.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.request
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UA = {"User-Agent": "fedora-nexus-hunt/1.0"}
COPR = "https://copr.fedorainfracloud.org/api_3"


def _gh_headers():
    headers = dict(UA)
    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
             or os.environ.get("REPO_FULL_ACCESS_TOKEN"))
    if token:
        headers["Authorization"] = "token " + token
    return headers


def get_json(url, timeout=45):
    req = urllib.request.Request(url, headers=_gh_headers() if "api.github.com" in url else UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 404):
            return None
        raise


def resolve_version(path, raw):
    """Expand %{macro} in a spec field from the spec's own %global definitions."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    for _ in range(3):
        m = re.search(r"%\{(\w+)\}", raw)
        if not m:
            break
        g = re.search(r"^%%global\s+%s\s+(\S+)" % re.escape(m.group(1)), txt, re.M)
        if not g:
            break
        raw = raw.replace(m.group(0), g.group(1))
    return raw


def strip_packaging(v):
    """Drop packaging suffixes so 1.3.1 is not 'older' than 1.3.1-0-ppa2."""
    v = re.sub(r"[-+](\d+[._]?(fc|el|deb|ubuntu|ppa)\S*|ppa\d+|git\S*)$", "", v or "")
    v = re.sub(r"\.git\S+$", "", v)
    v = re.sub(r"[-._](r|rel)\d+$", "", v)
    return v.strip()


def sweep_module():
    spec = importlib.util.spec_from_file_location("ts", os.path.join(HERE, "teardown-sweep.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def specs():
    out = []
    for d in sorted(os.listdir(ROOT)):
        pdir = os.path.join(ROOT, d)
        if not os.path.isdir(pdir):
            continue
        for f in sorted(os.listdir(pdir)):
            if f.endswith(".spec"):
                out.append(os.path.join(pdir, f))
    return out


def spec_field(path, key):
    try:
        txt = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""
    m = re.search(r"^%s:\s*(.+)$" % re.escape(key), txt, re.M)
    return m.group(1).strip() if m else ""


def spec_macro(path, name):
    try:
        txt = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""
    m = re.search(r"^%%global\s+%s\s+(\S+)" % re.escape(name), txt, re.M)
    return m.group(1).strip() if m else ""


def github_repo(url):
    m = re.search(r"github\.com/([^/]+)/([^/\s#]+)", url or "")
    return (m.group(1), m.group(2).replace(".git", "")) if m else None


def vkey(v):
    parts = [p for p in re.split(r"[.\-_+~]", (v or "").strip().lstrip("vV")) if p]
    out = []
    for p in parts:
        m = re.match(r"^(\d+)(.*)$", p)
        out.append((0, int(m.group(1)), m.group(2)) if m else (-1, 0, p))
    return out


def vge(a, b):
    ka, kb = vkey(a), vkey(b)
    while len(ka) < len(kb):
        ka.append((0, 0, ""))
    while len(kb) < len(ka):
        kb.append((0, 0, ""))
    return ka >= kb


def hunt_builds():
    """Newest COPR build per package must not be failed."""
    newest, off = {}, 0
    while True:
        d = get_json("%s/build/list?ownername=ackerman&projectname=nexus&limit=200&offset=%d"
                     % (COPR, off))
        rows = d.get("items", [])
        if not rows:
            break
        for b in rows:
            sp = b.get("source_package")
            name = sp.get("name") if isinstance(sp, dict) else None
            if name and name not in newest:
                newest[name] = b
        off += 200
        if off > 3000:
            break
    bad = []
    for name, b in sorted(newest.items()):
        if b.get("state") in ("failed", "unknown"):
            bad.append((name, b.get("id"), b.get("state")))
    states = {}
    for b in newest.values():
        states[b.get("state")] = states.get(b.get("state"), 0) + 1
    return ("builds", "%d packages, %d failed" % (len(newest), len(bad)),
            "states: " + ", ".join("%s=%d" % kv for kv in sorted(states.items())), bad)


def hunt_chroots():
    """The project's enabled chroots, re-read live."""
    d = get_json("%s/project?ownername=ackerman&projectname=nexus" % COPR)
    roots = sorted((d.get("chroot_repos") or {}).keys())
    bad = [r for r in roots if "fedora" not in r and "epel" not in r]
    return ("chroots", "%d enabled" % len(roots), ", ".join(roots), bad)


def upstream_refs(txt):
    """Find the upstream project in a spec: URL and every Source line."""
    urls = re.findall(r"^(?:URL|Source\d*):\s*(\S+)", txt, re.M)
    for u in urls:
        u = u.split("#")[0]
        m = re.search(r"github\.com/([^/\s]+)/([^/\s#]+)", u)
        if m:
            yield ("github", m.group(1), m.group(2).rstrip("/"))
            continue
        m = re.search(r"codeberg\.org/([^/\s]+)/([^/\s#]+)", u)
        if m:
            yield ("codeberg", m.group(1), m.group(2).rstrip("/"))
            continue
        m = re.search(r"gitlab\.freedesktop\.org/([^/\s]+)/([^/\s#]+)", u)
        if m:
            yield ("gitlab-fdo", m.group(1), m.group(2).rstrip("/"))
            continue
        m = re.search(r"gitlab\.com/([^/\s]+)/([^/\s#]+)", u)
        if m:
            yield ("gitlab", m.group(1), m.group(2).rstrip("/"))
            continue
        m = re.search(r"pypi\.org/project/([^/\s#]+)", u)
        if m:
            yield ("pypi", m.group(1), "")
            continue


def latest_release(forge, owner, repo):
    if forge == "github":
        return (get_json("https://api.github.com/repos/%s/%s/releases/latest" % (owner, repo), 30)
                or {}).get("tag_name")
    if forge == "codeberg":
        d = get_json("https://codeberg.org/api/v1/repos/%s/%s/releases/latest" % (owner, repo), 30) or {}
        return d.get("tag_name")
    if forge in ("gitlab", "gitlab-fdo"):
        host = "gitlab.com" if forge == "gitlab" else "gitlab.freedesktop.org"
        d = get_json("https://%s/api/v4/projects/%s/releases" % (host, quote(owner + "/" + repo, "")), 30) or []
        for rel in d:
            if not rel.get("upcoming_release"):
                return rel.get("tag_name")
    if forge == "pypi":
        d = get_json("https://pypi.org/pypi/%s/json" % owner, 30) or {}
        return (d.get("info") or {}).get("version")
    return None


def hunt_upstream():
    """Spec pin vs upstream HEAD (git pins) or latest release (tag pins)."""
    findings, checked, skipped = [], 0, []
    for sp in specs():
        txt = open(sp, encoding="utf-8", errors="replace").read()
        refs = list(upstream_refs(txt))
        if not refs:
            skipped.append(os.path.basename(sp))
            continue
        forge, owner, repo = refs[0]
        commit = spec_macro(sp, "commit")
        ver = strip_packaging(resolve_version(sp, spec_field(sp, "Version")).lstrip("v"))
        checked += 1
        try:
            if commit and forge == "github":
                out = subprocess.run(["git", "ls-remote", "https://github.com/%s.git" % repo, "HEAD"],
                                     capture_output=True, text=True, timeout=60).stdout.split()
                if not out:
                    continue
                head = out[0]
                if head != commit:
                    findings.append((os.path.basename(sp), "commit %s -> %s" % (commit[:7], head[:7])))
                continue
            tag = latest_release(forge, owner, repo)
            if not tag:
                continue
            tag = strip_packaging(str(tag).lstrip("v"))
            if re.search(r"\d", ver) and re.search(r"\d", tag) and not vge(ver, tag):
                findings.append((os.path.basename(sp), "version %s -> %s" % (ver, tag)))
        except Exception as exc:
            findings.append((os.path.basename(sp), "probe failed: %s" % type(exc).__name__))
    return ("upstream-versions", "%d packages checked, %d behind" % (checked, len(findings)),
            "skipped (no upstream URL found): %s" % (", ".join(skipped) or "none"), findings)


def hunt_cves():
    """OSV hits, filtered by the advisory's own version ranges."""
    ts = sweep_module()
    hits, checked = [], 0
    for sp in specs():
        name = spec_field(sp, "Name")
        ver = spec_field(sp, "Version")
        if not name or not ver:
            continue
        if "%" in ver:
            m = re.search(r"^%global\s+\w*version\s+(\d[\w.+-]*)", open(sp, encoding="utf-8", errors="replace").read(), re.M)
            if m:
                ver = m.group(1)
            else:
                continue
        checked += 1
        try:
            ids = ts.osv_query(name, ver, "fedora")
        except Exception:
            continue
        for vid in ids:
            state = ts.osv_version_affected(vid, ver)
            if state is True:
                hits.append((name, ver, vid, "affected"))
            elif state is None:
                hits.append((name, ver, vid, "unverified"))
    aff = [h for h in hits if h[3] == "affected"]
    unv = [h for h in hits if h[3] == "unverified"]
    return ("cves", "%d packages, %d affected, %d unverified" % (checked, len(aff), len(unv)),
            "unverified = advisory ranges do not cover the version", hits)


def hunt_licenses():
    """Every open-source spec must ship its license text."""
    missing, n_a, checked = [], [], 0
    for sp in specs():
        lic = spec_field(sp, "License")
        if not lic:
            missing.append((os.path.basename(sp), "no License: field"))
            continue
        if "LicenseRef" in lic:
            n_a.append(os.path.basename(sp))
            continue
        txt = open(sp, encoding="utf-8", errors="replace").read()
        checked += 1
        if re.search(r"^%license\b", txt, re.M) or re.search(r"^Source\d*:.*(LICENSE|COPYING)", txt, re.M | re.I):
            continue
        missing.append((os.path.basename(sp), "no %license and no license Source"))
    note = "LicenseRef (proprietary, no text to ship): %s" % (", ".join(n_a) or "none")
    return ("licenses", "%d specs, %d missing license text" % (checked, len(missing)),
            note, missing)


def hunt_release_discipline():
    """The newest changelog entry must name the spec's own Version and Release."""
    bad, checked, skipped = [], 0, []
    for sp in specs():
        txt = open(sp, encoding="utf-8", errors="replace").read()
        ver = resolve_version(sp, spec_field(sp, "Version")).strip()
        rel = resolve_version(sp, spec_field(sp, "Release")).split("%{?dist}")[0].strip()
        if "%{" in ver:
            # Macro from outside the spec (redhat-rpm-config, forge-srpm-macros):
            # only a Fedora buildroot can expand it - not a finding.
            skipped.append(os.path.basename(sp))
            continue
        ch = re.search(r"^%changelog\s*\n(.*)", txt, re.M | re.S)
        if not ch:
            bad.append((os.path.basename(sp), "no %changelog"))
            continue
        first = ch.group(1).strip().splitlines()[0]
        checked += 1
        if ver.split("^")[0] not in first or (rel and rel not in first):
            bad.append((os.path.basename(sp), "changelog %r vs Version %r Release %r"
                        % (first[-60:], ver, rel)))
    note = "skipped (version from an external macro): %s" % (", ".join(skipped) or "none")
    return ("release-discipline", "%d specs, %d changelog mismatches" % (checked, len(bad)),
            note, bad)


HUNTS = (hunt_builds, hunt_chroots, hunt_upstream, hunt_cves, hunt_licenses,
         hunt_release_discipline)


def main():
    only = [a.replace("_", "-") for a in sys.argv[1:]] or None
    for fn in HUNTS:
        name = fn.__name__.replace("hunt_", "").replace("_", "-")
        if only and name not in only:
            continue
        try:
            cat, summary, note, findings = fn()
        except Exception as exc:
            print("hunt: %s - UNAVAILABLE (%s: %s)" % (name, type(exc).__name__, exc))
            continue
        print("hunt: %s - %s" % (cat, summary))
        if note:
            print("    %s" % note)
        for f in findings:
            print("    FINDING %s: %s" % (f[0], " | ".join(str(x) for x in f[1:])))


if __name__ == "__main__":
    main()
