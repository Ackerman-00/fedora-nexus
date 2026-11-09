%global commit          56951426eb9931db3f1c57348f226c2427fba4f3
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261106143557

Name:           xdg-desktop-portal-umbriel-git
Version:        0.1.0^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        XDG Desktop Portal backend for Umbriel

License:        MIT
URL:            https://github.com/noctalia-dev/xdg-desktop-portal-umbriel
Source0:        %{url}/archive/%{commit}/xdg-desktop-portal-umbriel-%{shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc-c++
BuildRequires:  meson >= 1.3
BuildRequires:  ninja-build
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(sdbus-c++) >= 2.0.0
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.39
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(gtk4) >= 4.12
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gio-2.0)
# tests=true links tests/input_capture_client.cpp against libei >= 1.3
BuildRequires:  pkgconfig(libei-1.0) >= 1.3

Requires:       xdg-desktop-portal
Recommends:     slurp

Provides:       xdg-desktop-portal-umbriel = %{version}-%{release}
Conflicts:      xdg-desktop-portal-umbriel

%description
An xdg-desktop-portal backend for the Umbriel compositor, providing
Screencast and Screenshot portal interfaces for portal-based screen capture
and sharing, with a GTK4 share picker.
Compiled specifically for the Nexus repository via automated Git snapshot.

%prep
%autosetup -n xdg-desktop-portal-umbriel-%{commit}


%build
%meson -Db_lto=true -Dpicker=enabled
%meson_build

%install
%meson_install

%check
%meson_test

%files
%license LICENSE
%doc README.md
%{_userunitdir}/xdg-desktop-portal-umbriel.service
%{_libexecdir}/umbriel-share-picker
%{_libexecdir}/xdg-desktop-portal-umbriel
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.umbriel.service
%{_datadir}/xdg-desktop-portal/portals/umbriel.portal
%config(noreplace) %{_datadir}/xdg-desktop-portal/umbriel-portals.conf

%changelog
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0.1.0^20261106143557git5695142-2
- Add explicit pkgconfig(glib-2.0)/pkgconfig(gio-2.0) BuildRequires (gnome.compile_resources and glib-unix.h)
* Fri Nov 06 2026 Ackerman-00 <no-reply> - 0.1.0^20261106143557git5695142-1
- Nightly sync with upstream main branch (Commit: 5695142)
