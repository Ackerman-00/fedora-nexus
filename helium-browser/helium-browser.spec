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
Version:        0.16.5.1
Release:        2%{?dist}
Summary:            Private, fast, and honest web browser

License:            GPL-3.0-only
URL:                https://github.com/imputnet/helium-linux
Source0:            https://github.com/imputnet/helium-linux/releases/download/%{version}/helium-%{version}-x86_64_linux.tar.xz
# The official binary tarball does not ship the metainfo file, so pull it
# from the repo at the matching release tag (all release tags carry it).
Source1:            https://raw.githubusercontent.com/imputnet/helium-linux/%{version}/package/net.imput.helium.metainfo.xml

ExclusiveArch:      x86_64

# www-browser convention shared by Fedora's firefox/chromium packages
Provides:           www-browser = %{version}-%{release}

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
%{helium_base}/
%{_bindir}/helium
%{_datadir}/applications/helium.desktop
%{_datadir}/metainfo/net.imput.helium.metainfo.xml
%{_datadir}/icons/hicolor/256x256/apps/helium.png

%changelog
* Sat Sep 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.16.5.1-2
- Stop advertising bundled /opt/helium libs (libEGL, libGLESv2,
  libvulkan.so.1, ...) as system Provides via __provides_exclude_from;
  dnf had picked helium-browser as libvulkan provider for wlroots,
  breaking umbriel startup. Spec-only fix, same upstream version.
* Sat Sep 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.16.5.1-1
- Auto-update to upstream release 0.16.5.1
