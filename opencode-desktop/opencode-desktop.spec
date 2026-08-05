%global debug_package %{nil}
%global _enable_debug_packages 0
%global __requires_exclude_from ^/opt/OpenCode/.*$
%global __provides_exclude_from ^/opt/OpenCode/.*$

Name:           opencode-desktop
Version:        1.18.14
Release:        1%{?dist}
Summary:        Open source AI coding agent

License:        MIT
URL:            https://opencode.ai
Source0:        https://github.com/anomalyco/opencode/releases/download/v%{version}/opencode-desktop-linux-amd64.deb

ExclusiveArch:  x86_64
BuildRequires:  python3

Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       libuuid
Requires:       alsa-lib
Requires:       cups-libs
Requires:       mesa-libgbm
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libxkbcommon
Requires:       libsecret
Requires:       ripgrep
Recommends:     libappindicator-gtk3

Provides:       opencode = %{version}-%{release}
Obsoletes:      opencode < %{version}

%description
OpenCode is an open source agent that helps you write and run code with any AI model.

%prep
%setup -c -T
python3 - <<'PYEOF'
import io, sys, tarfile

src = "%{SOURCE0}"
dst = "."
with open(src, "rb") as f:
    assert f.read(8) == b"!<arch>\n", "not an ar archive"
    while True:
        hdr = f.read(60)
        if len(hdr) < 60:
            break
        name = hdr[:16].decode().strip()
        size = int(hdr[48:58].decode().strip())
        payload = f.read(size)
        if size % 2:
            f.read(1)
        if name == "data.tar.xz/" or name == "data.tar.xz":
            tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz").extractall(dst)
            sys.exit(0)
    sys.exit("data.tar.xz not found in %s" % src)
PYEOF

%install
rm -rf %{buildroot}

install -d -m 0755 %{buildroot}/opt/OpenCode
cp -a opt/OpenCode/* %{buildroot}/opt/OpenCode/

rm -rf %{buildroot}/opt/OpenCode/resources/apparmor-profile
rm -f %{buildroot}/opt/OpenCode/resources/app-update.yml
rm -f %{buildroot}/opt/OpenCode/resources/app.asar.unpacked/node_modules/@msgpackr-extract/msgpackr-extract-linux-x64/*.musl.node
rm -rf %{buildroot}/opt/OpenCode/resources/app.asar.unpacked/node_modules/@parcel/watcher-linux-x64-musl

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
cp -a usr/share/metainfo %{buildroot}%{_datadir}/

install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/opencode-desktop
#!/bin/sh
flags="--ozone-platform-hint=auto --enable-features=WaylandWindowDecorations --enable-wayland-ime=true --wayland-text-input-version=3"
conf="${XDG_CONFIG_HOME:-$HOME/.config}/opencode-desktop-flags.conf"
if [ -r "$conf" ]; then
    while IFS= read -r line; do
        case "$line" in
            ''|\#*) continue ;;
        esac
        flags="$flags $line"
    done < "$conf"
fi
exec /opt/OpenCode/ai.opencode.desktop $flags "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/opencode-desktop

sed -i 's|^Exec=.*|Exec=%{_bindir}/opencode-desktop %U|' \
    %{buildroot}%{_datadir}/applications/opencode-desktop.desktop
sed -i 's|^Exec=.*|Exec=%{_bindir}/opencode-desktop %U|' \
    %{buildroot}%{_datadir}/applications/ai.opencode.desktop.desktop

%files
%{_bindir}/opencode-desktop
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/applications/ai.opencode.desktop.desktop
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/metainfo/*
/opt/OpenCode/
%attr(4755, root, root) /opt/OpenCode/chrome-sandbox

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 1.18.14-1
- Auto-update to version 1.18.14
