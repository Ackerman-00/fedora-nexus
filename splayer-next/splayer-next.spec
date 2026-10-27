%global debug_package %{nil}
%global __requires_exclude_from ^/opt/SPlayer-Next/.*$
%global __provides_exclude_from ^/opt/SPlayer-Next/.*$

%global electron_version 44.9.0
%global better_sqlite3_version 13.0.3

Name:           splayer-next
Version:        1.2.0
Release:        2%{?dist}
Summary:        Cross-platform desktop music player with rich lyric support (Nexus Optimized)

License:        AGPL-3.0-only
URL:            https://github.com/SPlayer-Dev/SPlayer-Next

Source0:        %{url}/releases/download/v%{version}/splayer-next-%{version}-x86_64.rpm
# sha256: 30acae5ddc98e2b5f3254af6004613194ac9daa43f8d05eb6a1831481c7e9441
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

BuildRequires:  cpio
BuildRequires:  desktop-file-utils

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
rpm2cpio %{SOURCE0} | cpio -idmv

%build

%install

install -d -m 0755 %{buildroot}/opt/SPlayer-Next
cp -a opt/SPlayer-Next/* %{buildroot}/opt/SPlayer-Next/

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/

install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/splayer-next
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/SPlayer-Next/SPlayer-Next "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/splayer-next

install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/splayer-next
%{_datadir}/applications/top.imsyy.splayer_next.desktop
%{_datadir}/icons/hicolor/512x512/apps/SPlayer-Next.png
/opt/SPlayer-Next/
%attr(4755, root, root) /opt/SPlayer-Next/chrome-sandbox

%changelog
* Sat Oct 24 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.2.0-2
- Refresh the sha256 pin and both bundled() versions from the 1.2.0 payload:
  the auto-update left the pin and bundled(electron) at their 1.1.0 values
  (Electron 43.2.0 -> 44.9.0; better-sqlite3 13.0.3 unchanged).

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
