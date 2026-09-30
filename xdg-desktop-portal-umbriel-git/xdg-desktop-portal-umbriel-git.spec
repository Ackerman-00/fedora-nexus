# These will be automatically populated by update.sh
%global commit          d6bd72cabd83e3084fb2f2e24898d8ffa4a8c24f
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260926215005

Name:           xdg-desktop-portal-umbriel-git
Version:        0.1.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
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
# Protocol codegen uses meson find_program('wayland-scanner'), not
# dependency() - still needs an explicit BR, it never self-declares.
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(gtk4) >= 4.12

Requires:       xdg-desktop-portal
# Upstream README [screenshot] color_pick_cmd: external color picker
# (AUR optdepends slurp). Weak dep: portal works without it.
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

# NOTE (2026-09-14): upstream dropped the vendored split-style json.hpp and
# uses the system <nlohmann/json.hpp> in all sources since d7a1bc3, so no
# header rewrite is needed. If upstream ever re-vendors, re-add the rewrite.

%build
# -Dpicker=enabled states the release intent explicitly (meson_options.txt;
# picker=auto already resolves on while the gtk4 BR is present, same as AUR).
%meson -Db_lto=true -Dpicker=enabled
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
%config(noreplace) %{_datadir}/xdg-desktop-portal/umbriel-portals.conf

%changelog
* Sun Sep 27 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260926215005gitd6bd72c-1
- Nightly sync with upstream main branch (Commit: d6bd72c)
