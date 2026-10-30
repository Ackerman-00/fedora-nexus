%global debug_package %{nil}

%global __provides_exclude_from ^/opt/OpenCode/.*$
%global __requires_exclude_from ^/opt/OpenCode/.*$

Name:           opencode-desktop
Version:        2.2.3
Release:        1%{?dist}
Summary:        AI coding agent desktop app

License:        MIT
URL:            https://opencode.ai
Source0:        https://opencode.ai/files/bin/%{version}/opencode-desktop-linux-amd64.deb
# sha256: 98b6cccb1649e3c439bb1a5cf654c8310c6cf8b294a2444c540fd24cb781e99e

ExclusiveArch:  x86_64

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
ar x %{SOURCE0}
for data_archive in data.tar.zst data.tar.xz data.tar.gz; do
    if [ -f "$data_archive" ]; then
        tar xf "$data_archive"
        break
    fi
done

%install
install -dm755 %{buildroot}/opt/OpenCode
cp -a opt/OpenCode/* %{buildroot}/opt/OpenCode/
rm -f %{buildroot}/opt/OpenCode/resources/app-update.yml
find %{buildroot}/opt/OpenCode -name '*.musl.node' -delete
find %{buildroot}/opt/OpenCode -depth -type d -name '*-musl' -exec rm -rf {} + 2>/dev/null || true
if ! opt/OpenCode/resources/opencode-cli --version 2>/dev/null | grep -q '^opencode v2'; then
  echo "WARNING: bundled opencode-cli does not answer as v2 (strip damage?)" >&2
fi
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

# entry point name moved between releases; resolve it, never hardcode
launcher=""
for c in ai.opencode ai.opencode.desktop; do
    if [ -x "%{buildroot}/opt/OpenCode/$c" ]; then
        launcher=$c
        break
    fi
done
[ -n "$launcher" ] || { echo "ERROR: no Electron entry point under /opt/OpenCode" >&2; exit 1; }

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/opencode-desktop <<WRAPPER_EOF
#!/bin/sh
export OPENCODE_DISABLE_AUTOUPDATE=1
exec /opt/OpenCode/$launcher "\$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/opencode-desktop


icons=0
for sz in 32x32 64x64 128x128; do
    src=$(ls usr/share/icons/hicolor/"$sz"/apps/*.png 2>/dev/null | head -1)
    [ -n "$src" ] || continue
    install -Dm0644 "$src" %{buildroot}%{_datadir}/icons/hicolor/"$sz"/apps/opencode-desktop.png
    icons=$((icons + 1))
done
[ "$icons" -gt 0 ] || { echo "ERROR: upstream deb ships no hicolor app icon" >&2; exit 1; }

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
%attr(4755, root, root) /opt/OpenCode/chrome-sandbox

%changelog
* Fri Oct 30 2026 Ackerman-00 <quietcraft@gmail.com> - 2.2.3-1
- Auto-update to upstream release 2.2.3
