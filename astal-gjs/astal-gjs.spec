%global commit          ab2ab64f79c571bb5fef5c03bdb4d8afe642e758
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261106224639

%global debug_package %{nil}
%global _vpath_srcdir lang/gjs

Name:           astal-gjs
Version:        0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Astal GJS package

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  meson
BuildRequires:  pkgconfig(astal-io-0.1)
BuildRequires:  pkgconfig(astal-3.0)
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
* Sat Nov 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20261106224639gitab2ab64-1
- Nightly sync with upstream main branch (Commit: ab2ab64)
