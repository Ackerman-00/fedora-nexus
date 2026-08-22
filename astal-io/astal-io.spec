# These will be automatically populated by update.sh
%global commit          0876946fcea17c54626cc0119e9c54e378ea524f
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260822101925

%global _vpath_srcdir lib/astal/io

Name:           astal-io
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
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)

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
%{_bindir}/astal
%{_libdir}/girepository-1.0/AstalIO-0.1.typelib
%{_libdir}/libastal-io.so.0{,.*}

%files devel
%{_datadir}/gir-1.0/AstalIO-0.1.gir
%{_datadir}/vala/vapi/astal-io-0.1.vapi
%{_includedir}/astal-io.h
%{_libdir}/libastal-io.so
%{_libdir}/pkgconfig/astal-io-0.1.pc

%changelog
* Sat Aug 22 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260822101925git0876946-1
- Nightly sync with upstream main branch (Commit: 0876946)
