# These will be automatically populated by update.sh
%global commit          ee380d66984a45310ef48a283ad806ebab752788
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260924131601

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
%config(noreplace) %{_datadir}/xdg-desktop-portal/umbriel-portals.conf

%changelog
* Fri Sep 25 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260924131601gitee380d6-2
- Shorten Summary to fix rpmlint summary-too-long
* Thu Sep 24 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260924131601gitee380d6-1
- Nightly sync with upstream main branch (Commit: ee380d6)
