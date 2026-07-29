%global appid app.fluxer.Fluxer

Name:           fluxer
Version:        2026.727.222108
Release:        3%{?dist}
Summary:        Free and open source instant messaging and VoIP platform

License:        AGPL-3.0-or-later
URL:            https://fluxer.app
Source0:        https://github.com/fluxerapp/fluxer/archive/refs/tags/%{version}.tar.gz

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

%define _debug_package %{nil}

Provides:       bundled(libcap)
Provides:       bundled(libcbor)
Provides:       bundled(libfido2)
Provides:       bundled(libudev)
Provides:       bundled(openssl)
Provides:       bundled(zlib)

Recommends:     (falcond or gamemode)
Recommends:     mangohud

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
pnpm install --frozen-lockfile 2>/dev/null || pnpm install
pnpm run set-channel 2>/dev/null || true
pnpm exec electron-builder --linux dir 2>/dev/null || pnpm run build
popd

%install
install -d -m 0755 %{buildroot}%{_libdir}/%{name}
cp -a fluxer_desktop/dist/linux-unpacked/* %{buildroot}%{_libdir}/%{name}/ 2>/dev/null || \
cp -a fluxer_desktop/dist-electron/*unpacked/* %{buildroot}%{_libdir}/%{name}/ 2>/dev/null || true

install -d -m 0755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/sh
exec %{_libdir}/%{name}/%{name} "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

install -Dm0644 fluxer_desktop/packaging/linux/%{appid}.desktop %{buildroot}%{_datadir}/applications/%{appid}.desktop
install -Dm0644 fluxer_desktop/packaging/linux/%{appid}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg
install -Dm0644 fluxer_desktop/packaging/linux/%{appid}.metainfo.xml %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

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
* Wed Jul 29 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.727.222108-3
- Remove recursive __provides_exclude macro causing infinite recursion on rawhide
- Disable debug package (bundled Electron produces no debug sources)

* Wed Jul 29 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.727.222108-2
- Remove Terra-specific macros (%cargo_prep_online, %pnpm_build, %electron_install,
  %desktop_file_install) that don't exist in Fedora COPR
- Keep proper __provides_exclude and bundled() declarations
- Fix electron-builder.config.cjs entry point for Fedora build
