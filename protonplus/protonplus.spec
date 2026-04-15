%global tag         v0.5.19
%global app_id      com.vysp3r.ProtonPlus
%global forgeurl    https://github.com/vysp3r/ProtonPlus
%forgemeta
%undefine distprefix

Name:           protonplus
Version:        %{fileref}
Release:        %autorelease
Summary:        A modern compatibility tools manager
ExclusiveArch:  x86_64

License:        GPL-3.0-or-later
URL:            https://protonplus.vysp3r.com
Source0:        %{forgesource}

BuildRequires:  gettext
BuildRequires:  meson >= 1.0.0
BuildRequires:  vala
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.6
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libsoup-3.0)

Requires:       hicolor-icon-theme

%description
ProtonPlus is a modern compatibility tools manager for Linux. It allows you to easily manage and update various compatibility tools like Proton, Wine, DXVK, and VKD3D across different launchers.

%prep
%forgeautosetup

%build
%meson
%meson_build

%install
%meson_install
%find_lang %{app_id}

%check
%meson_test

%files -f %{app_id}.lang
%license LICENSE.md
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/glib-2.0/schemas/%{app_id}.gschema.xml
%{_datadir}/icons/hicolor/*/apps/%{app_id}.png
%{_metainfodir}/%{app_id}.metainfo.xml

%changelog
%autochangelog
