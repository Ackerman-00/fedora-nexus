%global debug_package %{nil}
# bundled sonames stay private
%global __requires_exclude_from ^/opt/HermesDesktop/.*$
%global __provides_exclude_from ^/opt/HermesDesktop/.*$
%global __brp_mangle_shebangs_exclude_from ^/opt/HermesDesktop/.*$
%global commit          30d501875697d2789e0711ba719221c4afa0530a
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261111224709

Name:           hermes-agent-desktop
Version:        0.23.1^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Native desktop shell for Hermes Agent (git snapshot)
License:        MIT
URL:            https://github.com/NousResearch/hermes-agent
Source0:        https://github.com/NousResearch/hermes-agent/archive/%{commit}.tar.gz
# sha256:  e0f82144205e81ed344faa1d67f515113fd441ac8cde691762911f02cbdead68
Source1:        https://nodejs.org/download/release/v26.12.1/node-v26.12.1-linux-x64.tar.xz
# sha256: 6170b2d474e1c626f43cff3adc118df9fe3b573258a4fc3d850c8dbc6b079bbd
Source2:        https://registry.npmjs.org/@pnpm/exe.linux-x64/-/exe.linux-x64-12.15.0.tgz
# sha256: 402f7045b1e0587acb1542f18d38afbccb6babf3c7451394e6fb3d9f0160c6ca
Source3:        hermes-agent-desktop-rpmlintrc

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  libX11-devel
BuildRequires:  libXi-devel
BuildRequires:  libatomic
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

Requires:       gtk3
Requires:       nss
Requires:       libX11.so.6()(64bit)
Requires:       libXi.so.6()(64bit)
Requires:       libXss.so.1()(64bit)
Requires:       libnotify.so.4()(64bit)
Requires:       at-spi2-core
Requires:       xdg-utils
Requires:       libXtst.so.6()(64bit)
Requires:       libuuid.so.1()(64bit)
Requires:       libsecret-1.so.0()(64bit)
Requires:       libasound.so.2()(64bit)
Requires:       libcups.so.2()(64bit)
Requires:       mesa-libgbm
Requires:       libdrm.so.2()(64bit)
Requires:       hicolor-icon-theme
# Optional system playback fallback, used by some Electron paths; RPM Fusion
# or Fedora's ffmpeg may provide it.
Recommends:     ffmpeg
Recommends:     ffmpeg-libs
Requires(post): gtk-update-icon-cache
Requires(postun): gtk-update-icon-cache

%description
Hermes Agent desktop: chat sessions, background agent work, file browsing and
management, integrated terminal/browser, previews, sessions, memory and skills.
This package is built from the current upstream git snapshot.

%prep
%autosetup -n hermes-agent-%{commit}
mkdir -p .tools/node .tools/pnpm
tar -xJf %{SOURCE1} -C .tools/node --strip-components=1
tar -xzf %{SOURCE2} -C .tools/pnpm
export PATH="$PWD/.tools/node/bin:$PWD/.tools/pnpm/package:$PATH"
node --version
pnpm --version

%build
export PATH="$PWD/.tools/node/bin:$PWD/.tools/pnpm/package:$PATH"
pnpm install --frozen-lockfile
pnpm --filter hermes run build
node scripts/build/electron-runtime.mjs --source .
cd apps/desktop
node scripts/run-electron-builder.mjs --linux --x64 --dir --publish never
cd ../..

%install
install -d %{buildroot}/opt/HermesDesktop %{buildroot}%{_bindir}
install -Dpm0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE
if [ -d apps/desktop/release/linux-unpacked ]; then
    cp -a apps/desktop/release/linux-unpacked/* %{buildroot}/opt/HermesDesktop/
else
    echo "ERROR: electron-builder did not produce release/linux-unpacked" >&2
    exit 1
fi
install -Dpm0644 %{buildroot}/opt/HermesDesktop/resources/app.asar.unpacked/dist/hermes.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/hermes-agent-desktop.png

cat > %{buildroot}%{_bindir}/hermes-agent-desktop <<'WRAPPER_EOF'
#!/bin/sh
exec /opt/HermesDesktop/Hermes "$@"
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
Icon=hermes-agent-desktop
DESKTOP_EOF

%post
/bin/touch --no-create %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
/usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor >/dev/null 2>&1 || :

%postun
case "$1" in
    0)
        /bin/touch --no-create %{_datadir}/icons/hicolor >/dev/null 2>&1
        /usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
        ;;
esac

%posttrans
/usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor >/dev/null 2>&1 || :

%files
/opt/HermesDesktop/
%attr(4755, root, root) /opt/HermesDesktop/chrome-sandbox
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/hermes-agent-desktop
%{_datadir}/applications/hermes-agent-desktop.desktop
%{_datadir}/icons/hicolor/512x512/apps/hermes-agent-desktop.png

%changelog
* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.23.1^20261111224709git30d5018-1
- Nightly sync with upstream main branch (Commit: 30d5018)
