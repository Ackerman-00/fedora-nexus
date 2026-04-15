%global debug_package %{nil}
%global __requires_exclude_from ^/opt/Heroic/.*$
%global __provides_exclude_from ^/opt/Heroic/.*$

Name:           heroic-games-launcher
Version:        2.20.1
Release:        1%{?dist}
Summary:        Open source launcher for GOG, Epic, and Amazon Games (Nexus Optimized)

License:        GPL-3.0-or-later
URL:            https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher

# Use the native upstream RPM
Source0:        %{url}/releases/download/v%{version}/Heroic-%{version}-linux-x86_64.rpm

ExclusiveArch:  x86_64

# Required to unpack the upstream RPM natively
BuildRequires:  cpio

# Explicit dependencies
Requires:       alsa-lib
Requires:       atk
Requires:       cups-libs
Requires:       gtk3
Requires:       mesa-libgbm
Requires:       nss
Requires:       libXScrnSaver
Requires:       libxcb
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXrandr
Requires:       libdrm
Requires:       hicolor-icon-theme
Requires:       desktop-file-utils

# Native gaming ecosystem integrations
Recommends:     mangohud
Recommends:     protonplus

Provides:       heroic = %{version}-%{release}

%description
Heroic is a Free and Open Source Epic, GOG, and Amazon Prime Games launcher.
Packaged exclusively for the Nexus repository. This version bypasses bloated source compilation by natively extracting the upstream RPM, injecting a custom Wayland rendering wrapper, and stripping unnecessary static binaries.

%prep
%setup -c -T
# Rip open the upstream RPM natively
rpm2cpio %{SOURCE0} | cpio -idmv

%build
# No compilation required for pre-built binaries

%install
rm -rf %{buildroot}

# 1. Install the main application folder
install -d -m 0755 %{buildroot}/opt/Heroic
cp -a opt/Heroic/* %{buildroot}/opt/Heroic/

# 2. Install standard desktop entries and icons
install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/

# 3. Create the Native Wayland Wrapper Script
install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/heroic
#!/bin/sh
# Automatically force native Wayland rendering if detected
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/Heroic/heroic "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/heroic

# 4. Optimization: Strip useless static libraries bundled by upstream
find %{buildroot}/opt/Heroic -type f -name "*.a" -delete

%files
%{_bindir}/heroic
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
/opt/Heroic/
# Enforce strict sandbox permissions natively
%attr(4755, root, root) /opt/Heroic/chrome-sandbox

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 2.20.1-1
- Initial Repackaged Wayland-Optimized Build via Upstream RPM
