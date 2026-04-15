%global debug_package %{nil}

%global __requires_exclude_from ^/opt/Vesktop/.*$
%global __provides_exclude_from ^/opt/Vesktop/.*$

Name:           vesktop
Version:        1.6.5
Release:        1%{?dist}
Summary:        Custom Discord desktop client with Vencord preinstalled (Nexus Optimized)

License:        GPL-3.0-or-later
URL:            https://github.com/Vencord/Vesktop
# Use the native upstream RPM
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.x86_64.rpm

ExclusiveArch:  x86_64

# Required to unpack the upstream RPM natively
BuildRequires:  cpio

# Explicit dependencies
Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       util-linux-core
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
rm -rf %{buildroot}

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
# Automatically force native Wayland rendering if detected
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/Vesktop/vesktop "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/vesktop

%files
%{_bindir}/vesktop
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
/opt/Vesktop/
# Enforce strict sandbox permissions natively
%attr(4755, root, root) /opt/Vesktop/chrome-sandbox

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.6.5-1
- Initial Repackaged Wayland-Optimized Build via Upstream RPM
