%global commit          b7aaf4ce69ebb3c5b1818d524e04b23bc755a97d
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261108102027

%bcond bootstrap 0

%global _vpath_srcdir lib/astal/gtk4

Name:           astal-gtk4
Version:        0^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
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

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

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
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 0^20261108102027gitb7aaf4c-2
- Move the in-app updater strip into %install

* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0^20261108102027gitb7aaf4c-1
- Nightly sync with upstream main branch (Commit: b7aaf4c)
