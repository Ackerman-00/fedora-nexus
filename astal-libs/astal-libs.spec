# These will be automatically populated by update.sh
%global commit          cbcd9f49dd6b9638dc5623b56cc6e1e0a60b593e
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260923200029

%global _lto_cflags %{nil}

Name:           astal-libs
Version:        0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Astal libraries

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        https://github.com/LukashonakV/cava/archive/1.0.0.tar.gz#/cava-1.0.0.tar.gz
Source2:        https://github.com/kotontrion/wl-vapi-gen/archive/refs/tags/1.0.0.tar.gz#/wl-vapi-gen-1.0.0.tar.gz
# Source3 must match lib/workspace/subprojects/wl-vapi-gen.wrap
Source3:        https://github.com/kotontrion/wl-vapi-gen/archive/refs/tags/1.1.0.tar.gz#/wl-vapi-gen-1.1.0.tar.gz

BuildRequires:  gcc
BuildRequires:  iniparser-devel
BuildRequires:  meson
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(appmenu-glib-translator)
BuildRequires:  pkgconfig(dbusmenu-gtk3-0.4)
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(gtk4-wayland)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libnm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(ncursesw)
BuildRequires:  pkgconfig(pam)
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wireplumber-0.5)
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
Development files for %{name}.

%description
%{summary}.

Requires:       libcava%{?_isa} = 1.0.0

%prep
%autosetup -n astal-%{commit} -p1
tar -xf %{SOURCE1} -C lib/cava/subprojects
# never hardcode subproject dirs - upstream adds wrap dirs
for d in lib/*/subprojects lib/*/*/subprojects; do
  if [ -f "$d/wl-vapi-gen.wrap" ]; then
    if grep -q 'directory = wl-vapi-gen-1.1.0' "$d/wl-vapi-gen.wrap"; then
      tar -xf %{SOURCE3} -C "$d"
    else
      tar -xf %{SOURCE2} -C "$d"
    fi
  fi
done

%build
cd lib
# Stage libs into a prefix; COPR runs unprivileged.
mkdir -p %{_builddir}/astal-stage
# Dependents build after the stage prefix is exported.
for lib in quarrel wayland-glib wl/wl; do
  pushd $lib
  meson setup --prefix=%{_builddir}/astal-stage --libdir=lib64 redhat-linux-build . --auto-features=auto
  meson compile -C redhat-linux-build
  meson install -C redhat-linux-build
  popd
done
export PKG_CONFIG_PATH=%{_builddir}/astal-stage/lib64/pkgconfig
export XDG_DATA_DIRS=%{_builddir}/astal-stage/share:/usr/local/share:/usr/share
export CPPFLAGS="-I%{_builddir}/astal-stage/include"
for lib in wl/wl4; do
  pushd $lib
  meson setup --prefix=%{_builddir}/astal-stage --libdir=lib64 redhat-linux-build . --auto-features=auto
  meson compile -C redhat-linux-build
  meson install -C redhat-linux-build
  popd
done
for lib in $(find -maxdepth 1 -mindepth 1 -type d -not -path ./astal -not -path ./quarrel -not -path ./wayland-glib -not -path ./wl); do
  pushd $lib
  %meson --auto-features=auto
  %meson_build
  popd
done

%install
cd lib
for lib in $(find -maxdepth 1 -mindepth 1 -type d -not -path ./astal -not -path ./quarrel -not -path ./wayland-glib -not -path ./wl); do
  pushd $lib
  %meson_install
  popd
done
cp -a %{_builddir}/astal-stage/lib64/* %{buildroot}%{_libdir}/
cp -a %{_builddir}/astal-stage/share/* %{buildroot}%{_datadir}/
cp -a %{_builddir}/astal-stage/include/* %{buildroot}%{_includedir}/
sed -i 's/ cava,//' %{buildroot}%{_libdir}/pkgconfig/astal-cava-0.1.pc
rm -rf %{buildroot}%{_includedir}/cava
rm -rf %{buildroot}%{_datadir}/consolefonts/cava.psf
rm -rf %{buildroot}%{_libdir}/pkgconfig/libcava.pc
# Drop bundled libcava; the standalone package owns it.
rm -rf %{buildroot}%{_libdir}/libcava.so*

%files
%license LICENSE
%config(noreplace) /etc/pam.d/astal-auth
%{_bindir}/astal-apps
%{_bindir}/astal-auth
%{_bindir}/astal-battery
%{_bindir}/astal-brightness
%{_bindir}/astal-greet
%{_bindir}/astal-hyprland
%{_bindir}/astal-mpris
%{_bindir}/astal-notifd
%{_bindir}/astal-power-profiles
%{_bindir}/astal-tray
%{_bindir}/astal-workspace
%{_datadir}/glib-2.0/schemas/io.astal.notifd.gschema.xml
%{_libdir}/girepository-1.0/AstalApps-0.1.typelib
%{_libdir}/girepository-1.0/AstalAuth-0.1.typelib
%{_libdir}/girepository-1.0/AstalBattery-0.1.typelib
%{_libdir}/girepository-1.0/AstalBluetooth-0.1.typelib
%{_libdir}/girepository-1.0/AstalBrightness-0.1.typelib
%{_libdir}/girepository-1.0/AstalCava-0.1.typelib
%{_libdir}/girepository-1.0/AstalGreet-0.1.typelib
%{_libdir}/girepository-1.0/AstalHyprland-0.1.typelib
%{_libdir}/girepository-1.0/AstalIdleNotify-0.1.typelib
%{_libdir}/girepository-1.0/AstalMpris-0.1.typelib
%{_libdir}/girepository-1.0/AstalNetwork-0.1.typelib
%{_libdir}/girepository-1.0/AstalNotifd-0.1.typelib
%{_libdir}/girepository-1.0/AstalPowerProfiles-0.1.typelib
%{_libdir}/girepository-1.0/AstalRiver-0.1.typelib
%{_libdir}/girepository-1.0/AstalTray-0.1.typelib
%{_libdir}/girepository-1.0/AstalWl-0.1.typelib
%{_libdir}/girepository-1.0/AstalWl4-0.1.typelib
%{_libdir}/girepository-1.0/AstalWorkspace-0.1.typelib
%{_libdir}/girepository-1.0/AstalWp-0.1.typelib
%{_libdir}/girepository-1.0/Quarrel-0.1.typelib
%{_libdir}/libastal-apps.so.0{,.*}
%{_libdir}/libastal-auth.so.0{,.*}
%{_libdir}/libastal-battery.so.0{,.*}
%{_libdir}/libastal-bluetooth.so.0{,.*}
%{_libdir}/libastal-brightness.so.0{,.*}
%{_libdir}/libastal-cava.so.0{,.*}
%{_libdir}/libastal-greet.so.0{,.*}
%{_libdir}/libastal-hyprland.so.0{,.*}
%{_libdir}/libastal-idle-notify.so.0{,.*}
%{_libdir}/libastal-mpris.so.0{,.*}
%{_libdir}/libastal-network.so.0{,.*}
%{_libdir}/libastal-notifd.so.0{,.*}
%{_libdir}/libastal-power-profiles.so.0{,.*}
%{_libdir}/libastal-river.so.0{,.*}
%{_libdir}/libastal-tray.so.0{,.*}
%{_libdir}/libastal-wireplumber.so.0{,.*}
%{_libdir}/libastal-wl.so.0{,.*}
%{_libdir}/libastal-wl4.so.0{,.*}
%{_libdir}/libastal-workspace.so.0{,.*}
%{_libdir}/libquarrel.so.0{,.*}

%post
glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :

%postun
glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :

%files devel
%{_datadir}/gir-1.0/Astal*-0.1.gir
%{_datadir}/gir-1.0/Quarrel-0.1.gir
%{_datadir}/vala/vapi/astal-*-0.1.deps
%{_datadir}/vala/vapi/astal-*-0.1.vapi
%{_datadir}/vala/vapi/quarrel-0.1.vapi
%{_includedir}/astal-*.h
%{_includedir}/astal/
%{_includedir}/quarrel.h
%{_libdir}/libastal-apps.so
%{_libdir}/libastal-auth.so
%{_libdir}/libastal-battery.so
%{_libdir}/libastal-bluetooth.so
%{_libdir}/libastal-brightness.so
%{_libdir}/libastal-cava.so
%{_libdir}/libastal-greet.so
%{_libdir}/libastal-hyprland.so
%{_libdir}/libastal-idle-notify.so
%{_libdir}/libastal-mpris.so
%{_libdir}/libastal-network.so
%{_libdir}/libastal-notifd.so
%{_libdir}/libastal-power-profiles.so
%{_libdir}/libastal-river.so
%{_libdir}/libastal-tray.so
%{_libdir}/libastal-wireplumber.so
%{_libdir}/libastal-wl.so
%{_libdir}/libastal-wl4.so
%{_libdir}/libastal-workspace.so
%{_libdir}/libquarrel.so
%{_libdir}/pkgconfig/astal-*.pc
%{_libdir}/pkgconfig/quarrel-0.1.pc

%changelog
* Wed Sep 23 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260923200029gitcbcd9f4-1
- Nightly sync with upstream main branch (Commit: cbcd9f4)
