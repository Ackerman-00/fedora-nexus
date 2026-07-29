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
BuildRequires:  nodejs
BuildRequires:  nodejs-npm
BuildRequires:  nodejs-packaging
BuildRequires:  pnpm
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(libfido2)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(libudev)
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
Provides:       bundled(libudev)
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
if ! grep entry electron-builder.config.cjs; then
    sed '/desktop:/,/}/{/desktop:/a entry:{
    /\}/a },
    }' -i electron-builder.config.cjs
fi
ln -sf electron-builder.config.cjs electron-builder.js
%pnpm_build -F -r set-channel,build
popd

%install
pushd fluxer_desktop
mv dist-electron/*unpacked dist/
%electron_install -b fluxer_desktop -i %{appid} -s fluxer -I packaging/linux/%{appid}.svg

%desktop_file_install -k Exec,Icon -v fluxer,%{appid} -u %U packaging/linux/%{appid}.desktop
install -Dm644 packaging/linux/%{appid}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg

install -Dm644 packaging/linux/%{appid}.metainfo.xml %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml
popd

%files
%doc README.md
%license LICENSE
%{_bindir}/fluxer
%{_libdir}/%{name}/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Sat Jul 29 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.727.222108-1
- Initial package
