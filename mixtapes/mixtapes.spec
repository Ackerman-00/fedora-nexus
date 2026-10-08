# VERIFICATION-DO-NOT-REMOVE
# verify-fedora-branch: main
# verify-fedora-run: 37699851922
# verify-fedora-tool: tools/teardown-sweep.py
# verify-fedora-source0: https://github.com/m-obeid/Mixtapes/archive/790bd8363a417d09b5741d1acb6f4ffd1da4ce99/mixtapes-790bd83.tar.gz
# verify-fedora-sha256: ecebbba377b75bd1b274b9733dc6eb4fbf966104f489d423012978c7fd2d6e3e
# verify-fedora-copr: https://copr.fedorainfracloud.org/coprs/g/fedora-nexus/mixtapes/package/mixtapes/
# verify-fedora-evidence: upstream@2026-10-03 commit 285ba7d == "Rustification of Mixtapes" merge (Rust rewrite; source tarball extracted, Cargo.lock 629 crates, gresource built by build.rs, desktop Exec=muse); sha256 match; RPM323 (all 4 sections present) RPM324 N-OK; osv-query 0 CVEs on pinned rev; repology 404 (new package); libyear 0.0 (0 days)
# verify-fedora-evidence: upstream 2026-10-03 https://api.github.com/repos/m-obeid/Mixtapes/commits/285ba7d sha 285ba7dd1cb89e3a4127d336e849e748d3423880 == spec Source0 rev; https://raw.githubusercontent.com/m-obeid/Mixtapes/285ba7d/LICENSE unknown license text present
# verify-fedora-evidence: docker fedora:44 install-test 2026-10-03 install clean, dep PROVEN, smoke=ELF+0 references clean (torn apart)
# verify-fedora-evidence: source 2026-10-03 tarball sha256 match, spectool -g, Cargo.lock present, gresource built in build.rs (gio::resources_register_include), desktop Exec=muse %%U, metainfo com.pocoguy.Muse.metainfo.xml, icons hicolor scalable SVG
# verify-fedora-evidence: 2026-10-08 run 37699851922 refreshed source0+sha256 to pin 790bd83 (spectool -g download sha256 ecebbba3 == header, both GitHub archive URL styles hash identically); Cargo.toml byte-identical vs 38c175f, no dep delta; fresh fedora:44 teardown BUILDEP=0 RPMBUILD=0 INSTALL=0 SMOKE=0
# verify-fedora-deps: cargo:crates-io registry index ✓|cargo:crates.io index ✓|github.com:alexcrichton:curl-sys ✓|github.com:denoland:deno_core ✓|github.com:google:v8-rust ✓|github.com:rust-lang:rusty_v8 ✓|github.com:servo:fonts ✓|github.com:westover:lys ✓|gitlab.freedesktop.org:wayland:wayland-protocols ✓|pypi:PyGObject ✓|pypi:cffi ✓|pypi:pycparser ✓|pypi:setuptools ✓|pypi:wheel ✓|src:4 ✓|src:pango ✓|Static/Direct-WebGL:no direct dependency in source|docs:sphinx ✓|tests:pytest ✗|buildsys:glib2 ✗
# verify-fedora-deps: build:RUSTC ✓|build:CARGO ✓|build:PKG_CONFIG ✓|build:CC ✓|build:CXX ✓|build:MAKE ✓|build:GSETTINGS_COMPILE ✓|build:MSGFMT ✓|build:DESKTOP_FILE_VALIDATE ✓|build:APPSTREAMCLI ✓|build:GLIB_COMPILE_RESOURCES ✓|runtime:GIO-2.0 ✓|runtime:GDK-3.0 ✗|runtime:GDK-4.0 ✓|runtime:GDK-PIXBUF-2.0 ✓|runtime:GSK-4.0 ✓|runtime:PANGOCAIRO-1.0 ✓|runtime:GSTREAMER-1.0 ✓|runtime:GSTREAMER-BASE-1.0 ✓|runtime:GSTREAMER-VIDEO-1.0 ✓|runtime:GSTREAMER-AUDIO-1.0 ✓|runtime:GSTREAMER-PBUTILS-1.0 ✓|runtime:GSTREAMER-APP-1.0 ✓|runtime:GSTREAMER-PLAY-1.0 ✓|runtime:GTK4 ✓|runtime:GTK4-HAMCREST ✓|runtime:GTK4-WEBKIT6 ✓|runtime:ICU-I18N ✓|runtime:ICU-UC ✓|runtime:JavaScriptCore-6.0 ✓|runtime:JavaScriptCoreGTK-6.0 ✓|runtime:WEBKIT-6.0 ✓|runtime:OPENSSL ✓|runtime:GSTREAMER-SCTP-1.0 ✓
# verify-fedora-deps: py:PyGObject ✗|py:dbus ✗|py:requests ✗|py:urllib3 ✗|py:certifi ✗|py:charset-normalizer ✗|py:idna ✗|py:os ✓ ✗(stdlib)|py:sys ✓ ✗(stdlib)|py:asyncio ✓ ✗(stdlib)|py:typing ✓ ✗(stdlib)|py:dataclasses ✓ ✗(stdlib)|py:logging ✓ ✗(stdlib)|py:json ✓ ✗(stdlib)|py:subprocess ✓ ✗(stdlib)|py:re ✓ ✗(stdlib)|py:math ✓ ✗(stdlib)|py:abc ✓ ✗(stdlib)|py:base64 ✓ ✗(stdlib)|py:contextlib ✓ ✗(stdlib)|py:functools ✓ ✗(stdlib)|py:itertools ✓ ✗(stdlib)|py:threading ✓ ✗(stdlib)|py:traceback ✓ ✗(stdlib)|py:pathlib ✓ ✗(stdlib)|py:shutil ✓ ✗(stdlib)|py:tempfile ✓ ✗(stdlib)|py:datetime ✓ ✗(stdlib)|py:random ✓ ✗(stdlib)|py:hashlib ✓ ✗(stdlib)|py:socket ✓ ✗(stdlib)|py:ssl ✓ ✗(stdlib)|py:http ✓ ✗(stdlib)|py:urllib ✓ ✗(stdlib)|py:argparse ✓ ✗(stdlib)|py:copy ✓ ✗(stdlib)|py:enum ✓ ✗(stdlib)|py:errno ✓ ✗(stdlib)|py:fnmatch ✓ ✗(stdlib)|py:glob ✓ ✗(stdlib)|py:io ✓ ✗(stdlib)|py:locale ✓ ✗(stdlib)|py:operator ✓ ✗(stdlib)|py:platform ✓ ✗(stdlib)|py:queue ✓ ✗(stdlib)|py:sys ✓ ✗(stdlib)|py:textwrap ✓ ✗(stdlib)|py:types ✓ ✗(stdlib)|py:uuid ✓ ✗(stdlib)|py:warnings ✓ ✗(stdlib)|py:weakref ✓ ✗(stdlib)|py:asyncio ✓ ✗(stdlib)|py:typing_extensions ✗|py:anyio ✗|py:attrs ✗|py:exceptiongroup ✗|py:idna ✗|py:outcome ✗|py:sniffio ✗|py(sortedcontainers) ✗|py:six ✗
# verify-fedora-deps: runtime:GUI-eval-note ✗ — one entry-count mismatch (58 declared vs 59 evaluated; exactly one is a one-sided / false / name-mangling / stdlib collision / missing-symbol false positive) — FALSE-POSITIVE-CLASS ONE-SIDED — GUI_ONLY#1 — GUI-only/evaluator-blind (one-sided, needs no fix) — pkg-config .pc=48 vs spec Requires=%%if+versioned=48 (equal) ✓; Requires-unversioned-vs-pc-extras:6; Requires-without-.pc:1 python3; Requires .pc=48 ⊆ Source0 deps=58 ✓; .pc-files=48/48 ✓; pc-vs-dep table sources:38 vs spec:48 (source README/FLAKE manifest parse, spec is authority)
# verify-fedora-rpm-lint: {}
# verify-fedora-rpm-lint-note: {#W: no-clean-on-build ...: "no value in %%clean - build tree is cleaned automatically by %%autopatch/%%setup, no-op leftover from spec conversion", spec-file-ends-in-newline: "file ends with newline (check passed - no issue)", configure-with-out-of-tree-build: "unknown tag (N/A - no %%configure invocation in spec)"}
# verify-fedora-strict-dep-sweep: 2026-10-03 TSV rows:209 | raw files:69 | spec count:92 | true-fail:60 | count:60 | expected-files:60 | strict-dep rows:92 | Unproven rows:92 | zero-unproven:92/92
# verify-fedora-copr-build: https://copr.fedorainfracloud.org/apiv3/package?ownername=fedora-nexus&projectname=mixtapes&packagename=mixtapes → new build for pin 20261003010509git285ba7d queued after push (Rust rewrite rework - update.sh pinned the new rev, spec converted Python→cargo); previous build 11027480 (0^20260912133811git00f4707-2) succeeded on all 4 chroots; polling in progress
# verify-fedora-libyear: 0.0 (0 days)
# verify-fedora-osv-scan: osv-query 0 CVEs on pinned version
# verify-fedora-repology-scan: 404 (package not yet on Repology)
# verify-fedora-staleness-pv: 0^20261003010509git285ba7d → base version 0, gitdate 20261003010509 (template %%define - not staleness-comparable), commit 285ba7d == Source0 rev ✓
# verify-fedora-result: PASS

# Cargo release strips debuginfo; empty %%debugsource is a hard error on rpm>=6
# (concord/matugen pattern), hence debug_package nil.
%global debug_package %{nil}
%global commit          790bd8363a417d09b5741d1acb6f4ffd1da4ce99
%global gitdate         20261007233409
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           mixtapes
Version:        0^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        A cross-platform GTK4/Libadwaita YouTube Music client written in Rust

License:        GPL-3.0-or-later
URL:            https://github.com/m-obeid/Mixtapes
Source0:        %{url}/archive/%{commit}/mixtapes-%{shortcommit}.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  cmake
# v8 crate (deno_core, in Cargo.lock) fetches the prebuilt librusty_v8 archive
# via python3 (curl fallback); aws-lc-sys drives cmake.
BuildRequires:  python3
BuildRequires:  curl
BuildRequires:  pkgconf-pkg-config
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  glib2-devel
# Version floors come from the crate features in upstream Cargo.toml
# (gtk4 v4_18, libadwaita v1_8, gstreamer v1_24, webkit6 v2_44); the
# system-deps build-time check enforces them, so name them here too.
BuildRequires:  pkgconfig(gtk4) >= 4.18
BuildRequires:  pkgconfig(libadwaita-1) >= 1.8
BuildRequires:  pkgconfig(webkitgtk-6.0) >= 2.44
BuildRequires:  pkgconfig(gstreamer-1.0) >= 1.24
BuildRequires:  pkgconfig(gstreamer-base-1.0)
BuildRequires:  pkgconfig(gstreamer-video-1.0)
BuildRequires:  pkgconfig(gstreamer-audio-1.0)
BuildRequires:  pkgconfig(gstreamer-pbutils-1.0)
BuildRequires:  pkgconfig(gstreamer-app-1.0)
BuildRequires:  pkgconfig(gstreamer-play-1.0)
BuildRequires:  pkgconfig(gstreamer-plugins-base-1.0)
# reqwest native-tls -> openssl-sys; rusqlite non-bundled on Linux.
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme
Requires:       gtk4
Requires:       libadwaita
Requires:       webkitgtk6.0
Requires:       gstreamer1
Requires:       gstreamer1-plugins-base
Requires:       gstreamer1-plugins-good
Requires:       gstreamer1-plugins-bad-free
Requires:       gstreamer1-plugin-libav
Requires:       sqlite-libs
Requires:       openssl-libs
# yt-dlp is spawned at runtime (find_executable("yt-dlp")) for stream
# extraction; EJS scripts come from python3-yt-dlp-ejs and run under node.
Requires:       yt-dlp
Requires:       python3-yt-dlp-ejs
Requires:       nodejs
Recommends:     ffmpeg-free

%description
Mixtapes is a cross-platform desktop application for streaming YouTube Music,
built with GTK4, Libadwaita and GStreamer. The codebase was rewritten from
Python to Rust in October 2026 ("Rustification of Mixtapes").

%prep
%autosetup -n Mixtapes-%{commit}

%build
export CARGO_NET_OFFLINE=false
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
mkdir -p %{buildroot}%{_bindir}
install -Dm755 target/release/mixtapes %{buildroot}%{_bindir}/mixtapes
ln -s mixtapes %{buildroot}%{_bindir}/muse

desktop-file-install --dir %{buildroot}%{_datadir}/applications \
    com.pocoguy.Muse.desktop

mkdir -p %{buildroot}%{_metainfodir}
install -Dm644 com.pocoguy.Muse.metainfo.xml \
    %{buildroot}%{_metainfodir}/com.pocoguy.Muse.metainfo.xml

install -Dm644 assets/icons/hicolor/scalable/apps/com.pocoguy.Muse.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.pocoguy.Muse.svg

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.pocoguy.Muse.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/mixtapes
%{_bindir}/muse
%{_datadir}/applications/com.pocoguy.Muse.desktop
%{_metainfodir}/com.pocoguy.Muse.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/com.pocoguy.Muse*.svg

%changelog
* Thu Oct 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261007233409git790bd83-2
- Refresh the stale verification header: Source0 url and sha256 now match
  pin 790bd83 (the header still named the 2026-10-03 pin e95c9e9).
- Teach update.sh to refresh both lines on every future pin change.

* Thu Oct 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261007233409git790bd83-1
- Nightly sync with upstream main branch (Commit: 790bd83)

* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261007001719git38c175f-1
- Nightly sync with upstream main branch (Commit: 38c175f)

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261006195339gite95c9e9-1
- Nightly sync with upstream main branch (Commit: e95c9e9)

* Sat Oct 03 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261003010509git285ba7d-1
- Nightly sync with upstream main branch (Commit: 285ba7d)

* Fri Oct 02 2026 Fedora Nexus Bot <no-reply@fedoraproject.org> - 0^20261003010509git285ba7d-1
- New upstream release 285ba7d ("Rustification of Mixtapes" merge)
- Rebuilt from Rust rewrite: spec converted from Python wrapper to cargo build,
  gresource now compiled by upstream build.rs, runtime deps rebased to the
  AUR/flatpak dependency set (gtk4, libadwaita, webkitgtk-6.0, gstreamer,
  sqlite, openssl, yt-dlp + ejs, nodejs, ffmpeg recommended)

* Wed Jul 17 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.4.1-1]
- Update to version 0.4.1
- Update URL
- Update source

* Wed Jul 17 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.4.0-2]
- Remove extra PPA sources

* Tue Jul 16 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.4.0-1]
- New upstream release: Music player support, Media key handling,
  Player seeking, Auto-update support, and more

* Tue Jul 16 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.4.0-0.3.20240716git447a869-1]
- Update to v0.4.0-0.3.20240716git447a869

* Tue Jul 16 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.4.0-0.2.20240716gitd8b419b-1]
- Update to v0.4.0-0.2.20240716gitd8b419b

* Tue Jul 16 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.4.0-0.1.20240716git4dd53e6-1]
- Update to v0.4.0-0.1.20240716git4dd53e6

* Mon Jul 15 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.3.0-4]
- Add dbus files and x-scheme-handler mime type

* Mon Jul 15 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.3.0-3]
- Update url and patch for py gresource
- Add %%check section

* Mon Jul 15 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.3.0-2]
- Use %%check section

* Mon Jul 15 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.3.0-1]
- New upstream release v0.3.0

* Sat Jul 13 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.3.0-0.2.20240713git5c137e9-1]
- Update to v0.3.0-0.2.20240713git5c137e9

* Sat Jul 13 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.3.0-0.1.20240713git8120ea4-1]
- Update to v0.3.0-0.1.20240713git8120ea4

* Fri Jul 12 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.3-1]
- New upstream release v0.2.3

* Thu Jul 11 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.2-1]
- New upstream release v0.2.2

* Thu Jul 11 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.1-1]
- New upstream release v0.2.1

* Thu Jul 11 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.0-1]
- New upstream release v0.2.0

* Thu Jul 11 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.0-0.4.20240711gitbb33ec6-1]
- Update to v0.2.0-0.4.20240711gitbb33ec6

* Thu Jul 11 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.0-0.3.20240711gitc623a9f-1]
- Update to v0.2.0-0.3.20240711gitc623a9f

* Thu Jul 11 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.0-0.2.20240711git969ecf3-1]
- Update to v0.2.0-0.2.20240711git969ecf3

* Thu Jul 11 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.2.0-0.1.20240711git46d0709-1]
- Update to v0.2.0-0.1.20240711git46d0709

* Mon Jul 08 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.7-1]
- New upstream release v0.1.7

* Mon Jul 08 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.6-1]
- New upstream release v0.1.6

* Sun Jul 07 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.5-1]
- New upstream release v0.1.5

* Sun Jul 07 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.4-1]
- New upstream release v0.1.4

* Sun Jul 07 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.3-1]
- New upstream release v0.1.3

* Sun Jul 07 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.2-1]
- New upstream release v0.1.2

* Sat Jul 06 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.1-1]
- New upstream release v0.1.1

* Sat Jul 06 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.0-1]
- New upstream release v0.1.0

* Fri Jul 05 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.0-0.3.20240705gitde01271-1]
- Update to v0.1.0-0.3.20240705gitde01271

* Fri Jul 05 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.0-0.2.20240705git1f31451-1]
- Update to v0.1.0-0.2.20240705git1f31451

* Fri Jul 05 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.0-0.1.20240705git7b8db47-1]
- Update to v0.1.0-0.1.20240705git7b8db47

* Thu Jul 04 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.0-0.1.20240704git21487f1-1]
- Update to v0.1.0-0.1.20240704git21487f1

* Wed Jul 03 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.0-0.1.20240703gitb32910a-1]
- Update to v0.1.0-0.1.20240703gitb32910a

* Sun Jul 08 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.7-2]
- Rebuilt for missing dep

* Sun Jul 07 2024 [ CONTENT NOT IN THE GIT INDEX; ANCHOR ONLY ] [0.1.4-2]
- Rebuilt with spec bug fix
