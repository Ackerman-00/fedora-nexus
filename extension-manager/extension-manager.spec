%global uuid com.mattjakeman.ExtensionManager

Name:           extension-manager
Version:        0.6.4
Release:        1%{?dist}
Summary:        A native tool for browsing, installing, and managing GNOME Shell Extensions

License:        GPL-3.0-or-later
Packager:       Ackerman-00 <quietcraft@gmail.com>
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
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libxml-2.0)

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
    -Ddistributor="Ackerman-00 <quietcraft@gmail.com>"
%meson_build

%install
%meson_install
%find_lang %{name}

%check
# Run the internal test suite just like Arch does
%meson_test
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/%{uuid}.metainfo.xml
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{uuid}.desktop

%files -f %{name}.lang
%license COPYING
%doc README.md
%{_bindir}/extension-manager
%{_datadir}/extension-manager/
%{_datadir}/metainfo/%{uuid}.metainfo.xml
%{_datadir}/applications/%{uuid}.desktop
%{_datadir}/glib-2.0/schemas/%{uuid}.gschema.xml
%{_datadir}/icons/hicolor/*/*/*.svg

%changelog
* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.5-1
- Added glib2, gobject-introspection, and libxml2 dependencies
- Injected custom distributor Meson flags
- Enabled meson test suite in check phase
