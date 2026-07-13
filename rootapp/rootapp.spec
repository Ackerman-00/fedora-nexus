%global debug_package %{nil}
%global __os_install_post %{nil}
%global __requires_exclude_from ^/opt/rootapp/.*$
%global __provides_exclude_from ^/opt/rootapp/.*$

Name:           rootapp
Version:        0.9.118
Release:        3%{?dist}
Summary:        Root App is a new Discord alternative, designed for gaming communities and large online groups

License:        Proprietary
URL:            https://www.rootapp.com
ExclusiveArch:  x86_64

Source0:        https://installer.rootapp.com/installer/Linux/X64/Root.AppImage
# sha256: 7d0ad57e26fd235a926283224b23e1556536920c8a28e04b3ba532dc61dc6c92

BuildRequires:  binutils
BuildRequires:  squashfs-tools
BuildRequires:  coreutils

Requires:       gtk3
Requires:       nss
Requires:       alsa-lib
Requires:       libnotify
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       hicolor-icon-theme
Requires:       zlib
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
Requires:       libxkbcommon
Requires:       mesa-libgbm
Requires:       libsecret
Requires:       fontconfig
Requires:       cairo
Requires:       pango
Requires:       gdk-pixbuf2
Requires:       harfbuzz
Requires:       cups-libs
Requires:       pulseaudio-libs
Requires:       openssl-libs
Requires:       vulkan-loader
Requires:       nspr
Requires:       dbus-libs
Requires:       wl-clipboard
Requires:       libwayland-client
Requires:       libwayland-cursor
Requires:       libwayland-egl
Requires:       libdrm
Requires:       at-spi2-atk

Provides:       rootapp = %{version}-%{release}

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
export AVALONIA_PLATFORM=Wayland
export GDK_BACKEND=wayland
exec /opt/rootapp/AppRun "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/rootapp

install -Dm644 squashfs-root/Root.png %{buildroot}%{_datadir}/pixmaps/rootapp.png
install -Dm644 squashfs-root/Root.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/rootapp.png

if [ -f %{buildroot}/opt/rootapp/chrome-sandbox ]; then
    chmod 4755 %{buildroot}/opt/rootapp/chrome-sandbox
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
* Mon Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.118-3
- Add AVALONIA_PLATFORM=Wayland + GDK_BACKEND=wayland to wrapper (fix Wayland clipboard)
- Add Requires: wl-clipboard for wl-copy/wl-paste clipboard bridge
* Sat Jul 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.118-2
- Fix wayland -> libwayland-{client,cursor,egl} (Fedora 44 split subpackages)
- Use Nix-style extraction (readelf + unsquashfs -o) for correct offset
- Add APPDIR wrapper script matching AppImage runtime environment
- Disable brp strip/post-install to protect .NET bundle-embedded binary
- Add complete runtime Requires matching Nix FHS multiPkgs
* Sat Jul 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.118-1
- Initial package of Root App for Fedora Copr from AppImage
