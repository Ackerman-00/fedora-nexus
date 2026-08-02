%global goipath         github.com/nwg-piotr/nwg-look

Version:        1.1.1

%gometa

Name:           nwg-look
Release:        2%{?dist}
Summary:        GTK3 settings editor adapted to work in the wlroots environment (Nexus Optimized)

License:        MIT

URL:            https://github.com/nwg-piotr/nwg-look
Source0:        %{gosource}

BuildRequires:  golang
BuildRequires:  make
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gdk-3.0)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-gobject)

# Pure Wayland requirements
Requires:       gtk3
Requires:       glib2

%description
nwg-look is a GTK3 settings editor, designed to work properly in wlroots-based Wayland environments.
Packaged specifically for the Nexus repository. Compiled natively using optimized Go macros for peak Wayland performance.

%prep
%goprep
%autopatch -p1

%build
# Build the native Go binary
make build

%install

%make_install

%files
%license LICENSE
%doc README.md
%{_bindir}/nwg-look
%{_datadir}/applications/nwg-look.desktop
%{_datadir}/nwg-look/
%{_datadir}/pixmaps/nwg-look.svg

%changelog
* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1.1-2
- Drop dead Recommends on xcur2png, which is not packaged in Fedora

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 1.1.1-1
- Update to version 1.1.1

* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 1.0.6-1
- Initial Optimized Native Go Build
