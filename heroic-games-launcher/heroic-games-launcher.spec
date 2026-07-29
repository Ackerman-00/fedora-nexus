%global debug_package %{nil}
%global __requires_exclude_from ^/opt/Heroic/.*$
%global __provides_exclude_from ^/opt/Heroic/.*$

%global legendary_version 0.20.43
%global gogdl_version 1.2.1
%global nile_version 1.1.2
%global comet_version 0.2.0

Name:           heroic-games-launcher
Version:        2.22.0
Release:        1%{?dist}
Summary:        Open source launcher for GOG, Epic, and Amazon Games (Nexus Optimized)

License:        GPL-3.0-only AND MIT AND BSD-3-Clause
URL:            https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher

# Use the native upstream RPM
Source0:        %{url}/releases/download/v%{version}/Heroic-%{version}-linux-x86_64.rpm

ExclusiveArch:  x86_64

# Required to unpack the upstream RPM natively
BuildRequires:  cpio
BuildRequires:  desktop-file-utils

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
Requires:       libappindicator-gtk3
Requires:       python3
Requires:       which

# Native gaming ecosystem integrations
Recommends:     (falcond or gamemode)
Recommends:     mangohud
Recommends:     umu-launcher

Provides:       heroic = %{version}-%{release}
Provides:       bundled(comet) = %{comet_version}
Provides:       bundled(gogdl) = %{gogdl_version}
Provides:       bundled(legendary) = %{legendary_version}
Provides:       bundled(nile) = %{nile_version}

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

# 2. Install standard desktop entries, icons, and metainfo
install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
if [ -d usr/share/metainfo ]; then
    install -d -m 0755 %{buildroot}%{_metainfodir}
    cp -a usr/share/metainfo/*.xml %{buildroot}%{_metainfodir}/
fi

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
%{_datadir}/icons/hicolor/*/apps/*.*
%{_metainfodir}/com.heroicgameslauncher.hgl.metainfo.xml
/opt/Heroic/

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 2.22.0-1
- Initial Repackaged Wayland-Optimized Build via Upstream RPM
