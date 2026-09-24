# MAINTENANCE: ackerman/nexus COPR only — auto-update DISABLED (2026-09-17).
# Helium re-releases often (Chromium rebuilds, sometimes tag-before-assets)
# and each bump re-downloads ~130MB; updates are done deliberately by the
# maintainer, not by update-engine.yml. update.sh is an intentional no-op
# (kept so the generic scanner keeps skipping this spec). To update: bump
# Version, verify tarball + tag assets exist, push (COPR auto-builds),
# confirm the new build is green.
%global             debug_package %{nil}
%global             helium_base /opt/helium

# Helium ships private Chromium/Electron libraries (libEGL, libGLESv2,
# libvulkan.so.1, swiftshader, qt shims) under %{helium_base}. They live
# outside the loader path and must never be advertised as system-wide
# Provides: dnf once picked helium-browser as the provider of
# libvulkan.so.1()(64bit) for wlroots, leaving umbriel unstartable
# (libvulkan.so.1 => not found). Proven by combined install test 2026-09-05.
%global __provides_exclude_from ^%{helium_base}/.*$

Name:               helium-browser
Version:        0.18.1.1
Release:        1%{?dist}
Summary:            Private, fast, and honest web browser

License:            GPL-3.0-only AND BSD-3-Clause
URL:                https://github.com/imputnet/helium-linux
Source0:            https://github.com/imputnet/helium-linux/releases/download/%{version}/helium-%{version}-x86_64_linux.tar.xz
# sha256: 9f4d35239eea18b290846221874265ac2a8637adff954df69fdef77d6b15042c
# The official binary tarball does not ship the metainfo file, so pull it
# from the repo at the matching release tag (all release tags carry it).
Source1:            https://raw.githubusercontent.com/imputnet/helium-linux/%{version}/package/net.imput.helium.metainfo.xml
# The binary tarball carries no license texts either (s6muel fetches
# LICENSE.ungoogled_chromium from the tag too); stage both for %license.
Source2:            https://raw.githubusercontent.com/imputnet/helium-linux/%{version}/LICENSE
Source3:            https://raw.githubusercontent.com/imputnet/helium-linux/%{version}/LICENSE.ungoogled_chromium

ExclusiveArch:      x86_64

# www-browser convention shared by Fedora's firefox/chromium packages
Provides:           www-browser = %{version}-%{release}

Requires:           hicolor-icon-theme
# Chromium calls xdg-mime/xdg-settings/xdg-open at runtime (not ELF-linked,
# so auto-deps miss it). Same as Fedora's chromium package.
Requires:           xdg-utils
# Chromium dlopens dbus at runtime (invisible to ELF auto-deps); s6muel's dep
# review and CachyOS both list dbus explicitly.
Requires:           dbus-daemon
Requires(post):     desktop-file-utils
Requires(post):     gtk-update-icon-cache
Requires(postun):   gtk-update-icon-cache

Recommends:         liberation-fonts
Recommends:         vulkan-loader

%description
Helium is a private, fast, and honest web browser based on Chromium.
It strips Google services, telemetry and other privacy-invasive features,
while keeping the Chromium browsing experience.

%prep
%setup -q -n helium-%{version}-x86_64_linux

# Stage the tag-fetched license texts for %license (see Source2/Source3).
cp %{SOURCE2} LICENSE.GPL-3.0-only
cp %{SOURCE3} LICENSE.ungoogled_chromium

%build
# Using prebuilt binaries

%install
mkdir -p %{buildroot}%{helium_base} \
         %{buildroot}%{_bindir} \
         %{buildroot}%{_datadir}/applications \
         %{buildroot}%{_datadir}/metainfo \
         %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

cp -a . %{buildroot}%{helium_base}

# Brand the wrapper so bug reports show the distribution the build came from
sed -Ei "s/(CHROME_VERSION_EXTRA=).*/\1rpm/" \
    %{buildroot}%{helium_base}/helium-wrapper

install -m 644 product_logo_256.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/helium.png

install -m 644 %{buildroot}%{helium_base}/helium.desktop \
    %{buildroot}%{_datadir}/applications/

install -m 644 %{SOURCE1} \
    %{buildroot}%{_datadir}/metainfo/net.imput.helium.metainfo.xml

ln -sf %{helium_base}/helium-wrapper %{buildroot}%{_bindir}/helium

%post
# Refresh the desktop database and icon cache
/usr/bin/update-desktop-database > /dev/null 2>&1 || :
/bin/touch --no-create %{_datadir}/icons/hicolor > /dev/null 2>&1 || :

%postun
/usr/bin/update-desktop-database > /dev/null 2>&1 || :
case "$1" in
    0)
        /bin/touch --no-create %{_datadir}/icons/hicolor > /dev/null 2>&1
        /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor > /dev/null 2>&1 || :
        ;;
esac

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor > /dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%license LICENSE.GPL-3.0-only
%license LICENSE.ungoogled_chromium
%{helium_base}/
%{_bindir}/helium
%{_datadir}/applications/helium.desktop
%{_datadir}/metainfo/net.imput.helium.metainfo.xml
%{_datadir}/icons/hicolor/256x256/apps/helium.png

%changelog
* Thu Sep 24 2026 Ackerman-00 <quietcraft@gmail.com> - 0.18.1.1-1
- Update to upstream release 0.18.1.1 (Chromium 154.0.8037.57)
* Fri Sep 18 2026 Ackerman-00 <quietcraft@gmail.com> - 0.17.2.1-1
- Update to upstream release 0.17.2.1 (Chromium 153.0.8010.52, uBlock 1.75.0)
* Thu Sep 17 2026 Ackerman-00 <quietcraft@gmail.com> - 0.17.1.1-2
- Ship license texts (%license LICENSE + LICENSE.ungoogled_chromium from tag; License tag now GPL-3.0-only AND BSD-3-Clause, matching Terra/s6muel)
- Add Requires: dbus-daemon (Chromium dlopens dbus, invisible to auto-deps)
- COPR-only manual maintenance, auto-update disabled (update.sh is now a no-op)
* Wed Sep 16 2026 Ackerman-00 <quietcraft@gmail.com> - 0.17.1.1-1
- Auto-update to upstream release 0.17.1.1
