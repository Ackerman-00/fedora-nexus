%global debug_package %{nil}
%global __os_install_post %{nil}

# Bundled /opt libs must not leak into Provides.
%global __provides_exclude_from ^/opt/openchamber/.*$
%global __requires_exclude_from ^/opt/openchamber/.*$

Name:           openchamber
Version:        2.5.0
Release:        3%{?dist}
Summary:        AI coding agent workspace (Electron)

License:        MIT
URL:            https://github.com/openchamber/openchamber
Source0:        %{url}/releases/download/v2.5.0/OpenChamber-2.5.0-linux-x86_64.AppImage
# sha256: f90527c3537d28c3f09c9a7f9affc6fd2ef73731709b9f3c92e325c157ae19cf
# The AppImage carries no license text; the repo does at the same tag.
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64
# x86_64 only; aarch64 AppImage exists upstream.

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

# Strip builder-machine RUNPATH from sherpa-onnx node.
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

# Desktop entry uses the wrapper with SUID sandbox.
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

# Upstream MIT license text (the AppImage ships none)
install -Dm644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/openchamber
/opt/openchamber/
%{_datadir}/applications/openchamber.desktop
%{_datadir}/icons/hicolor/512x512/apps/openchamber.png
# Chromium SUID sandbox must stay setuid root.
%attr(4755, root, root) /opt/openchamber/chrome-sandbox

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 2.5.0-3
- Pin Source0's sha256 under Source0: the hash was written below Source1,
  so it read as a pin of the LICENSE text it does not match.

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 2.5.0-2
- Ship the upstream MIT LICENSE (Source1, same v2.5.0 tag as Source0);
  the AppImage payload carries no license text.

* Mon Oct 19 2026 Ackerman-00 <quietcraft@gmail.com> - 2.5.0-1
- Auto-update to upstream release v2.5.0
