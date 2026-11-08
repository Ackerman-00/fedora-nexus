%global commit          de0ddf0ce09e68e84f5b989d736f9d9f522ee8f5
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261108094636

%bcond bootstrap 0

%global _vpath_srcdir lib/astal/gtk4

Name:           astal-gtk4
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
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)

%if %{without bootstrap}
Requires:       astal-libs%{?_isa}
%endif

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
Development files for %{name}.

%description
%{summary}.

%prep
%autosetup -n astal-%{commit} -p1

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_libdir}/girepository-1.0/Astal-4.0.typelib
%{_libdir}/libastal-4.so.4{,.*}

%files devel
%{_datadir}/gir-1.0/Astal-4.0.gir
%{_datadir}/vala/vapi/astal-4-4.0.vapi
%{_includedir}/astal-4.h
%{_libdir}/libastal-4.so
%{_libdir}/pkgconfig/astal-4-4.0.pc

%changelog
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261108094636gitde0ddf0-1
- Nightly sync with upstream main branch (Commit: de0ddf0)
