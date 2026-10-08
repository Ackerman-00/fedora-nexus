# Keep upstream appid: renames break StartupWMClass/AppStream matching.
%global appid ai.storyteller.filmcraft

# Native binary: no bundled runtime, so no Provides pruning, no setuid sandbox.
%global debug_package %{nil}

Name:           filmcraft
Version:        0.4.0
Release:        1%{?dist}
Summary:        Video editing, color and sound

License:        MIT AND Apache-2.0
URL:            https://getartcraft.com/apps/filmcraft
Source0:        https://github.com/storytold/filmcraft/releases/download/v0.4.0/filmcraft-%{version}-linux-x86_64.rpm
# sha256: 97be65f1cd21073d9f252866cd9df54279f327be913d63a9005df46efb4fd59c

# %install runs desktop-file-validate; the buildroot does not provide it.
BuildRequires:  desktop-file-utils

# Verified against upstream nfpm.yaml and apps/filmcraft/Cargo.toml (cpal for
# audio, eframe wayland+x11, rfd portals). The binary dlopens the windowing
# and GPU stacks, so loaders are hard Requires.
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
FilmCraft is a video editor: cut film, grade color and mix sound with its own
pure Rust codecs (no FFmpeg), plus a headless CLI renderer.

%prep
%setup -T -c
# Upstream rpm is a plain FHS tree (see packaging/linux/package.sh); repack it.
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}%{_bindir}
install -m755 usr/bin/filmcraft %{buildroot}%{_bindir}/filmcraft
install -m755 usr/bin/filmcraft-cli %{buildroot}%{_bindir}/filmcraft-cli

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
%license usr/share/doc/filmcraft/LICENSE-MIT
%license usr/share/doc/filmcraft/LICENSE-APACHE
%doc usr/share/doc/filmcraft/README.md
%{_bindir}/filmcraft
%{_bindir}/filmcraft-cli
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
* Thu Oct 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.0-1
- Auto-update to upstream release v0.4.0
