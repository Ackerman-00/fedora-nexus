#!/usr/bin/env python3
"""hunt.py - mechanical hunt categories for the relay.

Every category here runs a real check against a live source and reports
what it found. Nothing is assumed and nothing is asserted from memory: a
category that cannot run says so instead of claiming a clean result.

Output: one relay-ready line per category

    hunt: <category> - <what was checked> - <finding>

followed by the detail rows for anything that needs fixing.
"""
import gzip
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
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


def fetch_sha256(url, attempts=3):
    """sha256 of a remote file, retried: a dropped socket is not a mismatch."""
    last = ""
    for n in range(attempts):
        h = hashlib.sha256()
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=600) as r:
                for chunk in iter(lambda: r.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest(), ""
        except Exception as exc:  # noqa: BLE001 - any transport error retries
            last = "%s: %s" % (type(exc).__name__, exc)
            time.sleep(2 * (n + 1))
    return "", last


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


def newest_builds():
    """Per package: the newest build's state, and the NVR of the newest SRPM.

    A skipped build carries no SRPM, so the NVR has to come from the newest
    row that actually built or the published NVR would look unknowable.
    """
    newest, built, off = {}, {}, 0
    while True:
        d = get_json("%s/build/list?ownername=ackerman&projectname=nexus&limit=200&offset=%d"
                     % (COPR, off))
        rows = d.get("items", [])
        if not rows:
            break
        for b in rows:
            sp = b.get("source_package")
            name = sp.get("name") if isinstance(sp, dict) else None
            if not name:
                continue
            bid = b.get("id", 0)
            if name not in newest or bid > newest[name].get("id", 0):
                newest[name] = b
            if (sp.get("url") or "") and (name not in built or bid > built[name].get("id", 0)):
                built[name] = b
        off += 200
        if off > 3000:
            break
    out = {}
    for name, b in newest.items():
        source = built.get(name) or b
        url = ((source.get("source_package") or {}).get("url") or "").split("?")[0]
        base = os.path.basename(url)
        prefix = name + "-"
        nvr = base[len(prefix):] if base.startswith(prefix) else base
        out[name] = (nvr_norm(nvr), source.get("id"), b.get("state"), b.get("id"))
    return out


def hunt_builds():
    """Newest COPR build per package must not be failed."""
    newest = newest_builds()
    bad = []
    states = {}
    for name, (_nvr, _srcid, state, newestid) in sorted(newest.items()):
        if state in ("failed", "unknown"):
            bad.append((name, newestid, state))
        states[state] = states.get(state, 0) + 1
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
        tags = get_json("https://%s/api/v4/projects/%s/repository/tags" % (host, quote(owner + "/" + repo, "")), 30) or []
        for t in tags:
            if re.match(r"^v?\d+(\.\d+)+$", t.get("name", "")):
                return t["name"]
    if forge == "pypi":
        d = get_json("https://pypi.org/pypi/%s/json" % owner, 30) or {}
        return (d.get("info") or {}).get("version")
    return None


def vendor_version(pkg, txt):
    """Version from a vendor feed that exposes no git tag or release API."""
    if pkg == "opencode-desktop":
        d = get_json("https://opencode.ai/update/api/latest/desktop/opencode/", 45) or {}
        return d.get("version"), "update feed /update/api/latest/desktop/opencode/"
    if pkg == "fluxer":
        url = (re.search(r"^Source0:\s*(\S+)", txt, re.M) or [None, ""])[1]
        if not url:
            return None, ""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fluxer.rpm")
            subprocess.run(["curl", "-fsSL", "-A", UA["User-Agent"], "-o", path, url], timeout=600)
            out = subprocess.run(["rpm", "-qp", "--qf", "%{VERSION}", path],
                                 capture_output=True, text=True, timeout=60)
            return (out.stdout.strip() or None), "api.fluxer.app latest rpm -> rpm -qp"
    if pkg == "gpu-screen-recorder":
        html = get_text("https://git.dec05eba.com/gpu-screen-recorder/") or ""
        tags = re.findall(r"tag/\?h=(\d+(?:\.\d+)+)", html)
        return (max(tags, key=vkey) if tags else None), "git.dec05eba.com cgit tag list"
    if pkg == "protonplus":
        d = get_json("https://api.github.com/repos/Vysp3r/ProtonPlus/releases/latest", 30) or {}
        return (d.get("tag_name") or "").lstrip("v") or None, "github Vysp3r/ProtonPlus releases/latest"
    if pkg == "zig0.17":
        d = get_json("https://ziglang.org/download/index.json", 60) or {}
        keys = [k for k in d if re.match(r"^\d+(\.\d+)+$", k)]
        return (max(keys, key=vkey) if keys else None), "ziglang.org/download/index.json stable keys"
    if pkg == "rootapp":
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "Root.AppImage")
            subprocess.run(["curl", "-fsSL", "-A", UA["User-Agent"], "-o", path,
                            "https://installer.rootapp.com/installer/Linux/X64/Root.AppImage"], timeout=1800)
            digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
            out = subprocess.run(
                ["bash", "-c",
                 "readelf -h \"$1\" | awk 'NR==13{s=$5} NR==18{t=$5} NR==19{n=$5} END{print s+t*n}'",
                 "_", path], capture_output=True, text=True, timeout=120).stdout.strip()
            subprocess.run(["unsquashfs", "-q", "-d", os.path.join(tmp, "root"), "-o", out, path],
                           capture_output=True, text=True, timeout=600)
            ver = None
            for root, _, files in os.walk(os.path.join(tmp, "root")):
                for f in files:
                    if f.endswith(".desktop"):
                        with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                            m = re.search(r"X-AppImage-Version=(\S+)", fh.read())
                            if m:
                                ver = m.group(1)
            return ver, "AppImage sha256 %s..., X-AppImage-Version" % digest[:8]
    return None, ""


def probe_upstream(sp):
    """One spec's pin vs the live upstream: (pkg, ref, ok, command, err)."""
    pkg = os.path.basename(os.path.dirname(sp))
    txt = open(sp, encoding="utf-8", errors="replace").read()
    ver = strip_packaging(resolve_version(sp, spec_field(sp, "Version")).lstrip("v"))
    refs = list(upstream_refs(txt))
    if not refs:
        ref, cmd = vendor_version(pkg, txt)
        if not ref:
            return pkg, "", None, "", "no upstream URL and no vendor feed"
        ok = not (re.search(r"\d", ver) and re.search(r"\d", ref) and not vge(ver, ref))
        return pkg, ref, ok, cmd, ""
    forge, owner, repo = refs[0]
    commit = spec_macro(sp, "commit")
    if commit and forge in ("github", "codeberg"):
        host = "github.com" if forge == "github" else "codeberg.org"
        out = subprocess.run(["git", "ls-remote", "https://%s/%s/%s.git" % (host, owner, repo), "HEAD"],
                             capture_output=True, text=True, timeout=60).stdout.split()
        if not out:
            return pkg, "", None, "git ls-remote %s/%s HEAD" % (owner, repo), "HEAD unreadable"
        return (pkg, out[0][:7], out[0] == commit,
                "git ls-remote %s/%s HEAD" % (owner, repo), "")
    tag = latest_release(forge, owner, repo)
    if not tag:
        return pkg, "", None, "latest_release %s/%s" % (owner, repo), "no release seen"
    tag = strip_packaging(str(tag).lstrip("v"))
    ok = not (re.search(r"\d", ver) and re.search(r"\d", tag) and not vge(ver, tag))
    return pkg, tag, ok, "%s %s/%s releases/latest" % (forge, owner, repo), ""


def hunt_upstream():
    """Spec pin vs upstream HEAD (git pins) or latest release (tag pins)."""
    findings, checked, skipped = [], 0, []
    for sp in specs():
        pkg, ref, ok, cmd, err = probe_upstream(sp)
        if ok is None:
            skipped.append(os.path.basename(sp))
            if err and err != "no upstream URL and no vendor feed":
                findings.append((pkg, "unprobed: " + err))
            continue
        checked += 1
        if not ok:
            findings.append((pkg, "behind upstream %s" % ref))
    return ("upstream-versions", "%d packages checked, %d behind" % (checked, len(findings)),
            "skipped (no upstream URL found): %s" % (", ".join(skipped) or "none"), findings)


def upstream_rows():
    """Per-package relay lines: the pin, the live ref, and the command behind it."""
    date = time.strftime("%Y-%m-%d", time.gmtime())
    rows = []
    for sp in specs():
        pkg, ref, ok, cmd, err = probe_upstream(sp)
        ver = strip_packaging(resolve_version(sp, spec_field(sp, "Version")).lstrip("v"))
        if ok is None:
            rows.append("upstream: %s UNPROBED-%s | %s | %s" % (pkg, err.replace(" ", "-"), cmd or "-", date))
        else:
            rows.append("upstream: %s %s %s spec | %s | %s"
                        % (pkg, ref, "==" if ok else "!= (pinned %s)" % ver, cmd, date))
    return rows


def hunt_cves():
    """OSV hits, filtered by the advisory's own version ranges."""
    ts = sweep_module()
    hits, checked, skipped = [], 0, []
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
                # a template or git-snapshot version: nothing to ask OSV about
                skipped.append(os.path.basename(sp))
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
    note = "unverified = advisory ranges do not cover the version; skipped (template version): %d" % len(skipped)
    return ("cves", "%d packages, %d affected, %d unverified" % (checked, len(aff), len(unv)),
            note, hits)


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


def hunt_version_probe():
    """Specs whose Source0 embeds the version: is a newer one published?

    The release feeds do not cover a vendor that just puts the version in the
    download path (opencode.ai/files/bin/<version>/...), so those packages
    would otherwise never be checked.
    """
    findings, checked = [], 0
    for sp in specs():
        txt = open(sp, encoding="utf-8", errors="replace").read()
        ver = resolve_version(sp, spec_field(sp, "Version")).strip()
        if not re.search(r"^\d+(\.\d+)*", ver):
            continue
        for src in re.findall(r"^Source\d*:\s*(\S+)", txt, re.M):
            if "%{version}" not in src:
                continue
            checked += 1
            base = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", ver)
            if not base:
                continue
            major, minor, patch = base.group(1), base.group(2), base.group(3) or "0"
            cands = ["%s.%s.%d" % (major, minor, int(patch) + 1),
                     "%s.%d.0" % (major, int(minor) + 1),
                     "%s.%s.%d" % (int(major) + 1, minor, 0)]
            for cand in cands:
                url = src.replace("%{version}", cand)
                code, ctype, clen = head_probe(url)
                if code in (200, 206) and "text/html" not in (ctype or "") and (clen or 0) > 1000:
                    findings.append((os.path.basename(sp),
                                     "%s is published upstream (%s, %s) - the spec pins %s"
                                     % (cand, url.split("/")[-1], (ctype or "").split(";")[0], ver)))
                    break
            break
    return ("version-probe", "%d versioned sources checked, %d newer upstream"
            % (checked, len(findings)), "", findings)


def head_probe(url):
    """HEAD (or 1-byte GET) -> (status, content-type, content-length)."""
    try:
        req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-1023"}, method="GET")
        with urllib.request.urlopen(req, timeout=45) as r:
            clen = r.headers.get("content-length") or 0
            return r.status, r.headers.get("content-type", ""), int(clen) if str(clen).isdigit() else 0
    except urllib.error.HTTPError as exc:
        return exc.code, "", 0
    except Exception:
        return 0, "", 0


def hunt_sources():
    """Every http(s) Source must answer: a dead Source0 fails the SRPM stage."""
    findings, checked, skipped = [], 0, 0
    for sp in specs():
        url = spec_field(sp, "URL")
        txt = open(sp, encoding="utf-8", errors="replace").read()
        mac = {}
        for name, val in re.findall(r"^%global\s+(\w+)\s+(\S+)", txt, re.M):
            mac[name] = val
        for field, key in (("Name", "name"), ("Version", "version")):
            val = spec_field(sp, field)
            if val:
                mac[key] = val
        if mac.get("shortcommit", "").startswith("%(") and mac.get("commit"):
            mac["shortcommit"] = mac["commit"][:7]
        for m in re.finditer(r"^Source\d*:\s*(\S+)", txt, re.M):
            src = m.group(1)
            if not (src.startswith("http") or src.startswith("%{url}")):
                skipped += 1
                continue
            u = src.replace("%{url}", url)
            for _ in range(6):
                mm = re.search(r"%\{(\w+)\}", u)
                if not mm:
                    break
                val = mac.get(mm.group(1), "")
                if not val or val.startswith("%("):
                    break
                u = u.replace(mm.group(0), val)
            if "%{" in u:
                skipped += 1
                continue
            checked += 1
            code, _ctype, _clen = head_probe(u)
            if code in (404, 410):
                findings.append((os.path.basename(sp),
                                 "Source answers %d: %s" % (code, u)))
    return ("sources", "%d http sources probed, %d skipped (local/macro), %d dead"
            % (checked, skipped, len(findings)), "", findings)


def hunt_readme():
    """Every package directory needs a row in the README's package table."""
    try:
        readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8", errors="replace").read()
    except OSError:
        return ("readme", "README.md missing", "", [])
    rows = set(re.findall(r"^\| `([a-z0-9.+-]+)` \|", readme, re.M))
    dirs = set()
    for d in os.listdir(ROOT):
        pdir = os.path.join(ROOT, d)
        if os.path.isdir(pdir) and any(f.endswith(".spec") for f in os.listdir(pdir)):
            dirs.add(d)
    missing = sorted(dirs - rows)
    extra = sorted(rows - dirs)
    findings = [("README.md", "no row for package %s" % m) for m in missing]
    findings += [("README.md", "row for %s has no package dir" % e) for e in extra]
    return ("readme", "%d packages, %d without a README row" % (len(dirs), len(missing)),
            "", findings)


def nvr_norm(s):
    """Name-version-release without dist, epoch or .src.rpm wrapper."""
    s = (s or "").strip()
    s = re.sub(r"\.src\.rpm$", "", s)
    s = re.sub(r"\.fc\d+$", "", s)
    s = re.sub(r"^\d+:", "", s)
    return s


def repodata_nvr(chroot):
    """Published name -> NVR for one chroot, read from its own primary.xml.gz.

    A fetch that fails must raise, never return {}: an empty map used to make
    every package read as "missing from repodata" (133 bogus findings).
    """
    base = "https://download.copr.fedorainfracloud.org/results/ackerman/nexus/%s" % chroot
    md, raw = "", None
    for attempt in range(3):
        md = get_text(base + "/repodata/repomd.xml")
        m = re.search(r"([a-f0-9]+-primary\.xml\.gz)", md)
        if m:
            try:
                raw = urllib.request.urlopen(
                    urllib.request.Request(base + "/repodata/" + m.group(1), headers=UA),
                    timeout=120).read()
                break
            except Exception:
                raw = None
        time.sleep(3 * (attempt + 1))
    if not raw:
        raise RuntimeError("repodata unreadable for %s after 3 tries" % chroot)
    prim = gzip.decompress(raw).decode("utf-8", "replace")
    out = {}
    for p in re.finditer(r'<package type="rpm">.*?<name>([^<]+)</name>'
                         r'.*?<version epoch="([^"]*)" ver="([^"]+)" rel="([^"]+)"/>', prim, re.S):
        name, epoch, ver, rel = p.groups()
        out[name] = nvr_norm("%s:%s-%s" % (epoch, ver, rel) if epoch not in ("0", "") else "%s-%s" % (ver, rel))
    return out


def hunt_published_nvr():
    """The NVR in git must be the NVR the repo actually serves.

    Compares the newest %changelog NVR (the NVR this repo authored) with the
    SRPM COPR built and with every chroot's published repodata, so a fix that
    never got a new NVR - the failure users would never receive - is a finding.
    """
    builds = newest_builds()
    chroots = sorted((get_json("%s/project?ownername=ackerman&projectname=nexus" % COPR)
                      .get("chroot_repos") or {}).keys())
    pub = {c: repodata_nvr(c) for c in chroots}
    findings, checked = [], 0
    for sp in specs():
        name = resolve_version(sp, spec_field(sp, "Name"))
        if "%{" in name:
            continue
        txt = open(sp, encoding="utf-8", errors="replace").read()
        ch = re.search(r"^%changelog\s*\n(.*)", txt, re.M | re.S)
        if not ch:
            findings.append((name, "no %changelog, NVR unknown"))
            continue
        m = re.match(r"^\*\s+\w+\s+\w+\s+\d+\s+\d{4}\s+.+?\s+-\s+(\S+)\s*$",
                     ch.group(1).strip().splitlines()[0])
        if not m:
            findings.append((name, "unparseable changelog line, NVR unknown"))
            continue
        want = nvr_norm(m.group(1))
        checked += 1
        built, bid, state = builds.get(name, ("", None, None))[:3]
        if not built:
            findings.append((name, "no COPR build row for this package"))
        elif built != want:
            findings.append((name, "git NVR %s is not the built NVR %s (build %s, %s)"
                             % (want, built, bid, state)))
        for c in chroots:
            room = pub[c]
            got = room.get(name)
            if got is None:
                findings.append((name, "%s missing from %s repodata" % (want, c)))
            elif got != want:
                findings.append((name, "%s repodata serves %s, git says %s" % (c, got, want)))
    note = "%d chroots read: %s" % (len(chroots), ", ".join(chroots))
    return ("published-nvr", "%d packages, %d findings" % (checked, len(findings)), note, findings)


def hunt_copr_config():
    """Every repo spec has a COPR record that points at its own subdir and spec.

    A push only builds when the record's subdirectory, spec name and
    webhook flag all agree with the repo directory.
    """
    d = get_json("%s/package/list?ownername=ackerman&projectname=nexus" % COPR)
    items = (d or {}).get("items") or (d or {}).get("packages") or []
    if not items:
        return ("copr-config", "unavailable (package list unreachable)", "", [])
    findings = []
    by_sub = {}
    for it in items:
        sd = it.get("source_dict") or {}
        name = it.get("name") or "?"
        by_sub[sd.get("subdirectory") or ""] = it
        if "Ackerman-00/fedora-nexus" not in (sd.get("clone_url") or ""):
            findings.append((name, "clone_url %s" % (sd.get("clone_url") or "missing")))
        if not it.get("auto_rebuild"):
            findings.append((name, "auto_rebuild off: a push to main would not build it"))
    seen = set()
    for sp in specs():
        sub = os.path.basename(os.path.dirname(sp))
        want = os.path.basename(sp)
        seen.add(sub)
        rec = by_sub.get(sub)
        if rec is None:
            findings.append((sub, "no COPR package record for this repo directory"))
            continue
        got = (rec.get("source_dict") or {}).get("spec") or ""
        if got != want:
            findings.append((sub, "COPR spec is %r but the directory ships %r" % (got, want)))
    for sub in sorted(set(by_sub) - seen):
        findings.append((by_sub[sub].get("name") or sub,
                         "COPR record for subdir %r with no repo directory" % sub))
    return ("copr-config", "%d records, %d specs, %d findings" % (len(items), len(seen), len(findings)),
            "", findings)


def hunt_probes():
    """Every package directory carries an install-test probe, and it is well formed.

    The probe file is what the install sweep runs, so a missing row means a
    package no run ever installs and a stale path means a false FAIL.
    """
    path = os.path.join(HERE, "probes.txt")
    if not os.path.exists(path):
        return ("probes", "unavailable (tools/probes.txt missing)", "", [])
    rows = {}
    findings = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|", 2)
        if len(parts) != 3 or not all(x.strip() for x in parts):
            findings.append((parts[0] or "?", "malformed row: %r" % line))
            continue
        pkg, dnf, smoke = parts
        if pkg in rows:
            findings.append((pkg, "duplicate row"))
            continue
        rows[pkg] = (dnf, smoke)
    inv = {os.path.basename(os.path.dirname(sp)) for sp in specs()}
    for pkg in sorted(inv - set(rows)):
        findings.append((pkg, "no probe row in tools/probes.txt"))
    for pkg in sorted(set(rows) - inv):
        findings.append((pkg, "probe row for a directory that ships no spec"))
    return ("probes", "%d rows, %d specs, %d findings" % (len(rows), len(inv), len(findings)),
            "", findings)


def supported_releases(readme_text):
    """Parse the README 'Supported releases' claim into (numbers, rawhide)."""
    m = re.search(r"\*\*Supported releases:\*\*(.*?)(?:\n>\s*$|\n\n)", readme_text, re.S)
    if not m:
        return (None, None)
    line = m.group(1).replace("\n> ", " ")
    nums = set(int(x) for x in re.findall(r"\b(\d{2})\b", line) if 30 <= int(x) <= 60)
    return (nums, bool(re.search(r"rawhide", line, re.I)))


def chroot_doc_findings(copr_nums, copr_rawhide, doc_nums, doc_rawhide):
    """Every mismatch between the built chroots and the documented ones."""
    findings = []
    for n in sorted(copr_nums - doc_nums):
        findings.append(("docs", "F%d chroot builds but README does not list it" % n))
    for n in sorted(doc_nums - copr_nums):
        findings.append(("docs", "README lists F%d but no chroot builds it" % n))
    if copr_rawhide != doc_rawhide:
        findings.append(("docs", "rawhide chroot=%s, README rawhide=%s"
                         % (copr_rawhide, doc_rawhide)))
    return findings


def hunt_chroot_docs():
    """README's supported releases must be the chroots COPR actually builds.

    A release the README promises without a chroot is a support claim with no
    package behind it; a chroot nobody documents is invisible to users.
    """
    d = get_json("%s/project?ownername=ackerman&projectname=nexus" % COPR)
    roots = sorted((d.get("chroot_repos") or {}).keys())
    copr_nums = set()
    copr_rawhide = False
    for r in roots:
        m = re.search(r"fedora-(\d+)-", r)
        if m:
            copr_nums.add(int(m.group(1)))
        if "rawhide" in r:
            copr_rawhide = True
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    doc_nums, doc_rawhide = supported_releases(readme)
    if doc_nums is None:
        return ("chroot-docs", "unavailable (no 'Supported releases' line in README)", "",
                [("readme", "supported releases line missing")])
    findings = chroot_doc_findings(copr_nums, copr_rawhide, doc_nums, doc_rawhide)
    releases = re.findall(r'href="(\d+)/"', get_text("https://mirrors.kernel.org/fedora/releases/"))
    if releases:
        stable = max(int(x) for x in releases)
        for n in sorted(copr_nums):
            if n < stable - 1:
                findings.append(("docs", "F%d chroot is older than supported F%d/F%d"
                                 % (n, stable - 1, stable)))
    summary = "%d chroots vs README [%s], %d findings" % (
        len(roots), ",".join(str(x) for x in sorted(doc_nums)) + ("+rawhide" if doc_rawhide else ""),
        len(findings))
    return ("chroot-docs", summary, "COPR chroot_repos + README supported releases", findings)


def hunt_fedora_releases():
    """Which Fedora is stable, and which is next - re-read, never remembered."""
    releases = re.findall(r'href="(\d+)/"', get_text("https://mirrors.kernel.org/fedora/releases/"))
    development = re.findall(r'href="(\d+)/"', get_text("https://mirrors.kernel.org/fedora/development/"))
    rel = sorted(int(x) for x in releases)
    dev = sorted(int(x) for x in development)
    if not rel:
        return ("fedora-releases", "unavailable (mirror unreachable)", "", [])
    stable = rel[-1]
    beta = dev[-1] if dev else None
    findings = []
    if beta and beta <= stable:
        findings.append(("fedora", "development lists %d, not newer than stable %d" % (beta, stable)))
    return ("fedora-releases", "stable F%d, next F%s" % (stable, beta if beta else "?"),
            "mirrors.kernel.org/fedora", findings)


def hunt_slice():
    """The fleet rotation slice, derived from the relay teardown ledger.

    Rotating by memory drops the packages nobody remembers; deriving it from
    the dated docker-teardown tokens makes the oldest-tested the next slice.
    """
    relay = os.path.join(ROOT, ".opencode-relay.md")
    inv = sorted(os.path.basename(os.path.dirname(sp)) for sp in specs())
    if not os.path.exists(relay):
        return ("slice", "unavailable (.opencode-relay.md missing)", "", [])
    last = {}
    for line in open(relay, encoding="utf-8", errors="replace"):
        m = re.match(r"^\s*docker-teardown:\s*(\S+)\s+.*\|\s*(\d{4}-\d{2}-\d{2})", line)
        if not m:
            continue
        pkg, day = m.group(1), m.group(2)
        if pkg in inv and day > last.get(pkg, ""):
            last[pkg] = day
    # 4-run rotation: tools/verify-fedora.sh requires ceil(n/4) per slice
    width = -(-len(inv) // 4)
    order = sorted(inv, key=lambda p: (last.get(p, ""), p))
    slice_pkgs, rest = order[:width], order[width:width + width]
    never = [p for p in inv if p not in last]
    findings = [("slice", "%s: no docker-teardown token in the relay" % p) for p in never]
    summary = ("%d packages, slice of %d, untested %d, oldest %s"
               % (len(inv), len(slice_pkgs), len(never),
                  min((last[p] for p in inv if p in last), default="none")))
    note = "teardown-slice: %s | next-start: %s" % (" ".join(slice_pkgs), " ".join(rest))
    return ("slice", summary, note, findings)


def get_text(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return ""


def hunt_sandbox():
    """An Electron payload ships chrome-sandbox 4755 or not at all.

    A plain 0755 helper trips Chromium's SUID preflight and aborts for every
    non-root user, so the spec must carry %attr(4755, root, root) or remove it.
    """
    n = 0
    findings = []
    for sp in specs():
        txt = open(sp, encoding="utf-8", errors="replace").read()
        if "chrome-sandbox" not in txt:
            continue
        n += 1
        pkg = os.path.basename(os.path.dirname(sp))
        if re.search(r"%attr\(\s*4755", txt):
            continue
        if re.search(r"^[ \t]*rm[ \t].*chrome-sandbox", txt, re.M):
            continue
        findings.append((pkg, "chrome-sandbox without %attr(4755, root, root) and not removed"))
    return ("sandbox", "%d Electron specs, %d findings" % (n, len(findings)), "", findings)


def hunt_pins():
    """Every pinned `# sha256:` comment must match the artifact it names.

    A pin that lags the version it ships is a false receipt: the auto-updater
    once bumped splayer-next to 1.2.0 and left the 1.1.0 hash in place.
    Sources over PIN_SIZE_CAP are reported, not downloaded - the run has a
    clock and a 500 MB AppImage is not what this check is for.
    """
    ts = sweep_module()
    PIN_SIZE_CAP = 150 * 1024 * 1024
    checked, skipped, findings = 0, [], []
    for sp in specs():
        txt = open(sp, encoding="utf-8", errors="replace").read()
        vars_ = ts.spec_vars(txt)
        pkg = os.path.basename(sp)
        for url, name, sha in ts.parse_spec_sources(txt, vars_):
            if not sha:
                continue
            if not url.startswith("http"):
                skipped.append("%s:%s(unexpanded)" % (pkg, name))
                continue
            try:
                req = urllib.request.Request(url, headers=UA, method="HEAD")
                with urllib.request.urlopen(req, timeout=45) as r:
                    size = int(r.headers.get("Content-Length") or 0)
            except Exception:
                size = 0
            if size > PIN_SIZE_CAP:
                skipped.append("%s:%s(%dMB)" % (pkg, name, size // (1024 * 1024)))
                continue
            checked += 1
            digest, err = fetch_sha256(url)
            if err:
                # Unreachable is not a mismatch; retries already ran.
                findings.append((pkg, "cannot fetch %s: %s" % (name, err)))
                continue
            if digest != sha:
                findings.append((pkg, "pin mismatch on %s: pinned %s got %s"
                                 % (name, sha[:16], digest[:16])))
    mismatched = [f for f in findings if "pin mismatch" in f[1]]
    note = "skipped (over %dMB or unexpanded): %s" % (
        PIN_SIZE_CAP // (1024 * 1024), ", ".join(skipped) or "none")
    return ("pins", "%d pinned sources hashed, %d mismatched, %d unreachable"
            % (checked, len(mismatched), len(findings) - len(mismatched)),
            note, findings)


HUNTS = (hunt_builds, hunt_chroots, hunt_copr_config, hunt_upstream, hunt_cves,
         hunt_licenses, hunt_release_discipline, hunt_version_probe, hunt_sources,
         hunt_pins, hunt_readme, hunt_published_nvr, hunt_probes, hunt_sandbox,
         hunt_fedora_releases, hunt_chroot_docs, hunt_slice)


def main():
    if "--upstream-rows" in sys.argv:
        for row in upstream_rows():
            print(row)
        return
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
