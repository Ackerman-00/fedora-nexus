%global debug_package %{nil}
%global __os_install_post %{nil}

%global __provides_exclude_from ^/opt/openchamber/.*$
%global __requires_exclude_from ^/opt/openchamber/.*$

Name:           openchamber
Version:        2.5.3
Release:        1%{?dist}
Summary:        AI coding agent workspace (Electron)

License:        MIT
URL:            https://github.com/openchamber/openchamber
Source0:        %{url}/releases/download/v2.5.3/OpenChamber-2.5.3-linux-x86_64.AppImage
# sha256: c034a8adf52af5bc50f99dce994d70159741074d0c4266f456b70f59bc81de32
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  squashfs-tools
BuildRequires:  coreutils
BuildRequires:  patchelf

Requires:       gtk3
Requires:       nss
Requires:       nspr
Requires:       alsa-lib
Requires:       libnotify
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       hicolor-icon-theme
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libX11
Requires:       libxkbcommon
Requires:       mesa-libgbm
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       fontconfig
Requires:       freetype
Requires:       cups-libs
Requires:       dbus-libs
Requires:       libsecret
Requires:       systemd-libs

Provides:       openchamber = %{version}-%{release}

%description
OpenChamber is an AI coding agent workspace: chat sessions, background
commands and subagents, file editing, terminal, browser panel, session
management and scheduled tasks, driven by local or remote models.

%prep
%setup -c -T

OFFSET=$(LC_ALL=C readelf -h %{SOURCE0} | awk 'NR==13{e_shoff=$5} NR==18{e_shentsize=$5} NR==19{e_shnum=$5} END{print e_shoff+e_shentsize*e_shnum}')
unsquashfs -q -d squashfs-root -o "$OFFSET" %{SOURCE0}
chmod go-w squashfs-root

%build

%install
install -dm755 %{buildroot}/opt/openchamber
cp -ar squashfs-root/* %{buildroot}/opt/openchamber/

find %{buildroot}/opt/openchamber/resources -name '*.node' -print0 | \
    xargs -0 -r patchelf --remove-rpath 2>/dev/null || true

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/openchamber <<'WRAPPER_EOF'
#!/bin/sh
export APPDIR="/opt/openchamber"
exec /opt/openchamber/AppRun "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/openchamber

install -Dm644 squashfs-root/usr/share/icons/hicolor/512x512/apps/openchamber.png \
    %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/openchamber.png

install -dm755 %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/openchamber.desktop <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=OpenChamber
Comment=AI coding agent workspace
Exec=openchamber %U
Icon=openchamber
Terminal=false
StartupWMClass=openchamber
Categories=Development;IDE;
DESKTOP_EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/openchamber.desktop || true

install -Dm644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/openchamber
/opt/openchamber/
%{_datadir}/applications/openchamber.desktop
%{_datadir}/icons/hicolor/512x512/apps/openchamber.png
%attr(4755, root, root) /opt/openchamber/chrome-sandbox

%changelog
* Wed Oct 28 2026 Ackerman-00 <quietcraft@gmail.com> - 2.5.3-1
- Auto-update to upstream release v2.5.3
