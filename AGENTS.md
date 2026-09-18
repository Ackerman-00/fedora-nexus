# AGENTS.md — fedora-nexus

Work-notes for AI agents and humans maintaining this repo.

## Self-healing sweep architecture (added 2026-08-21)

Three-layer defense-in-depth for package staleness and integrity:

### Layer 1: Deterministic Python sweep (`tools/teardown-sweep.py`) — AUXILIARY, NOT VERDICT

Pure stdlib Python helper the **agent calls** (not a separate CI gate). Downloads every
artifact, tears it apart (AppImage extract, .deb control, zip internals, Electron
.asar, `application.ini`, ELF `--version` probe), verifies checksums (Fedora
specs pin `# sha256:`; BLAKE2B+SHA512/SRI paths are cross-repo heritage in the
shared script, not Fedora convention), reads internal versions, compares against upstream, and
(2026-08) runs RPM excellence checks: `rpmspec -P`, `dnf builddep --assumeno`
(spec-dry-build), `rpm-spec-tool` RPM320-324, `rpmlint`/`rpmdeplint` hooks.
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

Exit code = verdict. Exit 0 = all packages verified. Exit 1 = any
FAIL/MISMATCH/STALE/UNVERIFIED → CI opens an issue.

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
2. Run 2026 toolchain: `rpmspec -P`, `spectool -g`, `rpmbuild -bs`, `dnf builddep --assumeno` (or docker fedora:44), `rpmlint`/`rpmdeplint`, `rpm-spec-tool` RPM320-324 — log output
3. Produce the mandatory deliverable `| package | upstream deps | in spec | missing | status |` for ALL packages (94 specs as of 2026-09-17 — derive via `ls */*.spec | wc -l`, NEVER hardcode the count)
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

`gate_passes()` in `opencode-schedule.yml` now hard-checks that
`.opencode-relay.md` on main contains `run_id` + `status: complete` + `PACKAGE.*BR.*Req` / `deps-verified` / `dependency audit`.
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
