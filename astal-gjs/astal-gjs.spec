# These will be automatically populated by update.sh
%global commit          35d4bc75a3a672b2fcfa43da62bc0cbddd54b41f
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260922142044

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
* Tue Sep 22 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260922142044git35d4bc7-1
- Nightly sync with upstream main branch (Commit: 35d4bc7)
