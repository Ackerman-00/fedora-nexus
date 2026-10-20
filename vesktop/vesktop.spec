# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}

# Prevent RPM from trying to auto-generate dependencies from the bundled Electron libraries
%global __requires_exclude_from ^/opt/Vesktop/.*$
%global __provides_exclude_from ^/opt/Vesktop/.*$

Name:           vesktop
Version:        1.6.7
Release:        3%{?dist}
Summary:        Custom Discord desktop client with Vencord preinstalled (Nexus Optimized)

License:        GPL-3.0-or-later
URL:            https://github.com/Vencord/Vesktop
# Use the native upstream RPM as our raw source payload
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.x86_64.rpm
# Upstream payload lacks license text; fetch from tag.
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

# Required to unpack the upstream RPM natively
BuildRequires:  cpio

# Deps mapped from Void template plus ldd NEEDED.
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
# Rip open the upstream RPM natively
rpm2cpio %{SOURCE0} | cpio -idmv

%build
# No compilation required for pre-built binaries

%install

# 1. Install the main application folder
install -d -m 0755 %{buildroot}/opt/Vesktop
cp -a opt/Vesktop/* %{buildroot}/opt/Vesktop/

# 2. Install standard desktop entries and icons
install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/

# 3. Create the Native Wayland Wrapper Script
install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/vesktop
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/Vesktop/vesktop "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/vesktop

# 4. Ship the upstream GPL-3.0 license text
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/vesktop
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.*
/opt/Vesktop/
# Enforce strict sandbox permissions natively
%attr(4755, root, root) /opt/Vesktop/chrome-sandbox

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.6.7-3
- Ship the upstream GPL-3.0 license text as Source1 (same v1.6.7 tag as the
  RPM payload, which contains none).

* Wed Sep 09 2026 Ackerman-00 <quietcraft@gmail.com> - 1.6.7-2
- Add missing runtime Requires from ldd audit (cups-libs, libdrm, pango,
  libXcomposite, libXdamage, libXrandr)

* Fri Aug 21 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.6.7-1
- Update to 1.6.7

* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 1.6.6-1
- Update to 1.6.6

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 1.6.5-2
- Replace util-linux-core with libuuid to match upstream RPM runtime Requires

* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.6.5-1
- Initial Repackaged Wayland-Optimized Build via Upstream RPM
