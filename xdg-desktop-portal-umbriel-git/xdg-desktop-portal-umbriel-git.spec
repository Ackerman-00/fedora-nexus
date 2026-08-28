# These will be automatically populated by update.sh
%global commit          4edf049e4f9982bd7c3d6c92e25379308fdaa8df
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260828152210

Name:           xdg-desktop-portal-umbriel-git
Version:        0.1.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        XDG Desktop Portal backend for the Umbriel compositor (Nexus Optimized Git Snapshot)

License:        MIT
URL:            https://github.com/noctalia-dev/xdg-desktop-portal-umbriel
Source0:        %{url}/archive/%{commit}/xdg-desktop-portal-umbriel-%{shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc-c++
BuildRequires:  meson >= 1.3
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(sdbus-c++) >= 2.0.0
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.39
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(gtk4)

Requires:       xdg-desktop-portal

Provides:       xdg-desktop-portal-umbriel = %{version}-%{release}
Conflicts:      xdg-desktop-portal-umbriel

%description
An xdg-desktop-portal backend for the Umbriel compositor, providing
Screencast and Screenshot portal interfaces for portal-based screen capture
and sharing, with a GTK4 share picker.
Compiled specifically for the Nexus repository via automated Git snapshot.

%prep
%autosetup -n xdg-desktop-portal-umbriel-%{commit}

# Upstream vendors only the top-level split-style nlohmann json.hpp (3.12.0),
# which includes <nlohmann/detail/*.hpp> files Fedora's json-devel does not
# ship -> fatal error nlohmann/detail/string_utils.hpp not found. Use the
# complete, self-contained system header instead (API-compatible).
sed -i 's|#include "vendor/json.hpp"|#include <nlohmann/json.hpp>|' \
    src/picker/main.cpp src/wayland/wayland.cpp src/dbus/screenshot.cpp src/dbus/screencast.cpp
rm -f src/vendor/json.hpp

%build
%meson -Db_lto=true
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_userunitdir}/xdg-desktop-portal-umbriel.service
%{_libexecdir}/umbriel-share-picker
%{_libexecdir}/xdg-desktop-portal-umbriel
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.umbriel.service
%{_datadir}/xdg-desktop-portal/portals/umbriel.portal
%{_datadir}/xdg-desktop-portal/umbriel-portals.conf

%changelog
* Fri Aug 28 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260828152210git4edf049-1
- Nightly sync with upstream main branch (Commit: 4edf049)
