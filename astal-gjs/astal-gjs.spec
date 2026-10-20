# These will be automatically populated by update.sh
%global commit          cbcd9f49dd6b9638dc5623b56cc6e1e0a60b593e
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260923200029

%global debug_package %{nil}
%global _vpath_srcdir lang/gjs

Name:           astal-gjs
Version:        0^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Astal GJS package

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  meson
BuildRequires:  pkgconfig(astal-io-0.1)
BuildRequires:  pkgconfig(astal-3.0)
# astal-4-4.0 is probed optional upstream but MUST stay pinned - unprobed built the gtk4 bindings against nothing
BuildRequires:  pkgconfig(astal-4-4.0)

Requires:       gjs%{?_isa}
Requires:       astal-io%{?_isa}
Requires:       astal%{?_isa}

Supplements:    astal

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
%dir %{_datadir}/astal
%{_datadir}/astal/gjs/

%files devel
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Fri Oct 02 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260923200029gitcbcd9f4-2
- Pin the silent-optional GTK4 backend on at build time: upstream
  lang/gjs/meson.build probes astal-4-4.0 with required:false but installs
  the gtk4 binding tree unconditionally, so the shipped gtk4 sources were
  built against nothing. Adds BuildRequires: pkgconfig(astal-4-4.0).
* Wed Sep 23 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260923200029gitcbcd9f4-1
- Nightly sync with upstream main branch (Commit: cbcd9f4)
