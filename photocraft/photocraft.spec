# Keep upstream appid: renames break StartupWMClass/AppStream matching.
%global appid ai.storyteller.photocraft

# Native binary: no bundled runtime, so no Provides pruning, no setuid sandbox.
%global debug_package %{nil}

Name:           photocraft
Version:        0.3.0
Release:        1%{?dist}
Summary:        Native image editor with layers, masks and PSD support

License:        MIT AND Apache-2.0
URL:            https://getartcraft.com/apps/photocraft
Source0:        https://github.com/storytold/photocraft/releases/download/v0.3.0/photocraft-%{version}-linux-x86_64.rpm
# sha256: ab77bd759e4e667eac0fba4278e8e130fe1e7edf1e3f7ccc8d09cd430eb5f8d8

# %install runs desktop-file-validate; the buildroot does not provide it.
BuildRequires:  desktop-file-utils

# Verified against upstream nfpm.yaml. The binary dlopens both stacks (eframe
# enables wayland+x11), so loaders are hard Requires.
# Arch->Fedora: libglvnd->mesa-libGL, vulkan-icd-loader->vulkan-loader.
Requires:       dbus
Requires:       libX11
Requires:       libXcursor
Requires:       libXi
Requires:       libXrandr
Requires:       libwayland-client
Requires:       libxkbcommon
Requires:       libxkbcommon-x11
Requires:       mesa-libGL
Requires:       vulkan-loader
Requires:       xkeyboard-config
Requires:       hicolor-icon-theme
# wgpu picks Vulkan or GL at runtime; drivers stay Recommends.
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal
Recommends:     xdg-utils

%description
PhotoCraft is a native image editor: layers, masks, adjustment layers, layer
styles, type and brushes. It opens and saves layered PSD/PSB files and
8/16/32-bit documents, with GPU compositing and a headless CLI converter.

%prep
%setup -T -c
# Upstream rpm is a plain FHS tree (see packaging/linux/package.sh); repack it.
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}%{_bindir}
install -m755 usr/bin/photocraft %{buildroot}%{_bindir}/photocraft
install -m755 usr/bin/photocraft-cli %{buildroot}%{_bindir}/photocraft-cli

# Ship the desktop file as-is: Icon/StartupWMClass already match the appid.
install -Dm0644 usr/share/applications/%{appid}.desktop \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop

# Fixed pngs plus one scalable svg; the .attribution sidecar is not shipped.
for size in 16x16 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    i=usr/share/icons/hicolor/$size/apps/%{appid}.png
    [ -e "$i" ] || continue
    install -Dm0644 "$i" \
        %{buildroot}%{_datadir}/icons/hicolor/$size/apps/%{appid}.png
done
i=usr/share/icons/hicolor/scalable/apps/%{appid}.svg
[ -e "$i" ] && install -Dm0644 "$i" \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg
true

install -Dm0644 usr/share/metainfo/%{appid}.metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/%{appid}.metainfo.xml

# Unlike its siblings, photocraft declares real MIME types (its own
# application/x-photocraft plus image/x-psb and image/qoi), so ship the dir.
if [ -d usr/share/mime ]; then
  mkdir -p %{buildroot}%{_datadir}/mime
  cp -a usr/share/mime/. %{buildroot}%{_datadir}/mime/
fi

desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop

%files
%license usr/share/doc/photocraft/LICENSE-MIT
%license usr/share/doc/photocraft/LICENSE-APACHE
%doc usr/share/doc/photocraft/README.md
%{_bindir}/photocraft
%{_bindir}/photocraft-cli
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/icons/hicolor/*/apps/%{appid}.svg
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_datadir}/mime

%post
# || : so a locked icon cache never fails the install.
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%changelog
* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.0-1
- Auto-update to upstream release v0.3.0
