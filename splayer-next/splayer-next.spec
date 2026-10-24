%global debug_package %{nil}
%global __requires_exclude_from ^/opt/SPlayer-Next/.*$
%global __provides_exclude_from ^/opt/SPlayer-Next/.*$

# versions read from the 1.1.0 app.asar, not the filename
%global electron_version 43.2.0
%global better_sqlite3_version 13.0.3

Name:           splayer-next
Version:        1.2.0
Release:        1%{?dist}
Summary:        Cross-platform desktop music player with rich lyric support (Nexus Optimized)

License:        AGPL-3.0-only
URL:            https://github.com/SPlayer-Dev/SPlayer-Next

# sha256: 7fe7ec69ba6353c0230d4a65dbea7d014fb40310f90745c0babfeda235224e1a
Source0:        %{url}/releases/download/v%{version}/splayer-next-%{version}-x86_64.rpm
# The rpm payload carries no license text; the repo does at the same tag.
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

# Required to unpack the upstream RPM natively
BuildRequires:  cpio
BuildRequires:  desktop-file-utils

# Runtime deps are NEEDED plus dlopen/helper deps.
Requires:       alsa-lib
Requires:       atk
Requires:       at-spi2-atk
Requires:       at-spi2-core
Requires:       cairo
Requires:       cups-libs
Requires:       dbus-libs
Requires:       expat
Requires:       glib2
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       libdrm
Requires:       libnotify
Requires:       libuuid
Requires:       libX11
Requires:       libxcb
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXext
Requires:       libXfixes
Requires:       libXrandr
Requires:       libXScrnSaver
Requires:       libxkbcommon
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       nss
Requires:       pango
Requires:       pipewire-libs
Requires:       pulseaudio-libs
Requires:       systemd-libs
Requires:       xdg-utils

Provides:       bundled(better-sqlite3) = %{better_sqlite3_version}
Provides:       bundled(electron) = %{electron_version}

%description
SPlayer-Next is a free and open source cross-platform desktop music
player with rich lyric support and wide audio format compatibility.
Packaged exclusively for the Nexus repository. This version bypasses
bloated source compilation by natively extracting the upstream RPM
(Electron + Rust napi native modules for audio capture/engine, media
keys and OpenCC lyrics conversion) and injecting a custom Wayland
rendering wrapper.

%prep
%setup -c -T
# Rip open the upstream RPM natively
rpm2cpio %{SOURCE0} | cpio -idmv

%build
# No compilation required for pre-built binaries

%install

# 1. Install the main application folder
install -d -m 0755 %{buildroot}/opt/SPlayer-Next
cp -a opt/SPlayer-Next/* %{buildroot}/opt/SPlayer-Next/

# 2. Install standard desktop entries and icons
install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
# Skip upstream .build-id symlinks; they dangle.

# 3. Create the Native Wayland Wrapper Script
install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/splayer-next
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/SPlayer-Next/SPlayer-Next "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/splayer-next

# 4. Ship the upstream AGPL-3.0 license text
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/splayer-next
%{_datadir}/applications/top.imsyy.splayer_next.desktop
%{_datadir}/icons/hicolor/512x512/apps/SPlayer-Next.png
/opt/SPlayer-Next/
# Electron aborts unless chrome-sandbox is SUID root 4755.
%attr(4755, root, root) /opt/SPlayer-Next/chrome-sandbox

%changelog
* Sat Oct 24 2026 Ackerman-00 <quietcraft@gmail.com> - 1.2.0-1
- Auto-update to upstream release v1.2.0

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.1.0-3
- Ship the upstream AGPL-3.0 LICENSE (Source1, same v1.1.0 tag as the rpm
  payload, which contains no license text).
* Fri Oct 02 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.1.0-2
- Fix startup crash: ship chrome-sandbox as %attr(4755, root, root) so the
  Electron SUID sandbox helper is configured correctly (was 0755 ->
  FATAL abort for every non-root launch; verified under xvfb before/after).
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1.0-1
- Initial package: natively repackaged upstream RPM (Electron 43.2.0,
  better-sqlite3 13.0.3, 4 Rust napi native modules). Runtime Requires
  derived from readelf NEEDED + upstream RPM Requires; Wayland wrapper
  included; /usr/lib/.build-id symlinks excluded.
