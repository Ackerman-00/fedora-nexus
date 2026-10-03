%global debug_package %{nil}
%global __os_install_post %{nil}

# Electron app extracted from the upstream AppImage. Everything the app needs
# travels under /opt/openchamber, so bundled libraries must not leak into
# system Provides/Requires; genuine system deps are declared explicitly below.
%global __provides_exclude_from ^/opt/openchamber/.*$
%global __requires_exclude_from ^/opt/openchamber/.*$

Name:           openchamber
Version:        2.1.0
Release:        2%{?dist}
Summary:        AI coding agent workspace (Electron)

License:        MIT
URL:            https://github.com/openchamber/openchamber
Source0:        %{url}/releases/download/v%{version}/OpenChamber-%{version}-linux-x86_64.AppImage
# sha256: ab4f20fc7c17ccbcbe720cfcbbbabd0b592c19d8e7ebe0663d7cb3f918a082f2

ExclusiveArch:  x86_64
# aarch64 AppImage exists upstream (OpenChamber-2.1.0-linux-arm64.AppImage) but
# this repo only enables x86_64 COPR chroots; extend if that changes.

BuildRequires:  binutils
BuildRequires:  squashfs-tools
BuildRequires:  coreutils
BuildRequires:  patchelf

# Electron runtime deps (mirrors rootapp.spec, same Chromium base)
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

# Extract the Type 2 AppImage (ELF section header offset method)
OFFSET=$(LC_ALL=C readelf -h %{SOURCE0} | awk 'NR==13{e_shoff=$5} NR==18{e_shentsize=$5} NR==19{e_shnum=$5} END{print e_shoff+e_shentsize*e_shnum}')
unsquashfs -q -d squashfs-root -o "$OFFSET" %{SOURCE0}
chmod go-w squashfs-root

%build
# Nothing to compile.

%install
install -dm755 %{buildroot}/opt/openchamber
cp -ar squashfs-root/* %{buildroot}/opt/openchamber/

# Bundled sherpa-onnx node carries a builder-machine RUNPATH that trips
# brp check-rpaths; $ORIGIN resolution is preserved without it.
find %{buildroot}/opt/openchamber/resources -name '*.node' -print0 | \
    xargs -0 -r patchelf --remove-rpath 2>/dev/null || true

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/openchamber <<'WRAPPER_EOF'
#!/bin/sh
export APPDIR="/opt/openchamber"
exec /opt/openchamber/AppRun "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/openchamber

# Upstream ships the icon at usr/share/icons/hicolor/scalable/openchamber.svg
# (NO apps/ subdir - verified by tearing the AppImage apart; the old
# .../scalable/apps/... path failed %install with "cannot stat").
# Installed to the standard apps/ location.
install -Dm644 squashfs-root/usr/share/icons/hicolor/scalable/openchamber.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/openchamber.svg

# Upstream desktop entry runs AppRun --no-sandbox; ours goes through the
# wrapper with the SUID sandbox intact (see %files %attr below).
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

%files
%{_bindir}/openchamber
/opt/openchamber/
%{_datadir}/applications/openchamber.desktop
%{_datadir}/icons/hicolor/scalable/apps/openchamber.svg
# Chromium SUID sandbox MUST stay setuid root (AGENTS.md Electron rule, Oct 2026:
# 0755 fatally aborts launch for every non-root user, proven rc=133 under xvfb).
%attr(4755, root, root) /opt/openchamber/chrome-sandbox

%changelog
* Sat Oct 03 2026 Ackerman-00 <quietcraft@gmail.com> - 2.1.0-2
- Fix icon source path: upstream AppImage ships it at
  usr/share/icons/hicolor/scalable/openchamber.svg (no apps/ subdir);
  old path failed %install. Verified: sha256 pin matches, X-AppImage-Version 2.1.0
* Sat Oct 03 2026 Ackerman-00 <quietcraft@gmail.com> - 2.1.0-1
- Initial packaging: extract upstream AppImage (Electron 43), SUID sandbox kept
