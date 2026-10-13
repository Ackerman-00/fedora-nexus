# Keep upstream appid: renames break StartupWMClass/AppStream matching.
%global appid ai.storyteller.artcraft-launcher

# NOTE: upstream repo is storytold/craft-launcher but every artifact
# (rpm/deb/AppImage name, binary, desktop file, Cargo crates) is called
# artcraft-launcher - only the RPM package name follows this repo's
# short name; all payload paths keep the upstream artcraft-launcher name.
# Native binary: no bundled runtime, so no Provides pruning, no setuid sandbox.
%global debug_package %{nil}

Name:           craft-launcher
Version:        0.4.0
Release:        1%{?dist}
Summary:        App launcher for the Craft suite

License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/craft-launcher
Source0:        https://github.com/storytold/craft-launcher/releases/download/v0.4.0/artcraft-launcher-0.4.0-linux-x86_64.rpm
# sha256: 69ecfb1b0f9b2f025a289dbd6ff5b0ffdb0af0e47720c9d6304a67271aac93be

ExclusiveArch:  x86_64
# Only the x86_64 rpm is repacked here; upstream also ships aarch64/riscv64
# assets. This repo only enables x86_64 COPR chroots.

BuildRequires:  cpio
BuildRequires:  desktop-file-utils
BuildRequires:  hicolor-icon-theme
# Runtime mapping: upstream's RPM Requires are ALREADY correct soname form
# (packaging/linux/nfpm.yaml rpm.depends, verified against the obs-nexus
# artcraft-launcher packaging). Kept verbatim; only the icon theme is added.
# libgcc_s (NEEDED) stays an auto-dep - the SUSE-only libgcc_s1 name must NOT
# be used here. Payload has no bundled .so needing excludes.
Requires:       hicolor-icon-theme
Requires:       libX11-xcb.so.1()(64bit)
Requires:       libX11.so.6()(64bit)
Requires:       libXcursor.so.1()(64bit)
Requires:       libXi.so.6()(64bit)
Requires:       libvulkan.so.1()(64bit)
Requires:       libEGL.so.1()(64bit)
Requires:       libwayland-client.so.0()(64bit)
Requires:       libxcb.so.1()(64bit)
Requires:       libxkbcommon-x11.so.0()(64bit)
Requires:       libxkbcommon.so.0()(64bit)
# GPU/display helpers stay weak: the launcher runs without them, degraded.
Recommends:     mesa-vulkan-drivers
Recommends:     xdg-desktop-portal

%description
ArtCraft Launcher: the app launcher for the Craft suite of clean-room
creative tools (CAD, audio, video, photo, vector, PDF, design). It lists every
app in the suite, installs the right build for this computer, verifies
downloads against the release SHA-256 checksums, keeps them up to date, and
can live in the system tray. This package retires the standalone *craft apps
(designcraft, effectcraft, filmcraft, lightcraft, photocraft, printcraft,
vectorcraft): install their upstream builds through the launcher instead.

%prep
%setup -q -c -T
# Upstream rpm is a plain FHS tree (see packaging/linux/package.sh); repack it.
rpm2cpio %{SOURCE0} | cpio -idmv

%build
# No compilation required for pre-built binaries

%install
install -d -m 0755 %{buildroot}%{_bindir}
install -m 0755 usr/bin/artcraft-launcher %{buildroot}%{_bindir}/

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
cp -a usr/share/icons %{buildroot}%{_datadir}/
cp -a usr/share/metainfo %{buildroot}%{_datadir}/
cp -a usr/share/doc %{buildroot}%{_datadir}/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop

%files
%license %{_datadir}/doc/artcraft-launcher/LICENSE-APACHE
%license %{_datadir}/doc/artcraft-launcher/LICENSE-MIT
%dir %{_datadir}/doc/artcraft-launcher
%doc %{_datadir}/doc/artcraft-launcher/ATTRIBUTION.md
%doc %{_datadir}/doc/artcraft-launcher/NOTICE
%doc %{_datadir}/doc/artcraft-launcher/README.md
%{_bindir}/artcraft-launcher
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg
%{_datadir}/metainfo/%{appid}.metainfo.xml

%post
# || : so a locked icon cache never fails the install.
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%changelog
* Tue Oct 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.0-1
- Auto-update to upstream release v0.4.0
