%global commit          04aa9870411e367f7dd87c00a23488f549624119
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261126132445

Name:           xdg-desktop-portal-umbriel-git
Version:        0.1.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        XDG Desktop Portal backend for Umbriel

License:        MIT
URL:            https://github.com/noctalia-dev/xdg-desktop-portal-umbriel
Source0:        %{url}/archive/%{commit}/xdg-desktop-portal-umbriel-%{shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc-c++
# dbus-run-session wraps two of the upstream tests
BuildRequires:  dbus-daemon
BuildRequires:  meson >= 1.3
BuildRequires:  ninja-build
BuildRequires:  systemd-rpm-macros
BuildRequires:  stb_image_resize2-devel
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-ft)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(pango) >= 1.50
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pangoft2)
BuildRequires:  pkgconfig(sdbus-c++) >= 2.0.0
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.39
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xkbcommon)
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
%meson -Db_lto=true -Dpicker=true
%meson_build

%install
%meson_install

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true
%check
%meson_test

%files
%license LICENSE
%doc README.md
%{_userunitdir}/xdg-desktop-portal-umbriel.service
%{_libexecdir}/umbriel-share-picker
%{_libexecdir}/xdg-desktop-portal-umbriel
%{_datadir}/xdg-desktop-portal-umbriel/
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.umbriel.service
%{_datadir}/xdg-desktop-portal/portals/umbriel.portal
%config(noreplace) %{_datadir}/xdg-desktop-portal/umbriel-portals.conf

%changelog
* Thu Nov 26 2026 Ackerman-00 <no-reply> - 0.1.0^20261126132445git04aa987-1
- Nightly sync with upstream main branch (Commit: 04aa987)
