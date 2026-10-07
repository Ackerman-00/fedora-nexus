# Keep upstream appid: renames break StartupWMClass/AppStream matching.
%global appid ai.storyteller.effectcraft

# Native binary: no bundled runtime, so no Provides pruning, no setuid sandbox.
%global debug_package %{nil}

Name:           effectcraft
Version:        0.4.0
Release:        1%{?dist}
Summary:        Motion graphics and visual effects compositor

License:        MIT AND Apache-2.0
URL:            https://getartcraft.com/apps/effectcraft
Source0:        https://github.com/storytold/effectcraft/releases/download/v0.4.0/effectcraft-%{version}-linux-x86_64.rpm
# sha256: 5d78104047a135bcf5ee098fb80693ab16ed954ebfa2adfe3ea5a23678448a9d

# %install runs desktop-file-validate; the buildroot does not provide it.
BuildRequires:  desktop-file-utils

# Verified against upstream nfpm.yaml and the AUR repack. The binary dlopens
# both stacks (eframe enables wayland+x11), so loaders are hard Requires.
# Arch->Fedora: libglvnd->mesa-libGL, vulkan-icd-loader->vulkan-loader.
Requires:       alsa-lib
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
EffectCraft is a motion graphics editor and visual effects compositor in the
spirit of After Effects: compositions, layers, keyframes, 306 effects, layer
styles, expressions, 3D cameras and lights, and a render queue. Lottie import
and export, a readable JSON project format, pure Rust video and audio codecs,
and an MCP server for agents.

%prep
%setup -T -c
# Upstream rpm is a plain FHS tree (see packaging/linux/package.sh); repack it.
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}%{_bindir}
install -m755 usr/bin/effectcraft %{buildroot}%{_bindir}/effectcraft
install -m755 usr/bin/effectcraft-cli %{buildroot}%{_bindir}/effectcraft-cli

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
%license usr/share/doc/effectcraft/LICENSE-MIT
%license usr/share/doc/effectcraft/LICENSE-APACHE
%doc usr/share/doc/effectcraft/README.md
%{_bindir}/effectcraft
%{_bindir}/effectcraft-cli
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
* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.0-1
- Auto-update to upstream release v0.4.0
