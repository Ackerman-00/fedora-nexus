%global debug_package %{nil}
%global commit          2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261105195738

Name:           hermes-agent-desktop
Version:        0.23.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Native desktop shell for Hermes Agent (git snapshot)
License:        MIT
URL:            https://github.com/NousResearch/hermes-agent
Source0:        https://github.com/NousResearch/hermes-agent/archive/%{commit}.tar.gz
Source1:        hermes-agent-desktop-rpmlintrc

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  make
BuildRequires:  nodejs26
BuildRequires:  nodejs26-npm
BuildRequires:  python3
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

Requires:       gtk3
Requires:       nss
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       at-spi2-core
Requires:       xdg-utils
Requires:       libXtst
Requires:       libuuid
Requires:       libsecret
Requires:       alsa-lib
Requires:       cups-libs
Requires:       mesa-libgbm
Requires:       libdrm
Requires:       hicolor-icon-theme
Requires:       nodejs >= 26

%description
Hermes Agent desktop: chat sessions, background agent work, file browsing and
management, integrated terminal/browser, previews, sessions, memory and skills.
This package is built from the current upstream git snapshot.

%prep
%autosetup -n hermes-agent-%{commit}

%build
export NPM_CONFIG_IGNORE_ENGINES=true
npm ci
npm run build --workspace apps/desktop
cd apps/desktop
npm run builder -- --dir --publish never
cd ../..

%install
install -d %{buildroot}/opt/HermesDesktop %{buildroot}%{_bindir}
if [ -d apps/desktop/release/linux-unpacked ]; then
    cp -a apps/desktop/release/linux-unpacked/* %{buildroot}/opt/HermesDesktop/
else
    echo "ERROR: electron-builder did not produce release/linux-unpacked" >&2
    exit 1
fi

cat > %{buildroot}%{_bindir}/hermes-agent-desktop <<'WRAPPER_EOF'
#!/bin/sh
exec /opt/HermesDesktop/hermes "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/hermes-agent-desktop

install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/hermes-agent-desktop.desktop <<'DESKTOP_EOF'
[Desktop Entry]
Type=Application
Name=Hermes Agent Desktop
Comment=Native desktop shell for Hermes Agent
Exec=hermes-agent-desktop %U
Terminal=false
Categories=Development;
DESKTOP_EOF

%files
/opt/HermesDesktop/
%{_bindir}/hermes-agent-desktop
%{_datadir}/applications/hermes-agent-desktop.desktop

%changelog
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.23.0^20261105195738git2bd378e-1
- Initial git snapshot build of hermes-agent-desktop from upstream main
