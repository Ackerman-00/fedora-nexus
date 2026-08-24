# These will be automatically populated by update.sh
%global commit          c8a9a223d48e6c62652f3f3cfaaa0f50aca39146
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260824081238

Name:           xdg-desktop-portal-umbriel-git
Version:        0.1.0^%{gitdate}git%{shortcommit}
# bumped to 2: compile fix (system nlohmann-json instead of broken vendor header),
# same upstream commit c8a9a22 -> keep Version, increment Release
Release:        2%{?dist}
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
* Mon Aug 24 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260824081238gitc8a9a22-2
- Fix build: replace broken vendored nlohmann json.hpp with system header
  (upstream vendor copy needs nlohmann/detail/string_utils.hpp, absent from
  Fedora's json-devel)

* Mon Aug 24 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260824081238gitc8a9a22-1
- Nightly sync with upstream main branch (Commit: c8a9a22)
