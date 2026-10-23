# Debuginfo disabled: all binaries are prebuilt upstream.
%global debug_package %{nil}
# Never put RPM directives in comments.

# Bundled /opt Chromium libs must not become Provides.
%global __provides_exclude_from ^/opt/OpenCode/.*$
%global __requires_exclude_from ^/opt/OpenCode/.*$

Name:           opencode-desktop
Version:        2.1.4
Release:        1%{?dist}
Summary:        AI coding agent desktop app

License:        MIT
URL:            https://opencode.ai
# fpm-built debs have no rpmbuild brp-strip phase, so repack from the deb.
Source0:        https://opencode.ai/files/bin/%{version}/opencode-desktop-linux-amd64.deb
# sha256: 3ba25052b860344c1dae29921287239705950798d16000651eed00d9327411d5

ExclusiveArch:  x86_64

# The install section validates the desktop entry; minimal buildroots lack it.
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd
BuildRequires:  desktop-file-utils

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

%description
OpenCode desktop app: chat sessions, background commands and subagents, file
editing, terminal, browser panel and session management driven by local or
remote models. (For the CLI, use the upstream installer instead.)

%prep
%setup -T -c
# Rip open the upstream deb natively; detect whichever data archive it holds.
ar x %{SOURCE0}
for data_archive in data.tar.zst data.tar.xz data.tar.gz; do
    if [ -f "$data_archive" ]; then
        tar xf "$data_archive"
        break
    fi
done

# upstream rpm is strip-damaged - repack from the deb
%install
install -dm755 %{buildroot}/opt/OpenCode
cp -a opt/OpenCode/* %{buildroot}/opt/OpenCode/
# Delete bundled app-update.yml; dnf owns updates.
rm -f %{buildroot}/opt/OpenCode/resources/app-update.yml
# Prune musl native modules: dead weight on glibc Fedora (same prune as AUR).
find %{buildroot}/opt/OpenCode -name '*.musl.node' -delete
find %{buildroot}/opt/OpenCode -depth -type d -name '*-musl' -exec rm -rf {} + 2>/dev/null || true
# Warn if the bundled CLI is strip-damaged again.
if ! opt/OpenCode/resources/opencode-cli --version 2>/dev/null | grep -q '^opencode v2'; then
  echo "WARNING: bundled opencode-cli does not answer as v2 (strip damage?)" >&2
fi
# Replace the Bun CLI with a resolver wrapper.
mv %{buildroot}/opt/OpenCode/resources/opencode-cli %{buildroot}/opt/OpenCode/resources/opencode-cli.bundled
cat > %{buildroot}/opt/OpenCode/resources/opencode-cli <<'CLI_EOF'
#!/bin/sh
for c in "$HOME/.opencode/bin/opencode" /usr/local/bin/opencode /usr/bin/opencode; do
    if [ -x "$c" ]; then
        case $("$c" --version 2>/dev/null) in
            "opencode v2"*) exec "$c" "$@" ;;
        esac
    fi
done
b=$(dirname "$0")/opencode-cli.bundled
[ -x "$b" ] && exec "$b" "$@"
echo "error: no working opencode v2 CLI (checked ~/.opencode/bin, /usr/local/bin, /usr/bin)" >&2
exit 127
CLI_EOF
chmod 0755 %{buildroot}/opt/OpenCode/resources/opencode-cli

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/opencode-desktop <<'WRAPPER_EOF'
#!/bin/sh
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

# Our desktop entry uses the PATH wrapper.
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

# Upstream ships AppStream metadata in the deb. Keep the upstream component id
# (an RDNS id; the file name must match it) and point the launchable at the
# desktop entry this package installs, so app centers can match the component.
install -Dm0644 usr/share/metainfo/ai.opencode.desktop.metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/ai.opencode.desktop.metainfo.xml
sed -i -e 's|<launchable type="desktop-id">ai.opencode.desktop.desktop</launchable>|<launchable type="desktop-id">opencode-desktop.desktop</launchable>|' \
    %{buildroot}%{_datadir}/metainfo/ai.opencode.desktop.metainfo.xml

%files
%license opt/OpenCode/LICENSE.electron.txt
%{_bindir}/opencode-desktop
/opt/OpenCode/
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/metainfo/ai.opencode.desktop.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/opencode-desktop.png
# Chromium SUID sandbox must stay setuid root.
%attr(4755, root, root) /opt/OpenCode/chrome-sandbox

%changelog
* Fri Oct 23 2026 Ackerman-00 <quietcraft@gmail.com> - 2.1.4-1
- Auto-update to upstream release 2.1.4
