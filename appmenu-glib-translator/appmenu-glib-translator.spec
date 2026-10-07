# These will be automatically populated by update.sh
%global commit          6de205220732c9fbafb2f1706b3f3e781a532404
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261007083410

%global _vpath_srcdir subprojects/appmenu-glib-translator

Name:           appmenu-glib-translator
Version:        25.04^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        appmenu-glib-translator

License:        LGPL-3.0-or-later
URL:            https://github.com/rilian-la-te/vala-panel-appmenu/blob/master/subprojects/appmenu-glib-translator
Source:         https://github.com/rilian-la-te/vala-panel-appmenu/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  meson >= 0.61.0
BuildRequires:  gcc
BuildRequires:  /usr/bin/vapigen

BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.52.0
BuildRequires:  pkgconfig(gobject-introspection-1.0)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
Development files for %{name}.

%description
%{summary}.

%prep
%autosetup -n vala-panel-appmenu-%{commit} -p1

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_libdir}/girepository-1.0/AppmenuGLibTranslator-25.04.typelib
%{_libdir}/libappmenu-glib-translator.so.0
%{_libdir}/libappmenu-glib-translator.so.25.04

%files devel
%{_datadir}/gir-1.0/AppmenuGLibTranslator-25.04.gir
%{_datadir}/vala/vapi/appmenu-glib-translator.deps
%{_datadir}/vala/vapi/appmenu-glib-translator.vapi
%{_includedir}/appmenu-glib-translator/importer.h
%{_libdir}/libappmenu-glib-translator.so
%{_libdir}/pkgconfig/appmenu-glib-translator.pc

%changelog
* Wed Oct 07 2026 Ackerman-00 <quietcraft@gmail.com> - 25.04^20261007083410git6de2052-1
- Nightly sync with upstream main branch (Commit: 6de2052)
