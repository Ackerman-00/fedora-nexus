%global uuid com.mattjakeman.ExtensionManager

Name:           extension-manager
Version:        0.7.0
Release:        3%{?dist}
Summary:        A native tool for browsing, installing, and managing GNOME Shell Extensions

License:        GPL-3.0-or-later
Packager:       Ackerman-00 <no-reply>
URL:            https://mattjakeman.com/apps/extension-manager
Source0:        https://github.com/mjakeman/extension-manager/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  blueprint-compiler
BuildRequires:  gettext
BuildRequires:  glib2-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.8
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libxml-2.0)
# glycin: sandboxed image loading, new in 0.7.0
BuildRequires:  pkgconfig(glycin-2)
BuildRequires:  pkgconfig(glycin-gtk4-2)

Requires:           hicolor-icon-theme
Requires:       vulkan-loader

%description
A native tool for browsing, installing, and managing GNOME Shell Extensions.
With Extension Manager you can:
* Browse and search extensions from extensions.gnome.org
* Install and Remove
* Enable and Disable
* Update in-app

%prep
%autosetup

%build
%meson \
    -Dbacktrace=false \
    -Dpackage="Fedora" \
    -Ddistributor="Ackerman-00 <no-reply>"
%meson_build

%install
%meson_install
%find_lang %{name}

%check
%meson_test
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/%{uuid}.metainfo.xml
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{uuid}.desktop

%files -f %{name}.lang
%license COPYING
%doc README.md
%{_bindir}/extension-manager
%{_datadir}/metainfo/%{uuid}.metainfo.xml
%{_datadir}/applications/%{uuid}.desktop
%{_datadir}/glib-2.0/schemas/%{uuid}.gschema.xml
%{_datadir}/dbus-1/services/%{uuid}.service
%{_datadir}/gnome-shell/search-providers/%{uuid}.search-provider.ini
%{_datadir}/icons/hicolor/*/*/*.svg

%changelog
* Sat Nov 07 2026 Ackerman-00 <no-reply> - 0.7.0-3
- Package new GNOME search-provider ini and D-Bus service files (0.7.0 install set)

* Sat Nov 07 2026 Ackerman-00 <no-reply> - 0.7.0-2
- Add glycin-2 and glycin-gtk4-2 BuildRequires (new upstream deps in 0.7.0)

* Fri Nov 06 2026 Ackerman-00 <no-reply> - 0.7.0-1
- Auto-update to version 0.7.0
