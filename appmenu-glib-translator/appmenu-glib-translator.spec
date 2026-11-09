%global commit          d475cca380e88b3b62bc8ecde9d861bc5e777c4e
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261102201706

%global _vpath_srcdir subprojects/appmenu-glib-translator

Name:           appmenu-glib-translator
Version:        25.04^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
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
%{_includedir}/appmenu-glib-translator/debug.h
%{_libdir}/libappmenu-glib-translator.so
%{_libdir}/pkgconfig/appmenu-glib-translator.pc

%changelog
* Sat Nov 07 2026 Ackerman-00 <no-reply> - 25.04^20261102201706gitd475cca-2
- Package new upstream debug.h public header (unpackaged file build failure)

* Tue Nov 03 2026 Ackerman-00 <no-reply> - 25.04^20261102201706gitd475cca-1
- Nightly sync with upstream main branch (Commit: d475cca)
