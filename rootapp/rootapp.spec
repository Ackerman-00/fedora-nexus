%global debug_package %{nil}
%global __os_install_post %{nil}
%global __requires_exclude_from ^/opt/rootapp/.*$
%global __provides_exclude_from ^/opt/rootapp/.*$

Name:           rootapp
Version:        0.9.119
Release:        2%{?dist}
Summary:        Root App is a new Discord alternative, designed for gaming communities and large online groups

License:        Proprietary
URL:            https://www.rootapp.com
ExclusiveArch:  x86_64

Source0:        https://installer.rootapp.com/installer/Linux/X64/Root.AppImage
# sha256: d50d01eda97876ccb965470c982947b56ac649fa497825449efe4952b06d2526

BuildRequires:  binutils
BuildRequires:  squashfs-tools
BuildRequires:  coreutils

# Core GUI toolkit
Requires:       gtk3
Requires:       nss
Requires:       alsa-lib
Requires:       libnotify
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       hicolor-icon-theme
Requires:       zlib

# X11 libraries (Chromium/DotNetBrowser needs these)
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libX11
Requires:       libXi
Requires:       libXt
Requires:       libXinerama
Requires:       libXrandr
Requires:       libXcursor
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXrender

# Wayland support
Requires:       libxkbcommon
Requires:       mesa-libgbm
Requires:       libwayland-client
Requires:       libwayland-cursor
Requires:       libwayland-egl
Requires:       libdrm

# OpenGL/rendering (Chromium GPU acceleration)
Requires:       libglvnd
Requires:       mesa-libGL

# Font/text rendering
Requires:       fontconfig
Requires:       freetype2
Requires:       cairo
Requires:       pango
Requires:       harfbuzz
Requires:       icu

# Image handling
Requires:       gdk-pixbuf2

# Audio/printing
Requires:       cups-libs
Requires:       pulseaudio-libs

# Security/crypto
Requires:       openssl-libs
Requires:       vulkan-loader
Requires:       nspr

# D-Bus
Requires:       dbus-libs

# Secret storage
Requires:       libsecret

# Clipboard
Requires:       wl-clipboard

# Accessibility
Requires:       at-spi2-atk

Provides:       rootapp = %{version}-%{release}
Provides:       root-app = %{version}-%{release}
Conflicts:      root-app

%description
Root App is a new Discord alternative, designed for gaming communities and
large online groups.

%prep
%setup -c -T

# Extract the Type 2 AppImage (Nix method using ELF section header offset)
OFFSET=$(LC_ALL=C readelf -h %{SOURCE0} | awk 'NR==13{e_shoff=$5} NR==18{e_shentsize=$5} NR==19{e_shnum=$5} END{print e_shoff+e_shentsize*e_shnum}')
unsquashfs -q -d squashfs-root -o "$OFFSET" %{SOURCE0}
chmod go-w squashfs-root

%build
# Nothing to compile.

%install
install -dm755 %{buildroot}/opt/rootapp
cp -ar squashfs-root/* %{buildroot}/opt/rootapp/

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/rootapp <<'WRAPPER_EOF'
#!/bin/sh
export APPDIR="/opt/rootapp"

# Detect Wayland and enable native Ozone backend for DotNetBrowser/Chromium
# Without this, Chromium falls back to XWayland which causes rendering issues
if [ -n "$WAYLAND_DISPLAY" ]; then
    export CHROMIUM_FLAGS="${CHROMIUM_FLAGS} --ozone-platform=wayland"
    # Chromium sandbox needs user namespaces on Linux
    if [ -f /proc/sys/kernel/unprivileged_userns_clone ]; then
        echo 1 > /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || true
    fi
fi

exec /opt/rootapp/AppRun "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/rootapp

install -Dm644 squashfs-root/Root.png %{buildroot}%{_datadir}/pixmaps/rootapp.png
install -Dm644 squashfs-root/Root.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/rootapp.png

# Remove chrome-sandbox SUID bit — DotNetBrowser bundles its own Chromium sandbox.
# Setting SUID root on chrome-sandbox is a known CVE vector (CVE-2021-38003 etc).
if [ -f %{buildroot}/opt/rootapp/chrome-sandbox ]; then
    rm -f %{buildroot}/opt/rootapp/chrome-sandbox
fi

install -dm755 %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/rootapp.desktop <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=Root
Comment=Root App is a new Discord alternative, designed for gaming communities and large online groups
Exec=rootapp %U
Icon=rootapp
Terminal=false
StartupWMClass=Root
Categories=Network;InstantMessaging;
MimeType=x-scheme-handler/rootapp;
DESKTOP_EOF

%files
%{_bindir}/rootapp
/opt/rootapp/
%{_datadir}/applications/rootapp.desktop
%{_datadir}/icons/hicolor/*/apps/rootapp.png
%{_datadir}/pixmaps/rootapp.png

%changelog
* Tue Jul 29 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.119-2
- Added missing dependencies: libglvnd, mesa-libGL, icu, freetype2
- Added Provides/Conflicts for root-app
- Removed chrome-sandbox SUID bit (security CVE vector)

* Sat Jul 18 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.119-1
- Auto-update to 0.9.119 via update.sh
