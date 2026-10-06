# Native appid kept as upstream's (apps are reverse-DNS; renaming them breaks
# desktop StartupWMClass matching, AppStream ids and the shared-mime-info cache).
%global appid ai.storyteller.effectcraft

# Native Rust binary, not Electron: no bundled Chromium runtime, no SUID
# sandbox helper, no Provides/Requires pruning needed.
%global debug_package %{nil}

Name:           effectcraft
Version:        0.3.0
Release:        1%{?dist}
Summary:        Motion graphics and visual effects compositor

License:        MIT AND Apache-2.0
URL:            https://getartcraft.com/apps/effectcraft
Source0:        https://github.com/storytold/effectcraft/releases/download/v%{version}/effectcraft-%{version}-linux-x86_64.rpm
# sha256: c1f1bdb97c60dad9376570f74f35fd7d0673f794494c1098d9844b6bec643fc6

# Runtime deps, two independent sources agree:
#  1. upstream's own rpm override (packaging/linux/nfpm.yaml) depends
#     libxkbcommon, (vulkan-loader or libglvnd-egl), alsa-lib; recommends
#     libwayland-client, libX11, libXcursor, libXi, libXrandr,
#     mesa-vulkan-drivers, xdg-desktop-portal.
#  2. the AUR effectcraft-bin repack, which had to satisfy the same binary on
#     a real distro: glibc, gcc-libs, libxkbcommon, libxkbcommon-x11, libx11,
#     libxcursor, libxi, libxrandr, wayland, libglvnd, vulkan-icd-loader, dbus,
#     alsa-lib; optdepends vulkan-driver, xdg-desktop-portal, xdg-utils.
# Upstream states the binary links only glibc and libgcc_s directly and
# dlopens the windowing and GPU stacks, so every name here is resolved at
# runtime, not via ELF NEEDED.
# apps/effectcraft/Cargo.toml enables eframe features "wayland" and "x11", so
# BOTH stacks are needed to launch: hard Requires on the loaders, matching the
# Electron packages in this repo (rootapp, helium-browser).
# Arch -> Fedora name map: libglvnd -> mesa-libGL (provides libGL.so.1),
# vulkan-icd-loader -> vulkan-loader (libvulkan.so.1), wayland ->
# libwayland-client (libwayland-client.so.0), gcc-libs -> libgcc (glibc/libgcc
# are resolved by the buildroot automatically, so they are not listed).
Requires:       alsa-lib
# eframe's "links" feature shells out to xdg-open for Help/Discord/Settings.
Requires:       dbus
Requires:       libX11
Requires:       libXcursor
Requires:       libXi
Requires:       libXrandr
Requires:       libwayland-client
Requires:       libxkbcommon
# winit's X11 backend needs the X11-xkb bridge lib.
Requires:       libxkbcommon-x11
Requires:       mesa-libGL
Requires:       vulkan-loader
# xkbcommon loads keymaps from xkeyboard-config at runtime.
Requires:       xkeyboard-config
Requires:       hicolor-icon-theme
# wgpu picks the backend at runtime: Vulkan when available, else GL (v0.3.0
# added a GL backend for Linux without Vulkan). Drivers stay Recommends.
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal
# The desktop entry advertises x-scheme-handler via TryExec/Exec only; eframe's
# "links" feature needs xdg-open to open Help, Discord and Settings pages.
Recommends:     xdg-utils

%description
EffectCraft is a motion graphics editor and visual effects compositor in the
spirit of After Effects: compositions, layers, keyframes, 306 effects, layer
styles, expressions, 3D cameras and lights, and a render queue. Lottie import
and export, a readable JSON project format, pure Rust video and audio codecs,
and an MCP server for agents.

%prep
%setup -T -c
# Upstream builds an FHS tree (packaging/linux/package.sh: usr/bin/effectcraft,
# usr/bin/effectcraft-cli, usr/share/{applications,mime,metainfo,icons,doc})
# and hands it to nfpm, so the rpm is a plain tree to repack.
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}%{_bindir}
install -m755 usr/bin/effectcraft %{buildroot}%{_bindir}/effectcraft
install -m755 usr/bin/effectcraft-cli %{buildroot}%{_bindir}/effectcraft-cli

# /usr/share/doc is owned by %doc/%license from the source tree, so it is
# never copied into the buildroot (rpm installs those paths itself).

# Upstream desktop file already matches Fedora conventions (Icon= is the
# appid, StartupWMClass= is the appid); ship it as-is.
install -Dm0644 usr/share/applications/%{appid}.desktop \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop

# hicolor icons are already named after the appid in every size dir. Upstream
# ships fixed pngs (16..512) and one scalable/apps/<appid>.svg, so glob png
# and svg: a png-only glob silently drops the scalable icon. The
# <appid>.svg.attribution sidecar is a repo file, not an install artifact.
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

# AppStream metadata (metainfo.xml.in with @VERSION@/@DATE@ already expanded).
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
* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.0-1
- Initial packaging: repack upstream nfpm rpm (native Rust app, no sandbox)