%global debug_package %{nil}
%global __requires_exclude_from ^/opt/SPlayer-Next/.*$
%global __provides_exclude_from ^/opt/SPlayer-Next/.*$

# Read out of the 1.1.0 artifact (/tmp teardown 2026-09-06):
# - better-sqlite3 version from
#   resources/app.asar.unpacked/node_modules/better-sqlite3/package.json
# - electron version from package.json devDependencies (~43.2.0),
#   confirmed by the bundled Chromium 150.0.7871.129 runtime probe
%global electron_version 43.2.0
%global better_sqlite3_version 13.0.3

Name:           splayer-next
Version:        1.1.0
Release:        1%{?dist}
Summary:        Cross-platform desktop music player with rich lyric support (Nexus Optimized)

License:        AGPL-3.0-only
URL:            https://github.com/SPlayer-Dev/SPlayer-Next

# sha256: 7fe7ec69ba6353c0230d4a65dbea7d014fb40310f90745c0babfeda235224e1a
# Use the native upstream RPM (upstream also publishes an aarch64 RPM;
# this repo only ships x86_64 chroots, same as heroic/vesktop/fluxer)
Source0:        %{url}/releases/download/v%{version}/splayer-next-%{version}-x86_64.rpm

ExclusiveArch:  x86_64

# Required to unpack the upstream RPM natively
BuildRequires:  cpio
BuildRequires:  desktop-file-utils

# Explicit runtime dependencies: the union of the ELF NEEDED set
# (readelf -d on the main binary, chrome_crashpad_handler, the bundled
# .so files and all 5 native .node modules incl. the better-sqlite3
# prebuild) and the upstream RPM's own Requires (libXtst, libuuid,
# libXScrnSaver, libnotify, xdg-utils are dlopen/helper deps that do
# not show up as NEEDED but are required at runtime)
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
rm -rf %{buildroot}

# 1. Install the main application folder
install -d -m 0755 %{buildroot}/opt/SPlayer-Next
cp -a opt/SPlayer-Next/* %{buildroot}/opt/SPlayer-Next/

# 2. Install standard desktop entries and icons
install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
# NOTE: the upstream RPM also ships /usr/lib/.build-id symlinks
# (openSUSE-style debuginfo links into /opt); they are deliberately
# NOT installed - they dangle and would collide with our debuginfo.

# 3. Create the Native Wayland Wrapper Script
install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/splayer-next
#!/bin/sh
# Automatically force native Wayland rendering if detected
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/SPlayer-Next/SPlayer-Next "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/splayer-next

%files
%{_bindir}/splayer-next
%{_datadir}/applications/top.imsyy.splayer_next.desktop
%{_datadir}/icons/hicolor/512x512/apps/SPlayer-Next.png
/opt/SPlayer-Next/

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1.0-1
- Initial package: natively repackaged upstream RPM (Electron 43.2.0,
  better-sqlite3 13.0.3, 4 Rust napi native modules). Runtime Requires
  derived from readelf NEEDED + upstream RPM Requires; Wayland wrapper
  included; /usr/lib/.build-id symlinks excluded.
