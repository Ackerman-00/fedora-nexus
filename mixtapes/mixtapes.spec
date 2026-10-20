# verify-fedora-source0: https://github.com/m-obeid/Mixtapes/archive/618c24c3abfb12266825a4373155f26e9abbff36/mixtapes-618c24c.tar.gz
# verify-fedora-sha256: a09276af07e80fcdeb84398807c184ef29d34120e23e6cdc3be8c0af78c2d37f

# debug_package nil: empty debugsource errors on rpm>=6.
%global debug_package %{nil}
%global commit          618c24c3abfb12266825a4373155f26e9abbff36
%global gitdate         20261019181359
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           mixtapes
Version:        0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
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
# v8 fetches librusty_v8 via python3; aws-lc-sys needs cmake.
BuildRequires:  python3
BuildRequires:  curl
BuildRequires:  pkgconf-pkg-config
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  glib2-devel
# Version floors mirror upstream crate features.
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
# yt-dlp spawned at runtime; EJS runs under node.
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
* Mon Oct 19 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261019181359git618c24c-1
- Nightly sync with upstream main branch (Commit: 618c24c)

* Sun Oct 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261011192142git1b5f1e8-1
- Nightly sync with upstream main branch (Commit: 1b5f1e8)

* Sun Oct 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261011154526gitd8cfa4e-1
- Nightly sync with upstream main branch (Commit: d8cfa4e)

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
