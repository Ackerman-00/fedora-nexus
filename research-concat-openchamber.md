# Research: Concat + OpenChamber packaging decisions (Fedora COPR / fedora-nexus)

Scope per request. All claims cited to primary sources. Local artifact checks were run in
`/tmp/opencode/concat-verify/`; downloaded file sha256s matched the GitHub-published digests exactly.

## 1. Concat v0.2.5 — exact .rpm requires, install paths, scripts

Upstream builds one nfpm description for both .deb and .rpm from the same staged folder:
[assets/linux/nfpm.yaml @ v0.2.5](https://raw.githubusercontent.com/jub0t/Concat/v0.2.5/assets/linux/nfpm.yaml)
and [.github/workflows/build-app.yml @ v0.2.5](https://raw.githubusercontent.com/jub0t/Concat/v0.2.5/.github/workflows/build-app.yml)
(`ubuntu-22.04` / `ubuntu-22.04-arm` runners, lines 104/113; nfpm v2.47.0).

Declared rpm depends (nfpm.yaml `overrides.rpm.depends`): `gtk3, fontconfig, freetype,
libxkbcommon, mesa-libGL, alsa-lib` — **no `libc` entry** (only the deb path lists `libc6`).

Verified by parsing the actual release RPM
(`Concat-0.2.5-linux-x86_64.rpm`, sha256 `48cfca1b864b58799b0642b847d7ac13e2b35c6841235ec73480d1ebc697c950`,
matches [release asset digest](https://api.github.com/repos/jub0t/Concat/releases/tags/v0.2.5)):
- Header Name-version-release: `concat-0.2.5-1.x86_64`, vendor "Concat contributors", license AGPL-3.0-or-later.
- **No %pre/%post/%preun/%postun scripts** (verified: no script tags in header).
- Requires (exact): `gtk3, fontconfig, freetype, libxkbcommon, mesa-libGL, alsa-lib`.
- File list (mode/size/path):
  - `0755 /opt/concat/concat` (98 MB)
  - `/opt/concat/lib/` — FFmpeg 7.1 + onnxruntime, symlinks plus real libs (`libavcodec.so.62.28.103`, `libonnxruntime.so.1.28.0`, …)
  - `0755 /usr/bin/concat` (shell script: `exec /opt/concat/concat "$@"`)
  - `0644 /usr/share/applications/concat.desktop`
  - `0644 /usr/share/icons/hicolor/256x256/apps/concat.png`
  - `0644 /usr/share/doc/concat/LICENSE`, `.../THIRD_PARTY_NOTICES.md`

Desktop entry staged by the workflow (`cat > stage/$name/concat.desktop` heredoc):
```
[Desktop Entry]
Type=Application
Name=Concat
Comment=Video editor
Exec=concat
Icon=concat
Categories=AudioVideo;Video;
Terminal=false
```
Package post-processing rewrites `Exec=concat` → `Exec=/opt/concat/concat %U`
([build-app.yml](https://raw.githubusercontent.com/jub0t/Concat/v0.2.5/.github/workflows/build-app.yml));
the installed desktop file in the RPM confirms this rewrite.
Binary links only its own bundle and base system: `readelf -d` shows `RPATH $ORIGIN/lib`,
DT_NEEDED includes `libavcodec/libavutil/libavformat/...` (found in lib/), plus system
`libstdc++, libm, libasound, libfontconfig, libfreetype, libgcc_s, libc, ld-linux` — matching the
nfpm depends list. (Upstream states the same design in the nfpm.yaml comment block.)

Repack decision support: an upstream-built .rpm already ships (135,350,440 B x86_64,
`48cfca…`; 123,876,914 B aarch64, `f3d699…`), extractable/repackable fluxer-style.

## 2. Concat has NO Chromium/Electron component — Electron sandbox rule does not apply

Evidence (primary):
- nfpm.yaml file list has no `chrome-sandbox`, no Electron/CEF paths
  ([nfpm.yaml](https://raw.githubusercontent.com/jub0t/Concat/v0.2.5/assets/linux/nfpm.yaml)).
- Full repo tree @ v0.2.5 (856 entries) contains no `chrome-sandbox`, no electron/CEF files; the
  only "chrome" paths are the effect package `concat.classic-chrome` and `ui/demo/editor-chrome.slint`
  ([tree API](https://api.github.com/repos/jub0t/Concat/git/trees/v0.2.5?recursive=1)).
- Build workflow greps: 0 hits for electron/chromium/chrome/sandbox/cef/tauri/wry/webview/webkit/postinst
  ([build-app.yml](https://raw.githubusercontent.com/jub0t/Concat/v0.2.5/.github/workflows/build-app.yml)).
- UI is Slint 1.17 (Cargo comment and [discussion #24](https://github.com/jub0t/Concat/discussions/24):
  "Migrated to Slint" — the older Tauri/WebKitGTK frontend was replaced; WebKitGTK was cited as the
  reason). No bundled web engine: the workflow only bundles FFmpeg + onnxruntime.
- Local: `rpmdump` of the release RPM shows no `chrome-sandbox` file.

Conclusion: the repo's Electron SUID-sandbox rule (%attr 4755 or explicit rm) is provably not
triggered by Concat. (Historical note only: the old Tauri build used WebKitGTK — issues/31,
[discussion #24](https://github.com/jub0t/Concat/discussions/24) — but Tauri/WebKitGTK does not ship
Chromium's SUID sandbox.)

## 3. OpenChamber v2.1.0 Linux AppImage hashes (GitHub digests + local re-verification)

From [release API v2.1.0](https://api.github.com/repos/openchamber/openchamber/releases/tags/v2.1.0)
(published assets created 2026-10-01):
- x86_64: `https://github.com/openchamber/openchamber/releases/download/v2.1.0/OpenChamber-2.1.0-linux-x86_64.AppImage`
  size 273,277,509 B, sha256 `ab4f20fc7c17ccbcbe720cfcbbbabd0b592c19d8e7ebe0663d7cb3f918a082f2`
- arm64: `https://github.com/openchamber/openchamber/releases/download/v2.1.0/OpenChamber-2.1.0-linux-arm64.AppImage`
  size 275,880,448 B, sha256 `d8a50320b43287048fa55f918d7e695f37797a56539f1323c9314e74418ae083`

Locally downloaded x86_64 file: sha256 `ab4f20fc…` — matches GitHub digest exactly.
No `.rpm`/`.deb` among the 25 release assets (AppImage is the only Linux package).
Upstream packaging config: [packages/electron/package.json @ v2.1.0](https://raw.githubusercontent.com/openchamber/openchamber/v2.1.0/packages/electron/package.json)
— electron-builder `^26.0.0`, electron `^43.7.0`, `linux.target: ["AppImage"]`,
`appId: dev.openchamber.desktop`.

**Sandbox rule confirmation (local extraction of the AppImage, `--appimage-extract`):**
`chrome-sandbox` ships as mode **0755** (not SUID), and the bundled desktop file sets
`Exec=AppRun --no-sandbox %U`. So the mandatory `%attr(4755)` fix (or deliberate removal) must be
applied on repack; the AppImage only works because it self-disables the sandbox.

## 4. COPR input size limit (~273 MB AppImage in an SRPM is fine)

No documented numeric limit for SRPM/source uploads; production Fedora COPR allows 10 GiB per
request. Primary source: Fedora Infra ansible, COPR frontend vhost:
[roles/copr/frontend/templates/httpd/coprs.conf @ main](https://raw.githubusercontent.com/fedora-infra/ansible/main/roles/copr/frontend/templates/httpd/coprs.conf):
- upload-handling locations `/api.*upload.*` and `/coprs.*new_build_upload.*` set
  `LimitRequestBody 10737418240` (10 GiB).
- COPR docs: upload paths are [Direct Upload](https://docs.copr.fedorainfracloud.org/user_documentation.html#direct-upload)
  (spec/SRPM locally) or [URLs](https://docs.copr.fedorainfracloud.org/user_documentation.html#urls)
  (SRPM hosted publicly); `copr-cli` has no size check ([cli/copr_cli/main.py](https://raw.githubusercontent.com/fedora-copr/copr/main/cli/copr_cli/main.py),
  no size constant; `DEFAULT_CONFIG` has no limit).
- Related build limits from the same docs page: default build timeout 5 h, COPR instance max 50 h.

Practical note for repack: a ~273 MB AppImage inside an SRPM (~273+ MB uploaded, well under 10 GiB)
is acceptable; keep it as one big source/SRPM or fetch upstream in a `.copr/Makefile` srpm target —
both are documented methods on the same page.

## 5. Fedora 43 EOL + COPR chroot grace

- Official schedule ([fedorapeople f-43 key tasks](https://fedorapeople.org/groups/schedule/f-43/f-43-key-tasks.html),
  GPG-signed Fedora schedule): "Fedora Linux 43 End of Life — Wed 2026-12-09", marked changeable,
  based on the Early Target Date.
- [endoflife.date/fedora](https://endoflife.date/fedora) (API `eolFrom` 2026-12-09) agrees exactly:
  **no conflict**; F43 security support ends 2026-12-09. (F44: 2027-06-02.)
- COPR EOL chroot policy ([Outdated chroots removal policy](https://docs.copr.fedorainfracloud.org/copr_outdated_chroots_removal_policy.html)):
  when a distro EOLs, its chroots are disabled after a small "adjustment period of undocumented
  length"; existing build results are preserved **180 days after chroot disablement**, and any
  project admin can suppress removal or reset the 180-day clock at any moment (unlimited extension).
- Operational detail ([How to manage chroots](https://docs.copr.fedorainfracloud.org/how_to_manage_chroots.html)):
  EOL marking sets a `delete_after` timestamp; notification and deletion are daily cron commands.

Implication: after 2026-12-09, fedora-43-* builds stop before results are deleted; the 180-day
window can be extended deliberately, so dropping f43 is a policy choice, not forced by storage loss.

## 6. Upstream Fedora/COPR guidance — none exists; no duplicate work

- No Fedora/Copr mention in README, CONTRIBUTING, CHANGELOG, ARCHITECTURE, SECURITY, or the bug
  template @ v0.2.5 (keyword scans; e.g. [README](https://raw.githubusercontent.com/jub0t/Concat/v0.2.5/README.md)).
- No wiki content (GitHub wiki has no pages; wiki URL returns the repo shell).
- Issue/discussion search: `fedora` → 0 relevant; `copr` → 0; `rpm` → issue #149
  ("Linux/rpm - Bug: Lags, Unstable, etc.") which is a runtime-quality report, not packaging guidance.
  AUR packaging discussions exist via [PR #23](https://github.com/jub0t/Concat/pull/23) (Arch PKGBUILD,
  by a community member) and Flatpak/Discussions #71; none mention RPM/COPR policy.
- No third-party Copr project or Fedora package exists: COPR search API `query=concat` returns 23
  projects, none named concat ([API](https://copr.fedorainfracloud.org/api_3/project/search?query=concat));
  `query=openchamber` returns none; Fedora dist-git API for `concat*`/`openchamber*` returns no projects
  ([src.fedoraproject.org API](https://src.fedoraproject.org/api/0/projects?pattern=concat*)).
- Relevant upstream policy that does exist:
  [TRADEMARK.md](https://raw.githubusercontent.com/jub0t/Concat/v0.2.5/TRADEMARK.md) explicitly permits
  "**Package Concat for a distribution** (Nix, Homebrew, AUR, Debian, Flatpak…) from unmodified upstream
  source, keeping the name — patches confined to packaging, paths and build flags are fine."
  An RPM repack of upstream unmodified release is within this grant.
- Repology ([API](https://repology.org/api/v1/project/concat)): existing channel is AUR
  (`concat`, `concat-bin`, `concat-git` at 0.2.5) + chocolatey 0.2.4; no RPM-based repo tracks it.

## Extra verified facts (decision support, all primary)

- Concat upstream rpm x86_64 sha256 `48cfca…`, aarch64 `f3d699…` from the release API above; the
  x86_64 artifact was downloaded and header-inspected in full (section 1). The bundled FFmpeg is 7.1
  (`libavcodec.so.62`, `avcodec 62.28.103`), onnxruntime 1.28.0.
- Concat build host is `ubuntu-22.04` (glibc 2.35), confirming the portability concern motivating repack.
- OpenChamber v2.1.0 x86_64 AppImage contains `chrome-sandbox` mode 0755 + desktop `--no-sandbox`
  (local extraction, section 3); asset sha256 re-verified locally.

## Not verified / caveats

- COPR `LimitRequestBody` is from Fedora Infra ansible (production config); the COPR user docs do
  not state a numeric limit. Treat 10 GiB as infra-derived, not a documented policy number.
- The exact length of COPR's "adjustment period" before EOL chroots are disabled is explicitly
  undocumented (policy page says so); only the 180-day post-disablement retention is documented.
- Concat `.rpm` payload contents were verified from the v0.2.5 release RPM and nfpm.yaml only; no
  build was performed locally (per machine policy), and the Fedora 43 schedule EOL date is
  self-described as changeable.
