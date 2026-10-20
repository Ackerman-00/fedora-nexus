# MAINTENANCE: ackerman/nexus COPR only — auto-update DISABLED (2026-09-17).
%global             debug_package %{nil}
# COPR release runs unreliable - manual bump only
%global             helium_base /opt/helium

# Bundled Chromium libs must not become Provides.
%global __provides_exclude_from ^%{helium_base}/.*$

Name:               helium-browser
Version:        0.19.4.1
Release:        1%{?dist}
Summary:            Private, fast, and honest web browser

License:            GPL-3.0-only AND BSD-3-Clause
URL:                https://github.com/imputnet/helium-linux
Source0:            https://github.com/imputnet/helium-linux/releases/download/%{version}/helium-%{version}-x86_64_linux.tar.xz
# sha256: 6ca6e4a00fef5916821fb1af8a9607cc6b386f678a7eb422e55f19116ba30469
Source1:            https://raw.githubusercontent.com/imputnet/helium-linux/%{version}/package/net.imput.helium.metainfo.xml
# Tarball lacks license texts; stage from the tag.
Source2:            https://raw.githubusercontent.com/imputnet/helium-linux/%{version}/LICENSE
Source3:            https://raw.githubusercontent.com/imputnet/helium-linux/%{version}/LICENSE.ungoogled_chromium

ExclusiveArch:      x86_64

# www-browser convention shared by Fedora's firefox/chromium packages
Provides:           www-browser = %{version}-%{release}

Requires:           hicolor-icon-theme
# xdg-* helpers are runtime-called, not ELF-linked.
Requires:           xdg-utils
# Chromium dlopens dbus; auto-deps miss it.
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
* Sat Oct 17 2026 Ackerman-00 <quietcraft@gmail.com> - 0.19.4.1-1
- Update to upstream release 0.19.4.1 (Chromium 155.0.8059.84)
* Wed Oct 14 2026 Ackerman-00 <quietcraft@gmail.com> - 0.19.3.1-1
- Update to upstream release 0.19.3.1 (Chromium 155.0.8059.79)
* Fri Oct 09 2026 Ackerman-00 <quietcraft@gmail.com> - 0.19.2.1-1
- Update to upstream release 0.19.2.1 (Chromium 155.0.8059.39 revision 2:
  browser-level exceptions for Google services, DBSC flags restored)

* Thu Oct 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.19.1.2-1
- Update to upstream release 0.19.1.2 (Chromium 155.0.8059.39)
