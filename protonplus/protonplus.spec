%global tag         v0.6.9
%global app_id      com.vysp3r.ProtonPlus
%global forgeurl    https://github.com/vysp3r/ProtonPlus
%forgemeta
%undefine distprefix

Name:           protonplus
Version:        %{fileref}
Release:        2%{?dist}
Summary:        A modern compatibility tools manager
ExclusiveArch:  x86_64

License:        GPL-3.0-or-later
URL:            https://protonplus.vysp3r.com
Source0:        %{forgesource}

BuildRequires:  dbus-daemon
BuildRequires:  dejavu-sans-fonts
BuildRequires:  gettext
BuildRequires:  glibc-langpack-en
BuildRequires:  meson >= 1.0.0
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  desktop-file-utils
BuildRequires:  xorg-x11-server-Xvfb
BuildRequires:  xorg-x11-xauth
BuildRequires:  pkgconfig(appstream)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4) >= 4.14
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.6
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(sdl3) >= 3.2.0
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(yaml-0.1)

Requires:       ca-certificates
Requires:       dconf
Requires:       glib-networking
Requires:       hicolor-icon-theme

%description
ProtonPlus is a modern compatibility tools manager for Linux.
It allows you to easily manage and update various compatibility tools
like Proton, Wine, DXVK, and VKD3D across different launchers.

%prep
%forgeautosetup

%build
%meson
%meson_build

%install
%meson_install
%find_lang %{app_id}

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true
%check
dbus-run-session -- %{__meson} test -C %{_vpath_builddir} --print-errorlogs
desktop-file-validate %{buildroot}%{_datadir}/applications/%{app_id}.desktop

%files -f %{app_id}.lang
%license LICENSE.md
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/glib-2.0/schemas/%{app_id}.gschema.xml
%{_datadir}/icons/hicolor/*/apps/%{app_id}.png
%{_metainfodir}/%{app_id}.metainfo.xml

%changelog
* Thu Nov 26 2026 Ackerman-00 <no-reply> - 0.6.9-2
- Add yaml and sqlite BuildRequires, match upstream Fedora check deps
- Add ca-certificates, dconf and glib-networking runtime requires

* Thu Nov 26 2026 Ackerman-00 <no-reply> - 0.6.9-1
- Update to version 0.6.9
