# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}

# Prevent RPM from trying to auto-generate dependencies from the bundled Electron libraries
%global __requires_exclude_from ^/opt/freebuff/.*$
%global __provides_exclude_from ^/opt/freebuff/.*$

Name:           freebuff
Version:        0.0.68
Release:        1%{?dist}
Summary:        The free coding agent for your desktop

License:        Apache-2.0
URL:            https://freebuff.com/desktop
# The freebuff.com download API 302-redirects here, so use the GitHub release
# asset directly to keep COPR source fetching stable
Source0:        https://github.com/CodebuffAI/codebuff-community/releases/download/freebuff-desktop-v%{version}/Freebuff-%{version}-linux-x86_64.AppImage

ExclusiveArch:  x86_64

# Required to locate and unpack the squashfs payload inside the Type 2 AppImage
BuildRequires:  binutils
BuildRequires:  squashfs-tools

# Core Electron runtime dependencies (Chromium 130 / Electron 33), matching the
# Vesktop/Obsidian package conventions
Requires:       zlib
Requires:       nss
Requires:       alsa-lib
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       at-spi2-core
Requires:       libnotify
Requires:       libdrm
Requires:       mesa-libgbm
Requires:       xdg-utils
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libsecret
Requires:       libappindicator-gtk3

# Freebuff is a coding agent: it drives the checker that matters for your
# project, which almost always means git
Recommends:     git

%description
Freebuff is the free, ad-supported tier of Codebuff: a coding agent that runs
in your desktop with parallel agents, each isolated in its own workspace.
No subscriptions, no API keys — powerful coding models funded by text ads.

%prep
%setup -c -T

# Extract the Type 2 AppImage (Nix method using ELF section header offset)
OFFSET=$(LC_ALL=C readelf -h %{SOURCE0} | awk 'NR==13{e_shoff=$5} NR==18{e_shentsize=$5} NR==19{e_shnum=$5} END{print e_shoff+e_shentsize*e_shnum}')
unsquashfs -q -d squashfs-root -o "$OFFSET" %{SOURCE0}
chmod go-w squashfs-root

%build
# Nothing to compile.

%install
# 1. Install the application payload as shipped by upstream
install -dm755 %{buildroot}/opt/freebuff
cp -a squashfs-root/. %{buildroot}/opt/freebuff/

# 2. Create the global wrapper script
install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/freebuff <<'EOF'
#!/bin/sh
# The AppImage's usr/lib carries the tray indicator stack (libappindicator,
# libindicator, libgconf, libnotify, libXtst, libXss) the app expects, so it
# must stay on LD_LIBRARY_PATH once the payload lands in /opt
export LD_LIBRARY_PATH="/opt/freebuff/usr/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
exec /opt/freebuff/@codebufffreebuff-desktop --ozone-platform-hint=auto "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/freebuff

# 3. Install the standard desktop entry
install -dm755 %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/freebuff.desktop <<'EOF'
[Desktop Entry]
Name=Freebuff
Comment=The free coding agent for your desktop
Exec=freebuff %U
Icon=freebuff
Terminal=false
Type=Application
StartupWMClass=Freebuff
Categories=Development;
EOF

# 4. Install the icon
install -dm755 %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -m644 squashfs-root/usr/share/icons/hicolor/512x512/apps/@codebufffreebuff-desktop.png \
    %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/freebuff.png

%files
%defattr(-,root,root,-)
%{_bindir}/freebuff
%{_datadir}/applications/freebuff.desktop
%{_datadir}/icons/hicolor/512x512/apps/freebuff.png
/opt/freebuff/
# Chromium sandbox needs the setuid helper now that the payload lives in /opt
# (the AppImage's squashfs was mounted nosuid, which made it inert upstream)
%attr(4755, root, root) /opt/freebuff/chrome-sandbox

%changelog
* Fri Aug 21 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.68-1
- Auto-updated to 0.0.68 via update.sh
