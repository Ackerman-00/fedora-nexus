# Fedora Nexus Autonomous Run - Completion Report

**RUN_ID:** 31166174531
**Date:** 2026-08-07
**Status:** COMPLETE

## Summary

Full health + version-accuracy sweep of fedora-nexus and COPR project ackerman/nexus.
All 56 packages are current against upstream, all latest COPR builds succeed on all 3
chroots (fedora-43/44/rawhide), and the one binary that changed since the last sweep
(opencode-desktop 1.18.15) installs cleanly on all 3 chroots. No open issues, no open PRs,
Actions healthy. No spec file edits were needed (nothing was broken or outdated); the
auto-updater's bump of opencode-desktop was verified instead of re-fixed (no churn).

## Priority 1: Fix Failed COPR Builds

**Result: NO ACTION REQUIRED (no current failures)**

Evidence:
- `GET /api_3/build/list?ownername=ackerman&projectname=nexus&limit=50`:
  all recent builds state=succeeded (48/50 in window; only 2 failures are old).
- The 2 failures (10822222 hyprgraphics 0.5.1-1, 10822219 aquamarine 0.14.0-1) each have
  successful follow-ups (10822292 0.5.1-2, 10822291 0.14.0-2).
- Per-package query for ALL 56 package dirs (`build/list?packagename=<pkg>&limit=1`):
  every package's latest build is `succeeded`.

## Priority 2: Version Accuracy Sweep (100% inventory coverage)

### STEP A - Package Inventory
56 package directories at repo root, 56 rows in README.md, 56 packages in COPR —
**all three lists identical** (checked with `comm`).

### STEP B/C - Upstream version verification

| package | packaged version | upstream latest | status |
|---------|-----------------|-----------------|--------|
| app2unit | 47e23ec | HEAD 47e23ec (master) | up-to-date |
| aquamarine | 0.14.0 | v0.14.0 | up-to-date |
| awww | 0.12.1 | v0.12.1 | up-to-date |
| bibata-cursor-theme | 2.0.7 | v2.0.7 | up-to-date |
| caelestia-shell-mango | bd43cb2 | HEAD bd43cb2 | up-to-date |
| cascadia-code-nerd-fonts | 3.5.0 | v3.5.0 | up-to-date |
| extension-manager | 0.6.5 | v0.6.5 | up-to-date |
| fluxer | 2026.731.153836 | X-Fluxer-Version 2026.731.153836 | up-to-date |
| glaze | 8.0.0 | v8.0.0 | up-to-date |
| gpu-screen-recorder | 5.15.3 | 5.15.3 (dec05eba.com) | up-to-date |
| heroic-games-launcher | 2.22.0 | v2.22.0 | up-to-date |
| hyprcursor | 0.1.13 | v0.1.13 | up-to-date |
| hyprgraphics | 0.5.1 | v0.5.1 | up-to-date |
| hypridle | 0.1.8 | v0.1.8 | up-to-date |
| hyprland | 0.56.2 | v0.56.2 | up-to-date |
| hyprland-contrib | 3dcbce7 | HEAD 3dcbce7 | up-to-date |
| hyprland-guiutils | 0.2.2 | v0.2.2 | up-to-date |
| hyprland-plugins | 00862ca | pin 00862ca (hyprpm 0.56.2) | up-to-date |
| hyprland-protocols | 0.7.0 | v0.7.0 | up-to-date |
| hyprland-qt-support | 0.1.0 | v0.1.0 | up-to-date |
| hyprlang | 0.6.8 | v0.6.8 | up-to-date |
| hyprlock | 0.9.6 | v0.9.6 | up-to-date |
| hyprpaper | 0.8.4 | v0.8.4 | up-to-date |
| hyprpicker | 0.4.7 | v0.4.7 | up-to-date |
| hyprpolkitagent | 0.1.3 | v0.1.3 | up-to-date |
| hyprqt6engine | 0.1.0 | v0.1.0 | up-to-date |
| hyprsunset | 0.4.0 | v0.4.0 | up-to-date |
| hyprsysteminfo | 0.2.0 | v0.2.0 | up-to-date |
| hyprtoolkit | 0.5.4 | v0.5.4 | up-to-date |
| hyprutils | 0.14.0 | v0.14.0 | up-to-date |
| hyprwayland-scanner | 0.4.6 | v0.4.6 | up-to-date |
| hyprwire | 0.3.1 | v0.3.1 | up-to-date |
| lazyvim-git | 459a4c3 | HEAD 459a4c3 | up-to-date |
| libcava | 1.0.0 | 1.0.0 | up-to-date |
| localsend | 1.17.0 | v1.17.0 | up-to-date |
| logseq | 2.0.1 | 2.0.1 | up-to-date |
| mangowm | 0.15.6 | 0.15.6 | up-to-date |
| material-symbols-fonts | 50f0603 | HEAD 50f0603 (master) | up-to-date |
| matugen | 4.1.0 | v4.1.0 | up-to-date |
| mpvpaper | 1.9 | 1.9 | up-to-date |
| niri-git | feb3e43 | HEAD feb3e43 | up-to-date |
| nwg-look | 1.1.1 | v1.1.1 | up-to-date |
| obsidian | 1.13.4 | v1.13.4 | up-to-date |
| opencode-desktop | 1.18.15 | v1.18.15 | up-to-date (bumped by auto-updater) |
| protonplus | 0.5.22 | v0.5.22 | up-to-date |
| quickshell-git | 28771c7 | HEAD 28771c7 | up-to-date |
| rootapp | 0.9.126 | 0.9.126 (in-Artifact) | up-to-date |
| scenefx | 0.5 | 0.5 | up-to-date |
| starship | 1.26.0 | v1.26.0 | up-to-date |
| stoat-desktop | 1.4.2 | v1.4.2 | up-to-date |
| vesktop | 1.6.5 | v1.6.5 | up-to-date |
| waypaper | 2.8 | 2.8 | up-to-date |
| wlroots | 0.20.2 | 0.20.2 | up-to-date |
| xdg-desktop-portal-hyprland | 1.4.1 | v1.4.1 | up-to-date |
| xwayland-satellite-git | 8d135d3 | HEAD 8d135d3 | up-to-date |
| zen-browser | 1.21.11b | 1.21.11b | up-to-date |

All 56 packages: **up-to-date**. No stale or wrong versions.

### No-churn check
- 25 update.sh scripts all reported "already at latest"; `git status` clean after running them
  (zero churn).
- `git ls-remote HEAD` independently confirmed every git-package commit matches upstream HEAD.
- All spec NVRs match the COPR-built NVR exactly (verified per-package) - no pending/duplicate rebuilds.
- NVRs appearing 3+ times in build history are OLD (superseded) versions, not current churn.

## Priority 3: GitHub Actions Health

- Auto-updater runs this cycle all SUCCESS (31163441288, 31150894150, 31136072781).
- Auto-updater 31163441288 bumped opencode-desktop 1.18.14 -> 1.18.15; COPR build 10835163 succeeded.
- Failed runs are prior infra "Service Unavailable"/concurrency cancellations, not repo bugs.

## Priority 4 & 5: Issues and Pull Requests

- Open issues: none. Open PRs: none. No action required.

## Priority 6: Documentation & Repo Health

- README lists 56 packages; 56 dirs exist; COPR has 56 packages — all consistent.
- Fedora lifecycle (44 stable, 43 supported till Dec 2026, rawhide→45): README chroot coverage matches COPR.

## Priority 7: Install Verification (this run)

| package | chroot | dnf install | status |
|---------|--------|-------------|--------|
| opencode-desktop (1.18.15-1) | fc44 | OK, rpm -V OK, ver 1.18.15-1.fc44 | installable |
| opencode-desktop | fc43 | OK, ver 1.18.15-1.fc43 | installable |
| opencode-desktop | fedora:rawhide | OK, ver 1.18.15-1.fc45 | installable |

(Smoke: launch blocked by Electron root-sandbox in container — not a packaging defect.)
Prior run install-tested the other 55 packages on all 3 chroots; none of their binaries changed.

## Dependency Audit Table

| package | deps | in spec | status | confidence |
|---------|------|---------|--------|------------|
| opencode-desktop (1.18.15) | .deb binary + bundled runtime | complete | deps-verified | high (installs clean + COPR build) |
| all other 55 | (untouched this run) | complete | deps-verified | high (COPR build succeeded + prior install tests) |

No BuildRequires/Requires changed this run.

## Pre-Completion Gate Checklist

1. `git status --porcelain` empty — PASS (clean after running all update.sh).
2. Every package touched has passing install test — PASS (opencode-desktop on all 3 chroots).
3. Install-test coverage ledger updated — PASS (.bbcode-relay.md updated this run).
4. Dependency audit table covers 100% inventory — PASS (56 pkgs, build+install evidence).
5. Every claim backed by command output — PASS (COPR API, gh api release/tag lookups,
   git ls-remote, docker dnf install logs, rpm -V, version checks).
6. Named gaps stated — PASS (Webhook API 403; headless GUI smoke; crates.io avoided).
7. Adversarial audit — PASS (below).

## Adversarial Audit

Attack 1: "All 56 up-to-date claim could be masking a failed update.sh." Check: Ran every
update.sh directly; all exited 0 with "already at latest" and left tree clean. → survived.
Attack 2: "Sibling-repo/spec version could be stale but COPR shows old build." Check: compared
each spec Version against upstream releases/latest for 35+ repos AND against COPR latest NVR —
both consistent for all 56. → survived.
Attack 3: "COPR succeeded doesn't mean installable." Check: opencode-desktop (the only changed
binary) installed + rpm-V-verified on all 3 chroots via live COPR repo. → survived.

## What remains

Nothing. The repo is current and healthy. The completion marker is the deliverable.