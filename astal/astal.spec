# These will be automatically populated by update.sh
%global commit          82f3964d19e39904e32807d3e452a2e19b0493ef
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260830120747

%global _vpath_srcdir lib/astal/gtk3

Name:           astal
Version:        0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Building blocks for creating custom desktop shells

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  pkgconfig(astal-io-0.1)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gtk-layer-shell-0)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
Development files for %{name}.

%description
%{summary}.

%prep
%autosetup -n %{name}-%{commit} -p1

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_libdir}/girepository-1.0/Astal-3.0.typelib
%{_libdir}/libastal.so.3{,.*}

%files devel
%{_datadir}/gir-1.0/Astal-3.0.gir
%{_datadir}/vala/vapi/astal-3.0.vapi
%{_includedir}/astal.h
%{_libdir}/libastal.so
%{_libdir}/pkgconfig/astal-3.0.pc

%changelog
* Sun Aug 30 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260830120747git82f3964-1
- Nightly sync with upstream main branch (Commit: 82f3964)
