# These will be automatically populated by update.sh
%global commit          f05d28d805a22a7564895aa178772361c44b6b7a
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20250421100807

%global _vpath_srcdir subprojects/appmenu-glib-translator

Name:           appmenu-glib-translator
Version:        25.04^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        appmenu-glib-translator

License:        LGPL-3.0-or-later
URL:            https://github.com/rilian-la-te/vala-panel-appmenu/blob/master/subprojects/appmenu-glib-translator
Source:         https://github.com/rilian-la-te/vala-panel-appmenu/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  /usr/bin/vapigen

BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
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
%{_includedir}/appmenu-glib-translator/appmenu-glib-translator.h
%{_libdir}/libappmenu-glib-translator.so
%{_libdir}/pkgconfig/appmenu-glib-translator.pc

%changelog
* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 25.04^20250421100807gitf05d28d-1
- Initial package