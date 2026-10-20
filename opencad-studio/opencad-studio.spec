# Keep upstream appid: renames break StartupWMClass/AppStream matching.
%global appid io.github.HakanSeven12.OpenCadStudio

# Prebuilt binary: no debuginfo to extract.
%global debug_package %{nil}
# The AppImage tree ships private copies of system libraries; they must never
# be advertised as system-wide Provides (same hijack class as fluxer/helium).
%global __provides_exclude_from ^/opt/opencad-studio/.*$
%global __requires_exclude_from ^/opt/opencad-studio/.*$

Name:           opencad-studio
Version:        2026.42
Release:        2%{?dist}
Summary:        Open-source 2D/3D CAD with native DWG/DXF support

License:        GPL-3.0-only
URL:            https://www.opencadstudio.com
ExclusiveArch:  x86_64
Source0:        https://github.com/HakanSeven12/OpenCADStudio/releases/download/v2026.42/OpenCADStudio-v2026.42-linux-x86_64.AppImage
# The AppImage carries no license text; the repo has the GPL-3.0 at the tag.
Source1:        https://raw.githubusercontent.com/HakanSeven12/OpenCADStudio/v%{version}/LICENSE
# sha256: 3c0cc42bb7266ed67a1a5be7548ed954d3951a4c8867bed2840e9a9c685b337a

# AppImage teardown needs readelf (ELF offset) + unsquashfs.
BuildRequires:  binutils
BuildRequires:  squashfs-tools
BuildRequires:  coreutils
BuildRequires:  desktop-file-utils

# Runtime deps: iced/wgpu stack dlopened at runtime (winit wayland+x11
# backends, wgpu Vulkan with GL fallback), so loaders are hard Requires.
# Matches the snap stage-packages mapped to Fedora names.
Requires:       dbus
Requires:       fontconfig
Requires:       freetype
Requires:       libX11
Requires:       libXcursor
Requires:       libXext
Requires:       libXi
Requires:       libXinerama
Requires:       libXrandr
Requires:       libwayland-client
Requires:       libxcb
Requires:       libxkbcommon
Requires:       libxkbcommon-x11
Requires:       mesa-libGL
Requires:       mesa-dri-drivers
Requires:       vulkan-loader
Requires:       xkeyboard-config
Requires:       hicolor-icon-theme
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal
Recommends:     xdg-utils

%description
Open CAD Studio is an open-source 2D/3D CAD application with native DWG/DXF
read and write, built in Rust. No FreeCAD or OCCT inside: geometry kernel,
codecs and renderers are its own crates.

%prep
%setup -T -c
# Extract the Type 2 AppImage via the ELF section-header offset.
OFFSET=$(LC_ALL=C readelf -h %{SOURCE0} | awk 'NR==13{e_shoff=$5} NR==18{e_shentsize=$5} NR==19{e_shnum=$5} END{print e_shoff+e_shentsize*e_shnum}')
unsquashfs -q -d squashfs-root -o "$OFFSET" %{SOURCE0}
chmod go-w squashfs-root

%install
# The AppImage tree is FHS usr/-rooted; flatten one level so the tree lands
# as /opt/opencad-studio/{bin,lib,share} and the wrapper path below holds.
mkdir -p %{buildroot}/opt/opencad-studio
cp -a squashfs-root/usr/* %{buildroot}/opt/opencad-studio/

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/opencad-studio <<'EOF'
#!/bin/sh
exec /opt/opencad-studio/bin/OpenCADStudio "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/opencad-studio

# Ship the upstream desktop entry (Icon/StartupWMClass already match the
# appid); only Exec is repointed at the PATH wrapper.
install -Dm0644 squashfs-root/usr/share/applications/%{appid}.desktop \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop
sed -i 's|^Exec=.*|Exec=opencad-studio %F|' \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop

# Upstream renders one 256x256 icon from its SVG at build time.
install -Dm0644 squashfs-root/usr/share/icons/hicolor/256x256/apps/%{appid}.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{appid}.png

install -Dm0644 squashfs-root/usr/share/metainfo/%{appid}.metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/%{appid}.metainfo.xml

desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop

# Upstream GPL-3.0 license text (the AppImage ships none)
install -Dm0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/opencad-studio
/opt/opencad-studio/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/metainfo/%{appid}.metainfo.xml

%post
# || : so a locked icon cache never fails the install.
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 2026.42-2
- Ship the upstream GPL-3.0 LICENSE (Source1, same v2026.42 tag as
  Source0); the AppImage payload carries no license text.

* Sun Oct 18 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.42-1
- Auto-update to upstream release v2026.42
