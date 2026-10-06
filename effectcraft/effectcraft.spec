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

# Upstream's nfpm rpm declares libxkbcommon, vulkan-loader|libglvnd-egl and
# alsa-lib. Fedora names: vulkan-loader, mesa-libGL, libX11, libXcursor, libXi,
# libXrandr, xkeyboard-config, hicolor-icon-theme, desktop-file-utils.
Requires:       alsa-lib
Requires:       libX11
Requires:       libXcursor
Requires:       libXi
Requires:       libXrandr
Requires:       libxkbcommon
Requires:       mesa-libGL
Requires:       vulkan-loader
Requires:       xkeyboard-config
Requires:       hicolor-icon-theme
# wgpu picks the backend at runtime: Vulkan when available, else GL.
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal

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

# hicolor icons are already named after the appid in every size dir.
for i in usr/share/icons/hicolor/*/apps/%{appid}.png; do
    [ -e "$i" ] || continue
    size=$(basename "$(dirname "$(dirname "$i")")")
    install -Dm0644 "$i" \
        %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/%{appid}.png
done

# AppStream metadata (metainfo.xml.in with @VERSION@/@DATE@ already expanded).
install -Dm0644 usr/share/metainfo/%{appid}.metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/%{appid}.metainfo.xml

# shared-mime-info package; upstream ships an (empty) mime file, harmless.
if [ -d usr/share/mime ]; then
  mkdir -p %{buildroot}%{_datadir}/mime
  cp -a usr/share/mime/. %{buildroot}%{_datadir}/mime/
fi

desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop

%files
%license usr/share/doc/effectcraft/LICENSE-MIT
%license usr/share/doc/effectcraft/LICENSE-APACHE
%doc usr/share/doc/effectcraft/README.md
%{_bindir}/effectcraft
%{_bindir}/effectcraft-cli
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_datadir}/mime

%post
# || : so a locked icon cache never fails the install.
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%changelog
* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.0-1
- Initial packaging: repack upstream nfpm rpm (native Rust app, no sandbox)