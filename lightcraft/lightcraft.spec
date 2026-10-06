# Keep upstream appid: renames break StartupWMClass/AppStream matching.
%global appid ai.storyteller.lightcraft

# Native binary: no bundled runtime, so no Provides pruning, no setuid sandbox.
%global debug_package %{nil}

Name:           lightcraft
Version:        0.2.0
Release:        2%{?dist}
Summary:        Photo library and raw development

License:        MIT AND Apache-2.0
URL:            https://getartcraft.com/apps/lightcraft
Source0:        https://github.com/storytold/lightcraft/releases/download/v%{version}/lightcraft-%{version}-linux-x86_64.rpm
# sha256: 5a27a0784305c73957036e2f3d7076d5ec5c270f0c864b9b41676468b0c701c8

# %install runs desktop-file-validate; the buildroot does not provide it.
BuildRequires:  desktop-file-utils

# Verified against upstream nfpm.yaml. The binary dlopens both stacks (eframe
# enables wayland+x11), so loaders are hard Requires. RAW decoding is pure
# Rust in-tree, so no libraw/dcraw runtime dep.
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
LightCraft is a photo library and raw developer: import, organize and grade
photos with its own pure-Rust RAW decoders (DNG, CR2, ARW, NEF, RAF, RW2, PEF,
ORF), a disk thumbnail cache and GPU compositing.

%prep
%setup -T -c
# Upstream rpm is a plain FHS tree (see packaging/linux/package.sh); repack it.
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}%{_bindir}
install -m755 usr/bin/lightcraft %{buildroot}%{_bindir}/lightcraft
install -m755 usr/bin/lightcraft-cli %{buildroot}%{_bindir}/lightcraft-cli

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

desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop

%files
%license usr/share/doc/lightcraft/LICENSE-MIT
%license usr/share/doc/lightcraft/LICENSE-APACHE
%doc usr/share/doc/lightcraft/README.md
%{_bindir}/lightcraft
%{_bindir}/lightcraft-cli
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/icons/hicolor/*/apps/%{appid}.svg
%{_datadir}/metainfo/%{appid}.metainfo.xml

%post
# || : so a locked icon cache never fails the install.
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%changelog
* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-2
- Add BuildRequires: desktop-file-utils for desktop-file-validate in %install

* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-1
- Initial packaging: repack upstream nfpm rpm (native Rust app, no sandbox)
