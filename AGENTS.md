# AGENTS.md — fedora-nexus

Work-notes for AI agents and humans maintaining this repo.

## Self-healing sweep architecture (added 2026-08-21)

Three-layer defense-in-depth for package staleness and integrity:

### Layer 1: Deterministic Python sweep (`tools/teardown-sweep.py`) — AUXILIARY, NOT VERDICT

Pure stdlib Python helper the **agent calls** (not a separate CI gate). Downloads every
artifact, tears it apart (AppImage extract, .deb control, zip internals, Electron
.asar, `application.ini`, ELF `--version` probe), verifies checksums (only a
minority of Fedora specs pin `# sha256:` today — the rest are
download-verified but unpinned; BLAKE2B+SHA512/SRI paths are cross-repo
heritage in the shared script, not Fedora convention), reads internal
versions, compares against upstream, and (2026-08) runs RPM excellence
checks: `rpmspec -P`, `dnf builddep --assumeno` (spec-dry-build), plus
static RPM323/RPM324 heuristics. `rpm-spec-tool`, `rpmlint` and `rpmdeplint`
are Layer-2 agent tools, NOT run by this script.
The agent IS the teardown — it must tear every package apart itself, produce
the dependency audit table, and ensure excellent .spec. Sweep is evidence,
not a pass-anyway script; CI gate hard-fails if the agent skips it.

Key functions:
- `resolve_canonical_repo()`: detects GitHub forks via API `parent.full_name`,
  compares against canonical upstream (not the fork)
- `is_chromium_build_number()`: filters Chromium engine build numbers
  (first component >= 50) from version probes
- `is_template_version()`: auto-detects RPM macros (%{bumpver}, %{shortcommit0}),
  bash expansions, git snapshots — skips them automatically (no hardcoded lists)
- `versions_match()`: handles both prefix and suffix version alignment
  (e.g. Chromium `143.1.93.137` vs Brave `1.93.137`)
- `staleness_pv()`: strips +build, .git-hash, -r1, ^git, ~beta suffixes
- `repology_newest()`: queries Repology API (120+ repos) for ANY package
- `repology_dep_info()`: gets upstream version + status from Repology
- `osv_query()`: queries OSV.dev for known CVEs on ANY package
- `compute_libyear()`: computes libyear drift from GitHub release dates
- `fix_stale_pkg()`: mechanical auto-fix — sed version in ebuild/spec/nix/template
- `--autofix` flag: when STALE is detected, auto-fix and re-verify

Exit code = the agent's verdict for this sweep run. Exit 0 = all packages
verified. Exit 1 = any FAIL/MISMATCH/STALE/UNVERIFIED. CI does not execute
this script; CI failure issues come from the `cleanup` job in
opencode-schedule.yml.

### Layer 1b: Docker-based install + dependency sweep (`tools/docker-sweep.py`)

Runs INSIDE the agent's execution. For each package:
1. Spins up a clean Docker container (gentoo/stage3, fedora, voidlinux, nixos/nix)
2. Installs the package + all dependencies
3. Verifies all deps resolved (no missing)
4. Runs the binary (if applicable) and checks it starts
5. Reports PASS/FAIL per package

Key features:
- `trivy_scan_image()`: scans base Docker images for CRITICAL/HIGH/MEDIUM CVEs
- `--scan-images` flag: enables Trivy CVE scanning of base layers
- Trivy floor (Sept 2026, OSV GHSA-69fq-xp46-6x23): March 2026 supply-chain
  compromise shipped malicious trivy v0.69.4 / hijacked trivy-action tags /
  DockerHub 0.69.5+0.69.6 images. Require trivy >= 0.72.0 (fixes CVE-2026-55092,
  CVE-2026-63328), verify binary provenance, pin trivy GitHub Actions to
  immutable commit SHAs. Fedora 44 repos still ship 0.69.3 — do NOT treat the
  distro package as safe without checking.
- Works for ANY package type (gentoo, fedora, nix, void, opensuse)

### Layer 2: Agentic self-healing prompt (opencode-schedule.yml PROMPT) — MANDATORY

YOU are the sweep. The coding agent's PROMPT includes a TEAR-APART SWEEP PROTOCOL that
is NOT optional and NOT a pass-anyway script. It must:

1. Tear every .spec + Source0 apart itself (Cargo.toml/meson.build/go.mod vs BuildRequires)
2. Run 2026 toolchain: `rpmspec -P`, `spectool -g`, `rpmbuild -bs`, `dnf builddep --assumeno` (or docker fedora:44), `rpmlint`/`rpmdeplint` — log output. (`rpm-spec-tool` as a standalone binary does not exist in Fedora or on PyPI; the static RPM323/RPM324 checks live in tools/teardown-sweep.py.)
3. Produce the mandatory deliverable `| package | upstream deps | in spec | missing | status |` for ALL packages (derive the count every run via `ls */*.spec | wc -l` — NEVER hardcode it)
   - OSV.dev vulnerability scan (CVEs on pinned version)
   - Repology freshness (outdated vs 120+ repos)
   - Libyear drift (years behind upstream, budget=20yr)
   - Auto-update tool hints (per-package `update.sh`, else update-engine.yml scanner)
4. For each OUTDATED: run the package's `update.sh` (or fix it) to update
5. For each FAIL/MISMATCH: re-download, verify checksum, update if re-released
6. LIBYEAR ENFORCEMENT: if >20 yr, prioritize highest-drift packages
7. Never close a teardown issue without passing sweep + evidence
8. False positive defense: fix the sweep script, never weaken checks

### Layer 3: CI gate + issue auto-open — ENFORCED

`gate_passes()` in `opencode-schedule.yml` hard-checks that
`.opencode-relay.md` on main contains `run_id`, `status: complete`, and
(`PACKAGE.*BR` or `deps-verified` or `dependency audit`), plus per-package
dependency-row counts (see the inline gate) and `tools/verify-fedora.sh`
as the external bar.
If the agent skips the dependency table, the job fails and the next run retries with a stronger model. Cleanup job opens an issue on failure.

### Environment baseline (verified 2026-09-17 via web search — re-discover every run, never hardcode)

- Fedora 44 = current stable (GA 2026-04-28, EOL ~2027-06-02). Fedora 43
  supported, EOL 2026-12-09. Fedora 45 branched 2026-08-11, beta freeze
  2026-08-25, GA scheduled 2026-10-20 (GNOME 51, GCC 16.2, RPM 6.1,
  Python 3.15, OpenSSL 4.0 wave). Rawhide = F46. COPR chroots
  fedora-43/44/45-x86_64 + fedora-rawhide-x86_64 match this — query the
  COPR project API every run.
- RPM 6.0 (F43+, multi-key signing) / 6.1 (F45 beta); rpmlint 2.9–2.10
  current. The Layer 2 toolchain above remains the excellence floor.
- Repology API: bulk clients must send a User-Agent and stay ≤1 req/s.
  OSV.dev `v1/querybatch` takes up to 1000 queries per POST, no auth.
- COPR migrated its file host: `download.fedorainfracloud.org` no longer
  resolves, `download.copr.fedorainfracloud.org` is the live one. Build-log
  links rendered in COPR's own web UI still point at the dead host, so fetch
  logs from the `download.copr.` host. `build/list` rows carry the package name
  in `source_package.name` (nullable, null for a deleted package) and there is
  no top-level `package_name` field.
- `build/list` response envelope changed (found 2026-10-07): it now answers
  `{"items": [...], "meta": {limit, offset, order, ...}}`; the old `{"builds": [...]}`
  key is gone. Read `items` (fall back to `builds` if you must) and page with
  `offset`/`limit` — offset paging returned distinct rows (1288 unique builds
  pulled with limit=200). Treating a missing `builds` key as an empty project
  reads as "no builds at all", which would hide a red newest build.
- SRPM-stage failures (before any chroot task exists) publish their logs under
  `results/<owner>/<proj>/srpm-builds/<buildid>/builder-live.log.gz` on the
  `download.copr.` host — there is no `<chroot>/<buildid>-<pkg>/` directory at
  all, so a per-chroot scan finds nothing for that build. The frontend build page
  is `/coprs/<owner>/<proj>/build/<buildid>/` (singular `build`, not `builds`);
  it lists that log URL. `copr-cli status <id>` gives only the state.
- RPM file downloads on `download.copr.` 301-redirect every `*.rpm` request to
  a `packages.redhat.com/api/pulp-content/public-copr/...` path that 404s
  (observed 2026-10-04; directory layout is
  `<chroot>/<buildid>-<pkg>/<state>/...`, results.json still fetches fine).
  Do not chase RPM files there for install tests: install from the live repo
  in the container instead (`dnf copr enable ackerman/nexus && dnf install
  <pkg>`), which also proves the published repodata carries the NVR. Direct
  results paths that do not end in `.rpm` (build.info, results.json, logs)
  still serve normally.

### OSV.dev query gotchas (found 2026-10-04, both produce false "clean")

- `version` must be TOP-LEVEL, not inside `package`. `{"package": {"name": ...,
  "version": ...}}` is HTTP 400 `invalid query`, not an empty result. Correct
  shape is `{"version": "...", "package": {"name": ...}}`. Both failures below
  are silent: `osv_query()` catches the exception and returns `[]`, so a broken
  query reads identically to "no known CVEs". It now logs the exception - if you
  see `OSV query failed ...` in the sweep output, the scan did NOT run.
- `ecosystem` must be a REAL OSV ecosystem name or be omitted entirely.
  Verified live 2026-10-19: `"Fedora"` and `"Gentoo"` are NOT OSV ecosystems and
  return HTTP 400 `{"code":3,"message":"invalid ecosystem"}`. `ECOSYSTEM_MAP`
  used to map `"fedora": "Fedora"`, so this repo's own repo_type 400'd on EVERY
  query and reported every package clean. Fixed 2026-10-19: gentoo/fedora map to
  `None`. Valid values here: `openSUSE`, `Debian`. Omitting `ecosystem` is legal
  and returns an unscoped (broader, noisier) answer - verified HTTP 200.
- `v1/querybatch` does NOT version-filter for every ecosystem. Asking for
  `crates.io starship 1.19.0` and `1.26.0` returns the identical advisory
  list (CVE-2024-41815, fixed in 1.20.0). Re-check every hit against the
  advisory's own `ranges` events (`introduced` / `fixed` / `last_affected`)
  from `v1/vulns/<id>` before calling a package affected, and confirm the name
  exists in the ecosystem's registry first so a typo cannot read as clean.

### Check criteria that produce false failures (found 2026-10-06)

- `dnf builddep --assumeno <spec>` EXITS 1 whenever a transaction would run, which is the
  normal case for a spec whose BuildRequires are not installed yet. Treating that exit code
  as the pass/fail criterion reported 43 false failures across 70 specs in a clean
  fedora:44 container. The real criterion is the OUTPUT: grep it for `no package matched`,
  `nothing provides`, `no match for argument`, `failed to solve`. With that criterion all 70
  specs resolved; the five that looked unresolved (astal-gjs, astal-gtk4, astal-libs, astal,
  caelestia-shell-mango) are this repo's own -devel packages and resolve as soon as
  ackerman/nexus is enabled, providers proved per package with
  `dnf repoquery --whatprovides`.
- A smoke test must use what the package actually installs, not an assumed name.
  python-yt-dlp-get-pot and python-yt-dlp-get-pot-rustypipe install into the
  `yt_dlp_plugins/extractor/` namespace (they are yt-dlp plugins), so
  `python3 -c 'import yt_dlp_get_pot'` fails with ModuleNotFoundError on a package that is
  perfectly healthy. Read `rpm -qpl <rpm>` first and import the real path.

### COPR dist-git race: a failed build that is not your spec (found 2026-10-04)

Symptom: a COPR build goes to state `failed`, one chroot task has no
`builder-live.log.gz` at all (HTTP 404), and
`https://copr-dist-git.fedorainfracloud.org/per-task-logs/<buildid>.log`
contains

    cmd: ['/usr/share/dist-git/setup_git_package', 'ackerman/nexus/<pkg>'], rc: 128,
    msg: ERROR: Package module ackerman/nexus/<pkg> already exists!

Cause: two builds for the same package land within seconds of each other and
race to create the COPR dist-git module. Nothing in the spec is wrong. 7 of 8
sampled failed builds in this repo's 1074-row history are this race
(wlroots 11027369, fluxer 11004735, openchamber 11066631, concat 11066628,
mixtapes 11065903, cliphist 11065113, freebuff 11054110, python-pydbus
11021893). Fix: resubmit the same NVR. Do not "fix" the spec.

Consequence for audits: a build row's state is failed if ANY chroot task
failed, and its `chroots` list only covers that one build. python-pydbus
0.6.0-4 looks single-chroot on its newest build 11021979, but f43/f45/rawhide
were published by 11021893. Never report a chroot gap from `build/list` rows;
check the published repodata instead
(`<repo>/<chroot>/repodata/repomd.xml` -> `primary.xml.gz`, `name` and
`version` attributes carry the NVR).

### Why the maintainer under-acted despite full access (added 2026-10-19)

Not a permissions problem. The agent had full write access the whole time
and still left real defects unfixed, because the COMPLETION CONTRACT let it
stop early. A blocker only had to be NAMED to be credited: the checklist
asked the agent to "state what you did NOT verify and why", and neither the
inline gate nor `tools/verify-fedora.sh` ever inspected the content of the
gaps section - both only grepped for the PRESENCE of evidence strings. An
agent blocker that was really its own failure (a version regex it could
have fixed, a spec missing a dependency, a stale receipt, a package behind
because it could not work out the new version) counted exactly like a
genuine external blocker. Access answers "can you fix it"; the contract
answers "must you" - and the contract said no.

RULE, enforced in code since 2026-10-19: every gap and HOLD must be a line
starting with the marker, classified as either
`GAP: external - <the external thing that must change first, and why>` or
`GAP: actionable - <what you will fix>`. An `actionable` marker FAILS the
run - it means the work was yours and you did not do it. The gate and the
verifier also fail an unclassified gap line and an `external` marker with
no reason after it. Both catch the legacy `not verified: ...` form too, so a
run cannot escape the contract by using the old wording. A bare heading
ending in `:` and prose that merely mentions the word gap are not
declarations.

CLASSIFYING IS NOT ESCAPING: `external` is a claim you must PROVE with a
command run this run - paste the 403, the 404, the missing asset, the
chroot that has not synced. If you cannot show the probe, it is
`actionable`. These are ACTIONABLE, never external: a version regex or sed
in this repo that cannot match a real upstream tag; a spec missing a
dependency, %license, %attr or arch declaration; a package behind because
the new version could not be worked out (read the artifact's INTERNAL
version - rpm2tree.py, app.asar, application.ini - never the download
filename alone); a dependency floor too high for the chroots you build; a
stale receipt, comment or report.

### Why this architecture

- **Deterministic + intelligent**: the sweep is pure Python (no LLM needed,
  no hallucination, fast). The agent handles complex cases that require
  reasoning about upstream changes.
- **Universal**: works for ANY package — Repology, OSV.dev, GitHub API,
  Trivy. No hardcoded skip lists or package-specific logic.
- **Self-healing**: genuinely stale packages get auto-fixed by the sweep's
  `--autofix` and/or the agent's investigation. False positives get caught
  and the sweep is improved.
- **Proof-or-Stop**: exit code = verdict. No claims without evidence.
  The sweep output is committed to the repo as a receipt.
- **Defense-in-depth**: even if one layer misses, the next catches it.
  Fork detection, template version detection, libyear budget, and
  Trivy CVE scanning prevent the known false positive classes.

## Changelog policy (corrected 2026-10-05 — wipe on version bump is intentional)

`update.sh` scripts rebuild `%changelog` from scratch on a version bump:
`sed -i '/^%changelog/,$d'`, then one entry for the new Version-Release.
That is owner policy, not data loss: the changelog tracks the latest version
only. (Corrects the 2026-10-04 rule, written by an agent, that framed the wipe
as a bug to be repaired.)

- Release bumps within one Version still accumulate entries by hand
  (e.g. concat 0.2.5-1/-2/-3) until the next version bump resets the section.
- Superseded by this policy, do not follow or extend:
  the insert-after-`%changelog` pattern in `freebuff/update.sh` (now the lone
  exception, not the template — leave it; touching it triggers a pointless
  COPR rebuild).
- Done 2026-10-05: repair step removed from `update-engine.yml`,
  `tools/changelog-repair.py` + `tools/test-changelog-repair.py` deleted.

## Electron chrome-sandbox rule (added 2026-10-02, real incident)

Five Electron packages (fluxer, obsidian, logseq, heroic-games-launcher,
splayer-next) shipped `/opt/*/chrome-sandbox` as plain 0755, so Chromium's
SUID-sandbox preflight FATAL-aborted at launch for EVERY non-root user
(`setuid_sandbox_host.cc:166`, "The SUID sandbox helper binary was found, but
is not configured correctly", core dump rc=133) - the apps could not start at
all. Reproduced under `xvfb-run` as a non-root user in a clean fedora:44
container on 2026-10-02 for all five.

RULE for every package that ships an Electron/Chromium binary:
1. `%files` MUST carry `%attr(4755, root, root) <path>/chrome-sandbox`
   (in-repo working references: vesktop, stoat-desktop; same as Google
   Chrome's own rpm), OR deliberately `rm` the helper like rootapp does -
   never ship it as 0755.
2. VERIFY with the launch test, not just rpmbuild:
   `docker run --rm --security-opt seccomp=unconfined ... useradd -m t && su
   t -c "xvfb-run -a <app>"` - expect rc=124 (app stays alive) and zero
   `setuid_sandbox_host` lines. (Without `seccomp=unconfined` even correct
   packages die on docker's namespace restriction - that error is a container
   artifact, the `setuid_sandbox_host` FATAL is the real bug.)
3. `tools/teardown-sweep.py:check_rpm_dependencies` statically flags any spec
   that names chrome-sandbox without the %attr (or an explicit rm).

## Container teardown harness rule (added 2026-10-10, real hit)

When you rebuild a package in a clean container with `rpmbuild -bb`, the
SOURCES dir must contain the package directory's LOCAL files (Patch files,
extra Source files like .desktop / policies.json / wrapper scripts), not just
what `spectool -g` downloads. spectool fetches URL-declared sources only.
COPR never hits this because its SCM clone carries the whole package dir, so
a teardown that fails with "Cannot read ... .patch" or a missing Source1-3 in
%install is a HARNESS bug, not a package bug - check the package dir for
tracked files before touching the spec. Fix: `cp -a <pkgdir>/. SOURCES/`
before running spectool. Hit on wlroots, ly, zen-browser 2026-10-10 (all
three COPR builds were green the whole time).

## Host `rpmspec -P` expansion gotcha (added 2026-10-11, real hit)

`rpmspec -P` on the Ubuntu runner expands `%( ... )` shell macros with
`/bin/sh`, which is dash there, and dash cannot parse the bash-only
`${v//'~'/-}` substitution. wlroots uses exactly that:
`%global tag %(v='%{version}'; echo "${v//'~'/-}")`. On the host the macro
expands to EMPTY, so Source0 reads
`.../-/archive//wlroots-.tar.gz` (curl 404) while `rpmspec -P` still exits 0.
That is a HOST artifact, never a broken Source URL - COPR and the Fedora
containers all expand it to `.../-/archive/0.20.2/wlroots-0.20.2.tar.gz`
(HTTP 200, verified 2026-10-11). The same host run reports nwg-look
(`%gosource`) and protonplus (`%forgesource`/`%forgemeta`) as unexpandable,
because `go-srpm-macros` and `forge-srpm-macros` are not installed there
(the Fedora package is named `go-srpm-macros`; `golang-srpm-macros` does
not exist, verified in fedora:44 2026-10-13).

RULE: any URL or macro expansion check (spectool, curl of Source0, sha256
comparison) must run in a Fedora container with `rpm-build rpmdevtools
forge-srpm-macros go-srpm-macros` installed. On the host, treat an empty
or `.tar.gz`-less expansion as "check in container", not as a finding.

## Harness smoke probes must match what the harness installed (added 2026-10-11, real hit)

A smoke that asserts a compression-specific path (`.../man1/mpvpaper.1.gz`)
fails on the harness-built RPM even when the published COPR RPM ships that
file: bare `rpmbuild -bb` in the container does not always run the brp
compression step that mock/COPR run. Hit on mpvpaper 2026-10-11
(SMOKE_EXIT=1 on the probe, `rpm -ql` from a live `dnf install mpvpaper`
listing `/usr/share/man/man1/mpvpaper.1.gz`, `rpm -V` clean both times).
Probe bug, not a package bug. Write harness smokes with a glob or check the
published package (`dnf install` from the COPR repo) for compression-specific
paths; keep `rpm -V` and `ldd` checks as the real verdict.

## The completion contract was presence-based (found 2026-10-20, real hit)

Run 39415197314 published an install-test table whose 34 verdict cells said
FAIL while its own prose said "47 rows, all PASS" - and 24 of those same
packages carried a same-run `docker-teardown: ... install PASS`. Only 1 of the
47 NVRs was missing from the live repodata, so the FAILs were not install
failures; they were written, not observed. The run was graded green because
`gate_passes()` and `tools/verify-fedora.sh` only grepped for the STRING
"install-test table" - a table full of FAIL passed the gate.

ROOT CAUSE of the under-acting maintainer, in order of weight:
1. The contract measured the PRESENCE of evidence strings, never their truth.
   "status: complete" plus 64 greppable rows was cheaper to produce than one
   real fix, and the cheapest passing strategy wins when the machine only
   counts strings.
2. Nothing counted repairs. A run that found 12 defects and fixed 0 was
   indistinguishable from a run that found 0 - so hunting for defects had no
   payoff in the contract.
3. The authority clause ("do not ask permission, you already have it") was
   prose. Prose is not enforced; only the machine is.
4. The cascade ran deepseek-v4.1-flash-free first: a weak model fills the
   table, it does not reason to a root cause.

RULE (enforced in code since 2026-10-20):
- The gate and the verifier parse the install-test table. ANY verdict cell that
  is not PASS fails the run, unless it is EXTERNAL and a `GAP: external` line
  names that package. A FAIL cell next to a same-run `docker-teardown: ...
  install PASS` fails the run as a contradiction.
- Every run carries `defects-found: N` and `defects-fixed: M`; the gate
  computes M + external_gaps >= N.
- Every run carries at least 5 distinct `hunt: <category> - <what you ran>`
  lines. A category you did not run is a category you did not check.
- A verdict is a transcript of a command, never a summary of a belief.

## Comment policy (owner rule, 2026-10-20)

Comments are short `#topic` labels: one line, a few words, naming a constraint
the code cannot show. No incident narratives, no dated lesson logs, no
restated code, no commented-out code, no banners, no "why this exists"
essays. Keep a comment only when a future maintainer would delete working code
without it (a version floor, the WHY of a pin, a license/SPDX proof, a
harness gotcha). The repo-wide sweep on 2026-10-20 removed ~1800 comment
lines and had to restore 15 of them as one-liners - that is the shape to aim
for: a label, not a story.
