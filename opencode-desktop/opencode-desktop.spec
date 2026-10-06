# Debuginfo disabled: every binary here is prebuilt upstream, so there are
# no build sources to extract debug symbols from (Fedora requires stating why).
%global debug_package %{nil}

# Electron app repacked from upstream's own .rpm. Everything travels under
# /opt/OpenCode, so bundled Chromium libraries must not leak into system
# Provides/Requires; genuine system deps are declared explicitly below.
%global __provides_exclude_from ^/opt/OpenCode/.*$
%global __requires_exclude_from ^/opt/OpenCode/.*$

Name:           opencode-desktop
Version:        2.0.24
Release:        2%{?dist}
Summary:        AI coding agent desktop app

License:        MIT
URL:            https://opencode.ai
Source0:        https://opencode.ai/files/bin/%{version}/opencode-desktop-linux-x86_64.rpm
# sha256: 0c64733ea978132155bf89eb9c2bd9f386d83ee275e44ead56f3fb22e24db897

ExclusiveArch:  x86_64

# Runtime deps: upstream rpm's own Requires (verified from the 2.0.22 header:
# gtk3, nss, libXScrnSaver, libnotify, at-spi2-core, xdg-utils), with the
# Debian-style rich deps mapped to Fedora names (libXtst, libuuid).
Requires:       gtk3
Requires:       nss
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       at-spi2-core
Requires:       xdg-utils
Requires:       libXtst
Requires:       libuuid
Requires:       hicolor-icon-theme

%description
OpenCode desktop app: chat sessions, background commands and subagents, file
editing, terminal, browser panel and session management driven by local or
remote models. (For the CLI, use the upstream installer instead.)

%prep
%setup -T -c
rpm2cpio %{SOURCE0} | cpio -idmv

%install
install -dm755 %{buildroot}/opt/OpenCode
cp -a opt/OpenCode/* %{buildroot}/opt/OpenCode/
# No bundled self-updater on a distro package: electron-updater reads
# resources/app-update.yml, and Electron's own docs say Linux updates belong
# to the package manager. Deleting it is the documented kill-switch
# (electron-builder#8838). dnf/COPR owns updates from here.
rm -f %{buildroot}/opt/OpenCode/resources/app-update.yml

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/opencode-desktop <<'WRAPPER_EOF'
#!/bin/sh
# The sidecar CLI self-updates out from under the desktop version
# (packages/cli updater.ts, default policy "notify", "auto" installs).
# A distro package owns its versions, so updates stay off here.
export OPENCODE_DISABLE_AUTOUPDATE=1
exec /opt/OpenCode/ai.opencode.desktop "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/opencode-desktop


install -Dm0644 usr/share/icons/hicolor/32x32/apps/ai.opencode.desktop.png \
    %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/opencode-desktop.png
install -Dm0644 usr/share/icons/hicolor/64x64/apps/ai.opencode.desktop.png \
    %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/opencode-desktop.png
install -Dm0644 usr/share/icons/hicolor/128x128/apps/ai.opencode.desktop.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/opencode-desktop.png

# Upstream desktop entries point straight at /opt and carry NoDisplay on the
# clean one; ours goes through the PATH wrapper with the SUID sandbox intact.
install -dm755 %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/opencode-desktop.desktop <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=OpenCode
Comment=Open source AI coding agent
Exec=opencode-desktop %U
Icon=opencode-desktop
Terminal=false
StartupWMClass=ai.opencode.desktop
MimeType=x-scheme-handler/opencode;
Categories=Development;IDE;
DESKTOP_EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/opencode-desktop.desktop || true

%files
%license opt/OpenCode/LICENSE.electron.txt
%{_bindir}/opencode-desktop
/opt/OpenCode/
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/opencode-desktop.png
# Chromium SUID sandbox MUST stay setuid root (AGENTS.md Electron rule, Oct 2026:
# 0755 fatally aborts launch for every non-root user, proven rc=133 under xvfb).
%attr(4755, root, root) /opt/OpenCode/chrome-sandbox

%changelog
* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-2
- Drop bundled electron-updater config; dnf owns updates on Fedora

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.24-1
- Auto-update to upstream release 2.0.24
