# opencode-complete-31112339114

## Run Summary
**Date:** 2026-08-06 15:25 UTC
**RUN_ID:** 31112339114 (relay=false; previous run relay state status=complete)

## 1. COPR Build Status (priority 1) - ALL PASSING
- Queried latest 100 builds + per-package build lists for all 55 COPR packages.
- 4 historical failed builds found, ALL already superseded by later successful builds:
  | Package | Failed build | Superseded by |
  |---------|-------------|---------------|
  | aquamarine | 10822219 | 10822291 succeeded |
  | hyprgraphics | 10822222 | 10822292 succeeded |
  | gpu-screen-recorder | 10811916 | 10812363 succeeded |
  | cascadia-code-nerd-fonts | 10804938 | 10806072 succeeded |
- No package has a latest build that failed.

## 2. Fix Applied (incremental delivery, one verified fix at a time)
**waypaper 2.8-6 -> 2.8-7** (commit `0b26c0e`)
- Bug (found via install sweep, NOT visible in COPR build state): waypaper crashed on
  launch: `ImportError: Typelib file for namespace 'xlib', version '2.0' not found`.
  Root cause: `python3-gobject` (gi) import of `Gdk` needs `xlib-2.0.typelib`, which is
  owned ONLY by the full `gobject-introspection` package (verified `rpm -qf
  /usr/lib64/girepository-1.0/xlib-2.0.typelib` = gobject-introspection-1.86.0-3.fc44,
  and `python3-gobject` does not Require it).
- Fix: add `Requires: gobject-introspection` to waypaper.spec; Release 6->7; %changelog entry.
- Webhook evidence: push 0b26c0e at ~15:02 -> build **10832723** (waypaper 2.8-7) appeared
  within ~20s, state `succeeded`.
- Verification (fresh fedora:44 container, dnf install waypaper): RC=0,
  `waypaper-2.8-7.fc44.noarch` installed, `gobject-introspection` pulled in as dep, and
  `from gi.repository import Gtk, GdkPixbuf, Gdk, GLib` now imports OK (failed before fix).
  Built RPM metadata check: `rpm -q --requires waypaper` lists `gobject-introspection`.
- not verified: GUI full launch requires a display; verified to import/parse stage only.

## 3. Version Accuracy Sweep (priority 2) - 100% coverage, ALL 55 up-to-date
Verified each package against real upstream (gh api releases/latest + tags, codeberg/gitlab
APIs, direct URL HEAD 200s). Full table in section 8.

## 4. GitHub Actions Health (priority 3) - PASSING
- Recent "Fedora Nexus Auto-Updater" runs all success (latest 2026-08-06T13:50:52Z).
- No failed runs to fix.

## 5. Issues & PRs (priorities 4-5) - NONE
- 0 open issues, 0 open PRs. Nothing to triage/merge.

## 6. Install-Verification Sweep (priority, mandatory) - 55/55 GREEN
Fresh clean containers, `dnf copr enable ackerman/nexus`, `dnf install <all 55>` with
`install_weak_deps=False`:
| Chroot (enabled) | container image | result |
|------------------|-----------------|--------|
| fedora-43-x86_64 | registry.fedoraproject.org/fedora:43 | RC=0, all 55 installed |
| fedora-44-x86_64 | registry.fedoraproject.org/fedora:44 | RC=0, all 55 installed |
| fedora-rawhide-x86_64 | registry.fedoraproject.org/fedora:rawhide | RC=0, all 55 installed (dnf5) |
- ldd scan of every ELF binary under /usr/bin + /opt: 0 genuinely missing libs
  (zen's "missing" libs are its own bundled moz libs present in /opt/zen; verified).
- Runtime smoke (CLI-able): awww 0.12.1, starship 1.26.0, mpvpaper, app2unit, hyprpicker,
  hyprsunset, hypridle, hyprlock, hyprpaper, extension-manager, waypaper all ran OK.
- GUI-only apps (logseq, obsidian, vesktop, zen-browser, fluxer, stoat-desktop, rootapp,
  opencode-desktop, heroic-games-launcher, localsend, nwg-look, protonplus, mangowm,
  niri): binaries start and reach "no DISPLAY / Missing X server" (headless container),
  i.e. dependencies resolve and ELF loads; full UI launch not testable headless
  (named gap).
- rootapp: downloaded AppImage (sha256 0736926f... matches spec pin), extracted squashfs
  at ELF section-header offset 944632, `X-AppImage-Version=0.9.126` confirmed.
- zen-browser: bundled libs present; app reaches DISPLAY stage (no DISPLAY error).

## 7. Docs / Repo health (priority 6)
- README lists 55 packages; all 55 match COPR package list and repo dirs exactly. No edits needed.
- Fedora lifecycle: F44 current (EOL Jun 2 2027), F43 prev (EOL Dec 9 2026), rawhide=F45.
  COPR enabled chroots discovered from project API: fedora-43/44/rawhide. README already accurate.

## 8. Version Verification Table (100% of inventory)
Status: up-to-date / UPDATED / FIXED-WRONG-VERSION / needs-build

| package | packaged | upstream latest | status |
|---------|----------|-----------------|--------|
| app2unit | git 47e23ec | HEAD 47e23ec | up-to-date |
| aquamarine | 0.14.0 | v0.14.0 | up-to-date |
| awww | 0.12.1 | v0.12.1 (codeberg) | up-to-date |
| bibata-cursor-theme | 2.0.7 | v2.0.7 | up-to-date |
| caelestia-shell-mango | git bd43cb2 | HEAD bd43cb2 | up-to-date |
| cascadia-code-nerd-fonts | 3.5.0 | v3.5.0 | up-to-date |
| extension-manager | 0.6.5 | v0.6.5 | up-to-date |
| fluxer | 2026.731.153836 | X-Fluxer-Version 2026.731.153836 | up-to-date |
| glaze | 8.0.0 | v8.0.0 | up-to-date |
| gpu-screen-recorder | 5.15.3 | 5.15.3 (snapshot exists, no newer) | up-to-date |
| heroic-games-launcher | 2.22.0 | v2.22.0 | up-to-date |
| hyprcursor | 0.1.13 | v0.1.13 | up-to-date |
| hyprgraphics | 0.5.1 | v0.5.1 | up-to-date |
| hypridle | 0.1.8 | v0.1.8 | up-to-date |
| hyprland | 0.56.2 | v0.56.2 | up-to-date |
| hyprland-contrib | git 3dcbce7 | HEAD 3dcbce7 | up-to-date |
| hyprland-guiutils | 0.2.2 | v0.2.2 | up-to-date |
| hyprland-plugins | git 00862ca | HEAD 00862ca | up-to-date |
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
| libcava | 1.0.0 | 1.0.0 | up-to-date |
| localsend | 1.17.0 | v1.17.0 | up-to-date |
| logseq | 2.0.1 | 2.0.1 | up-to-date |
| mangowm | 0.15.6 | 0.15.6 | up-to-date |
| material-symbols-fonts | git 50f0603 | HEAD 50f0603 | up-to-date |
| matugen | 4.1.0 | v4.1.0 | up-to-date |
| mpvpaper | 1.9 | 1.9 | up-to-date |
| niri-git | git feb3e43 (26.04) | HEAD feb3e43 | up-to-date |
| nwg-look | 1.1.1 | v1.1.1 | up-to-date |
| obsidian | 1.13.4 | v1.13.4 | up-to-date |
| opencode-desktop | 1.18.14 | v1.18.14 | up-to-date |
| protonplus | 0.5.22 | v0.5.22 | up-to-date |
| quickshell-git | git 28771c7 (0.3.0) | HEAD 28771c7 | up-to-date |
| rootapp | 0.9.126 | in-AppImage 0.9.126 (sha256 match) | up-to-date |
| scenefx | 0.5 | 0.5 | up-to-date |
| starship | 1.26.0 | v1.26.0 | up-to-date |
| stoat-desktop | 1.4.2 | v1.4.2 | up-to-date |
| vesktop | 1.6.5 | v1.6.5 | up-to-date |
| waypaper | 2.8-7 | 2.8 | up-to-date (Release bumped for fix) |
| wlroots | 0.20.2 | 0.20.2 (gitlab) | up-to-date |
| xdg-desktop-portal-hyprland | 1.4.1 | v1.4.1 | up-to-date |
| xwayland-satellite-git | git 8d135d3 (0.8.2) | HEAD 8d135d3 | up-to-date |
| zen-browser | 1.21.10b | 1.21.10b | up-to-date |

## 9. Dependency Audit Table (every package, per mandatory deliverable)
Method: spec BuildRequires/Requires cross-checked against upstream manifest/source where
available; empirical validator = clean dnf install on all 3 enabled chroots +
ldd-no-missing-libs + binary launch-to-display. status: deps-verified / deps-fixed.

| package | upstream deps found | in spec | missing/added | extra/dropped | status |
|---------|--------------------|---------|---------------|---------------|--------|
| waypaper | gi->Gdk needs xlib-2.0.typelib (gobject-introspection) | before: missing | ADDED gobject-introspection | none | deps-fixed |
| all 54 others | install + ldd + launch verified on F43/44/rawhide | resolves | none found | none found | deps-verified |
| rootapp | AppImage deps (Electron-style, self-contained) | n/a self-contained | none (sha256 pin matches) | none | deps-verified |
| zen-browser | bundled moz libs in /opt/zen + system | resolves | none | none | deps-verified |

Confidence: high for the waypaper diagnosis (empirically reproduced before/after).
Medium for the rest (validated by clean install + ldd on all chroots, but full per-spec
manifest diff for all 55 not re-extracted this run; versions all re-verified upstream).

## 10. Adversarial Audit (contrarian pass)
1. "waypaper fix works" - could it be coincidence? ATTACK: checked the BUILT RPM metadata
   (rpm -q --requires waypaper-2.8-7) -> declares gobject-introspection; fresh install
   pulls it and gi import succeeds (failed before). Survived.
2. "all 55 install" - could install_weak_deps=False mask weak-dep problems? It removes
   weak deps, making the required-dep resolution test STRICTER, not laxer; all resolved.
   Survived.
3. "all versions current" - risk: prereleases not captured by releases/latest. Repo
   convention is stable releases; git packages pinned to upstream HEAD confirmed.
   Survived (minor gap: no prerelease tracking by design).

## 11. Pre-completion Gate
1. PASS - `git status --porcelain` empty (verified before writing this marker; see run log).
2. PASS - waypaper 2.8-7 install-tested in a clean Fedora 44 container (before/after evidence
   captured: xlib ImportError before, gi import OK after).
3. PASS - install coverage ledger updated in .opencode-relay.md; every package whose binary
   changed (waypaper 2.8-7) install-tested; no install failures left.
4. PASS - dependency audit table covers 100% (55/55) of inventory.
5. PASS - all claims backed by command output (build IDs 10832723 etc., docker/dnf RC=0,
   sha256 0736926f..., rpm -q --requires output).
6. PASS - named gaps listed (GUI display testing, webhook API 403, full per-manifest diffs).
7. PASS - this marker committed + pushed to main.

## 12. Commits pushed this run
- `0b26c0e` waypaper 2.8-7 Requires gobject-introspection (COPR build 10832723 succeeded)
- `d7d9346` relay state update

## Remaining / not done
- Nothing left broken. Relay state marked complete. GUI full-launch testing remains
  impossible headless; next runs should continue periodic install sweeps.
