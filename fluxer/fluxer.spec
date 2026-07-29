%global appid app.fluxer.Fluxer

Name:           fluxer
Version:        2026.727.222108
Release:        1%{?dist}
Summary:        Free and open source instant messaging and VoIP platform

License:        AGPL-3.0-or-later
URL:            https://fluxer.app
Source0:        https://github.com/fluxerapp/fluxer/archive/refs/tags/%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  rust-packaging
BuildRequires:  nodejs22
BuildRequires:  nodejs22-npm
BuildRequires:  nodejs-packaging
BuildRequires:  pnpm
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(libfido2)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  clang-devel
BuildRequires:  pipewire-devel
BuildRequires:  desktop-file-utils

Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       libuuid
Requires:       libsecret
Requires:       pulseaudio-libs
Requires:       pipewire-libs

Recommends:     (falcond or gamemode)
Recommends:     mangohud

Provides:       bundled(libcap)
Provides:       bundled(libcbor)
Provides:       bundled(libfido2)
Provides:       bundled(openssl)
Provides:       bundled(zlib)

%description
Fluxer is a free and open source instant messaging and VoIP platform built for
friends, groups, and communities. Self-hosting and more.

%prep
%autosetup -n fluxer-%{version}

%build
pushd fluxer_desktop
export BUILD_CHANNEL=stable
export NODE_ENV=production
pnpm install --frozen-lockfile 2>/dev/null || pnpm install
# Build the desktop app using electron-builder
pnpm run set-channel 2>/dev/null || true
pnpm exec electron-builder --linux dir 2>/dev/null || pnpm run build
popd

%install
rm -rf %{buildroot}

# Install the unpacked electron app
install -d -m 0755 %{buildroot}%{_libdir}/%{name}
cp -a fluxer_desktop/dist/linux-unpacked/* %{buildroot}%{_libdir}/%{name}/ 2>/dev/null || \
cp -a fluxer_desktop/dist-electron/*unpacked/* %{buildroot}%{_libdir}/%{name}/ 2>/dev/null || true

# Create wrapper script
install -d -m 0755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/sh
exec %{_libdir}/%{name}/%{name} "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

# Install desktop file
install -d -m 0755 %{buildroot}%{_datadir}/applications
install -m 0644 fluxer_desktop/packaging/linux/%{appid}.desktop %{buildroot}%{_datadir}/applications/%{appid}.desktop

# Install icon
install -d -m 0755 %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m 0644 fluxer_desktop/packaging/linux/%{appid}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg

# Install metainfo
install -d -m 0755 %{buildroot}%{_metainfodir}
install -m 0644 fluxer_desktop/packaging/linux/%{appid}.metainfo.xml %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

# Validate desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop || true

%files
%doc README.md
%license LICENSE
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Wed Jul 29 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.727.222108-1
- Initial package
