%global debug_package %{nil}
%global _enable_debug_packages 0
%global __requires_exclude_from ^/opt/OpenCode/.*$
%global __provides_exclude_from ^/opt/OpenCode/.*$

Name:           opencode-desktop
Version:        1.18.9
Release:        1%{?dist}
Summary:        Open source AI coding agent

License:        MIT
URL:            https://opencode.ai
Source0:        https://github.com/anomalyco/opencode/releases/download/v%{version}/opencode-desktop-linux-x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio

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

Provides:       opencode = %{version}-%{release}
Obsoletes:      opencode < %{version}

%description
OpenCode is an open source agent that helps you write and run code with any AI model.

%prep
%setup -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%install
rm -rf %{buildroot}

install -d -m 0755 %{buildroot}/opt/OpenCode
cp -a opt/OpenCode/* %{buildroot}/opt/OpenCode/

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
cp -a usr/share/metainfo %{buildroot}%{_datadir}/

install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/opencode-desktop
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    exec /opt/OpenCode/ai.opencode.desktop --ozone-platform-hint=wayland "$@"
fi
exec /opt/OpenCode/ai.opencode.desktop "$@"
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
* Thu Jul 30 2026 Ackerman-00 <quietcraft@gmail.com> - 1.18.9-1
- Initial repackaged Wayland-optimized build from upstream RPM
