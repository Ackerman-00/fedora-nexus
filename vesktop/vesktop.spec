%global debug_package %{nil}

%global __requires_exclude_from ^/opt/Vesktop/.*$
%global __provides_exclude_from ^/opt/Vesktop/.*$

Name:           vesktop
Version:        1.6.9
Release:        2%{?dist}
Summary:        Custom Discord desktop client with Vencord preinstalled (Nexus Optimized)

License:        GPL-3.0-or-later
URL:            https://github.com/Vencord/Vesktop
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.x86_64.rpm
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

BuildRequires:  cpio

Requires:           hicolor-icon-theme
Requires:       gtk3
Requires:       pango
Requires:       libnotify
Requires:       nss
Requires:       cups-libs
Requires:       libdrm
Requires:       libXScrnSaver
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXrandr
Requires:       libXtst
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       libuuid
Requires:       libsecret
Requires:       mesa-libgbm
Requires:       alsa-lib
Requires:       libappindicator-gtk3

Provides:       vencorddesktop = %{version}-%{release}
Provides:       vesktop = %{version}-%{release}
Obsoletes:      vencorddesktop < %{version}

%description
Vesktop is a custom Discord client designed to enhance your experience while keeping everything lightweight.
Packaged exclusively for the Nexus repository. This version bypasses bloated source compilation by natively extracting the upstream RPM and enforcing strict sandbox permissions.

%prep
%setup -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%build

%install

install -d -m 0755 %{buildroot}/opt/Vesktop
cp -a opt/Vesktop/* %{buildroot}/opt/Vesktop/

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/

install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/vesktop
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/Vesktop/vesktop "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/vesktop

install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/vesktop
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.*
/opt/Vesktop/
%attr(4755, root, root) /opt/Vesktop/chrome-sandbox

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 1.6.9-2
- Move the in-app updater strip into %install

* Thu Nov 05 2026 Nexus Auto-Updater <bot@github.com> - 1.6.9-1
- Update to version 1.6.9

* Thu Oct 22 2026 Nexus Auto-Updater <bot@github.com> - 1.6.8-1
- Update to version 1.6.8

* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.6.7-3
- Ship the upstream GPL-3.0 license text as Source1 (same v1.6.7 tag as the
  RPM payload, which contains none).

* Wed Sep 09 2026 Ackerman-00 <no-reply> - 1.6.7-2
- Add missing runtime Requires from ldd audit (cups-libs, libdrm, pango,
  libXcomposite, libXdamage, libXrandr)

* Fri Aug 21 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.6.7-1
- Update to 1.6.7

* Mon Aug 17 2026 Ackerman-00 <no-reply> - 1.6.6-1
- Update to 1.6.6

* Sun Aug 02 2026 Ackerman-00 <no-reply> - 1.6.5-2
- Replace util-linux-core with libuuid to match upstream RPM runtime Requires

* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.6.5-1
- Initial Repackaged Wayland-Optimized Build via Upstream RPM
