%global commit          fa064d858c277d823b6bd3509a4b0952ba5a7ceb
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261113221544

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
for h in exporter importer; do
  install -d %{buildroot}%{_includedir}/%{name}/$h
  install -pm0644 %{buildroot}%{_includedir}/%{name}/$h.h \
      %{buildroot}%{_includedir}/%{name}/$h/$h.h
done

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%{_libdir}/girepository-1.0/AppmenuGLibTranslator-25.04.typelib
%{_libdir}/libappmenu-glib-translator.so.0
%{_libdir}/libappmenu-glib-translator.so.25.04

%files devel
%{_datadir}/gir-1.0/AppmenuGLibTranslator-25.04.gir
%{_datadir}/vala/vapi/appmenu-glib-translator.deps
%{_datadir}/vala/vapi/appmenu-glib-translator.vapi
%{_includedir}/%{name}/
%{_libdir}/libappmenu-glib-translator.so
%{_libdir}/pkgconfig/appmenu-glib-translator.pc

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 25.04^20261113221544gitfa064d8-2
- Move the in-app updater strip into %install

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 25.04^20261113221544gitfa064d8-1
- Nightly sync with upstream main branch (Commit: fa064d8)
