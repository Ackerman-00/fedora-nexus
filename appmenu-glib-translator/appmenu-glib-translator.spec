%global commit          e7714c5419158f608cef8abbd68d4b2c717b4fe3
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261123082535

%global _vpath_srcdir subprojects/appmenu-glib-translator

Name:           appmenu-glib-translator
Version:        25.04^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        appmenu-glib-translator

License:        LGPL-3.0-or-later
URL:            https://github.com/rilian-la-te/vala-panel-appmenu/blob/master/subprojects/appmenu-glib-translator
Source:         https://github.com/rilian-la-te/vala-panel-appmenu/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
# sha256: 479a99afdd5ee8249bca026e22f316e09da8946727759a1d238304c781ccf106

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
# item.h uses uint16_t/uint32_t without stdint.h; F43 glib no longer pulls it in
sed -i 's|^#include <stdbool.h>|#include <stdbool.h>\n#include <stdint.h>|' subprojects/appmenu-glib-translator/importer/item.h
grep -q '^#include <stdint.h>' subprojects/appmenu-glib-translator/importer/item.h

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
* Mon Nov 23 2026 Ackerman-00 <no-reply> - 25.04^20261123082535gite7714c5-1
- Nightly sync with upstream main branch (Commit: e7714c5)
