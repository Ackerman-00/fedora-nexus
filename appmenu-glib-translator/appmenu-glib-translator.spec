%global commit          4b14e30398e33ac339c395272c0993dbb307ed63
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261120061324

%global _vpath_srcdir subprojects/appmenu-glib-translator

Name:           appmenu-glib-translator
Version:        25.04^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        appmenu-glib-translator

License:        LGPL-3.0-or-later
URL:            https://github.com/rilian-la-te/vala-panel-appmenu/blob/master/subprojects/appmenu-glib-translator
Source:         https://github.com/rilian-la-te/vala-panel-appmenu/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
# sha256: c8839377c4f5bdf121aec483a45e6260339af3b0e5ba6ee31caf91e52ca3577c

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
* Fri Nov 20 2026 Ackerman-00 <no-reply> - 25.04^20261120061324git4b14e30-1
- Nightly sync with upstream main branch (Commit: 4b14e30)
