# These will be automatically populated by update.sh
# No debuginfo: pure Python sources + data, zero ELF binaries, so
# find-debuginfo emits an empty debugsource list which rpm >= 6 rejects
# as a hard error (proven by COPR build 10955014).
%global debug_package %{nil}
%global commit          c48756eebd836850eb0ee60991deb71b52e46ee1
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260904205500

Name:           mixtapes
Version:        0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Modern, Linux-first YouTube Music player (Nexus Git Snapshot)

License:        GPL-3.0-or-later
URL:            https://github.com/m-obeid/Mixtapes
Source0:        %{url}/archive/%{commit}/Mixtapes-%{shortcommit}.tar.gz

BuildRequires:  desktop-file-utils
BuildRequires:  glib2-devel
BuildRequires:  python3-devel

# Python runtime modules (requirements.txt). python3-ytmusicapi,
# python3-yt-dlp-ejs, python3-yt-dlp-get-pot(+rustypipe), python3-pydbus
# and python3-mprisify are Nexus-packaged (missing from Fedora proper);
# StrEnum is stdlib on Fedora's Python (>= 3.11) and needs no package.
Requires:       python3
Requires:       python3-gobject
Requires:       python3-numpy
Requires:       python3-ytmusicapi
Requires:       yt-dlp
Requires:       python3-yt-dlp-ejs
Requires:       python3-yt-dlp-get-pot
Requires:       python3-yt-dlp-get-pot-rustypipe
Requires:       python3-requests
Requires:       python3-urllib3
Requires:       python3-mutagen
Requires:       python3-pillow
Requires:       python3-pydbus
Requires:       python3-mprisify
# GTK/Adwaita/WebKit/GStreamer runtime (mirrors upstream README Fedora
# line + the nix packaging: webkit powers the in-app login browser,
# glib-networking its TLS, gst plugins audio playback)
Requires:       gtk4
Requires:       libadwaita
Requires:       webkitgtk6.0
Requires:       glib-networking
Requires:       gstreamer1-plugins-base
Requires:       gstreamer1-plugins-good
Requires:       gstreamer1-plugins-bad-free
Requires:       gstreamer1-plugins-ugly-free
Requires:       ffmpeg-free
Requires:       nodejs
Requires:       rustypipe-botguard
Requires:       hicolor-icon-theme

%description
Mixtapes (formerly Muse) is a modern, Linux-first YouTube Music player
built with GTK4 and Libadwaita: library/playlists/search, full
playback with downloads, MPRIS, scrobbling and background playback.
Packaged for the Nexus repository from a Git snapshot following the
upstream flake.nix build (Python + GResource bundle).

%prep
%autosetup -n Mixtapes-%{commit}

%build
# Compile the GResource bundle (mirrors upstream start.sh, also done by
# the nix packaging) so icons/styles resolve at runtime via Gio.Resource
glib-compile-resources --sourcedir=. src/muse.gresource.xml --target=src/muse.gresource

%install
rm -rf %{buildroot}

# Upstream layout: src/* runs as main.py (mirrors upstream flake.nix)
mkdir -p %{buildroot}%{_datadir}/mixtapes
cp -r src %{buildroot}%{_datadir}/mixtapes/src
[ -d assets ] && cp -r assets %{buildroot}%{_datadir}/mixtapes/assets || true
[ -d fonts ] && cp -r fonts %{buildroot}%{_datadir}/mixtapes/fonts || true

# Desktop entry + metainfo (Exec was historically `muse`; patch to ours)
install -Dm644 com.pocoguy.Muse.desktop %{buildroot}%{_datadir}/applications/com.pocoguy.Muse.desktop
sed -i 's/^Exec=muse\( \|$\)/Exec=mixtapes\1/' %{buildroot}%{_datadir}/applications/com.pocoguy.Muse.desktop
install -Dm644 com.pocoguy.Muse.metainfo.xml %{buildroot}%{_datadir}/metainfo/com.pocoguy.Muse.metainfo.xml

# Hicolor icons for the desktop entry
if [ -d assets/icons/hicolor ]; then
  mkdir -p %{buildroot}%{_datadir}/icons
  cp -r assets/icons/hicolor %{buildroot}%{_datadir}/icons/
fi

# Launcher (yt-dlp resolves ffmpeg + node from PATH, like the nix wrapper)
install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/mixtapes
#!/bin/sh
exec /usr/bin/python3 /usr/share/mixtapes/src/main.py "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/mixtapes

%files
%{_bindir}/mixtapes
%{_datadir}/applications/com.pocoguy.Muse.desktop
%{_datadir}/metainfo/com.pocoguy.Muse.metainfo.xml
%{_datadir}/icons/hicolor/
%{_datadir}/mixtapes/

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260904205500gitc48756e-1
- Initial package: Git snapshot (metainfo 2026-09-04.0). Python deps
  mapped to Fedora + Nexus-packaged modules; GResource compiled at
  build; upstream Exec patched to mixtapes. Debuginfo disabled
  (pure Python/data payload, no ELF for find-debuginfo).
