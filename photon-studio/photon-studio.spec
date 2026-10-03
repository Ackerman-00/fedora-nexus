%global debug_package %{nil}
%global __os_install_post %{nil}

# Electron app extracted from the upstream AppImage. Everything the app needs
# travels under /opt/photon-studio, so bundled Chromium libraries must not
# leak into system Provides/Requires; genuine system deps are declared below.
%global __provides_exclude_from ^/opt/photon-studio/.*$
%global __requires_exclude_from ^/opt/photon-studio/.*$

Name:           photon-studio
Version:        0.1.39
Release:        1%{?dist}
Summary:        Offline image editor with native PSD support

# No app-level license ships in the AppImage (only Electron/Chromium texts);
# Photon Studio is gratis proprietary software (tenzen.studio sells a suite
# around it). Same treatment as rootapp.spec in this repo.
License:        Proprietary
URL:            https://tenzen.studio
Source0:        https://downloads.tenzen.studio/photon/stable/linux/0.1.39/Photon-Studio-0.1.39-linux-x64.AppImage
# sha256: 3bfe9ce6e3c6f06908c9e323ebd6512a8e5ed5fcc086f27fdd2155f56fd81b8d

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  squashfs-tools
BuildRequires:  coreutils

# Electron runtime deps (same Chromium base as openchamber/rootapp specs)
Requires:       gtk3
Requires:       nss
Requires:       nspr
Requires:       alsa-lib
Requires:       libnotify
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       hicolor-icon-theme
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libX11
Requires:       libxkbcommon
Requires:       mesa-libgbm
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       fontconfig
Requires:       freetype
Requires:       cups-libs
Requires:       dbus-libs
Requires:       libsecret
Requires:       systemd-libs

Provides:       photon-studio = %{version}-%{release}

%description
Photon Studio is an offline image editor with Photoshop-equivalent
capabilities and native PSD/PSB support: layers, masks, adjustment layers,
RAW development, local AI selections, and Photoshop shortcuts, brushes and
scripts. Free, no account.

%prep
%setup -c -T

# Extract the Type 2 AppImage (ELF section header offset method)
OFFSET=$(LC_ALL=C readelf -h %{SOURCE0} | awk 'NR==13{e_shoff=$5} NR==18{e_shentsize=$5} NR==19{e_shnum=$5} END{print e_shoff+e_shentsize*e_shnum}')
unsquashfs -q -d squashfs-root -o "$OFFSET" %{SOURCE0}
chmod go-w squashfs-root

%build
# Nothing to compile.

%install
install -dm755 %{buildroot}/opt/photon-studio
cp -ar squashfs-root/* %{buildroot}/opt/photon-studio/

install -dm755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/photon-studio <<'WRAPPER_EOF'
#!/bin/sh
export APPDIR="/opt/photon-studio"
exec /opt/photon-studio/AppRun "$@"
WRAPPER_EOF
chmod 755 %{buildroot}%{_bindir}/photon-studio

install -Dm644 squashfs-root/usr/share/icons/hicolor/512x512/apps/photon-studio.png \
    %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/photon-studio.png

# Upstream desktop entry runs AppRun directly; ours goes through the PATH
# wrapper with the SUID sandbox intact (see %files %attr below). MimeTypes
# kept: this is an image editor that opens PSD/RAW/photo formats.
install -dm755 %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/photon-studio.desktop <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=Photon Studio
Comment=Offline image editor with native PSD support
Exec=photon-studio %U
Icon=photon-studio
Terminal=false
StartupWMClass=photon-studio
MimeType=application/x-photon;application/pdf;image/svg+xml;image/vnd.adobe.photoshop;image/x-photoshop;image/psd;image/x-psb;image/png;image/jpeg;image/tiff;image/gif;image/bmp;image/x-bmp;image/webp;image/avif;image/heic;image/heif;image/jxl;image/x-dcraw;image/x-adobe-dng;image/x-canon-cr2;image/x-canon-cr3;image/x-canon-crw;image/x-epson-erf;image/x-fuji-raf;image/x-hasselblad-3fr;image/x-hasselblad-fff;image/x-kodak-dcr;image/x-kodak-kdc;image/x-leaf-mos;image/x-mamiya-mef;image/x-minolta-mdc;image/x-minolta-mrw;image/x-nikon-nef;image/x-nikon-nrw;image/x-olympus-orf;image/x-panasonic-rw;image/x-panasonic-rw2;image/x-pentax-pef;image/x-phaseone-iiq;image/x-samsung-srw;image/x-sigma-x3f;image/x-sony-arw;image/x-sony-sr2;image/x-sony-srf;
Categories=Graphics;Photography;
DESKTOP_EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/photon-studio.desktop || true

%files
%{_bindir}/photon-studio
/opt/photon-studio/
%{_datadir}/applications/photon-studio.desktop
%{_datadir}/icons/hicolor/512x512/apps/photon-studio.png
# Chromium SUID sandbox MUST stay setuid root (AGENTS.md Electron rule, Oct 2026:
# 0755 fatally aborts launch for every non-root user, proven rc=133 under xvfb).
%attr(4755, root, root) /opt/photon-studio/chrome-sandbox

%changelog
* Sat Oct 03 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.39-1
- Auto-update to upstream release 0.1.39
