%global commit          7e73857b8069533d51408503138a17316e40e143
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261119101510

%global _vpath_srcdir subprojects/appmenu-glib-translator

Name:           appmenu-glib-translator
Version:        25.04^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        appmenu-glib-translator

License:        LGPL-3.0-or-later
URL:            https://github.com/rilian-la-te/vala-panel-appmenu/blob/master/subprojects/appmenu-glib-translator
Source:         https://github.com/rilian-la-te/vala-panel-appmenu/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
# sha256: 7676ed0877f37b972e3f8f0c62e939f3e0b6e184949f02d1233ef40cfa04a288

BuildRequires:  meson >= 1.3.0
BuildRequires:  gcc
BuildRequires:  /usr/bin/vapigen

BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.56.0
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
%{_libdir}/girepository-1.0/AppmenuGLibTranslator-*.typelib
%{_libdir}/libappmenu-glib-translator.so.*

%files devel
%{_datadir}/gir-1.0/AppmenuGLibTranslator-*.gir
%{_datadir}/vala/vapi/appmenu-glib-translator.deps
%{_datadir}/vala/vapi/appmenu-glib-translator.vapi
%{_includedir}/%{name}/
%{_libdir}/libappmenu-glib-translator.so
%{_libdir}/pkgconfig/appmenu-glib-translator.pc

%changelog
* Thu Nov 19 2026 Ackerman-00 <no-reply> - 25.04^20261119101510git7e73857-1
- Nightly sync with upstream main branch (Commit: 7e73857)
