# pinned: upstream deleted lang/gjs in 9b67eb5
%global live_hold_reason upstream deleted lang/gjs in 9b67eb5; held at last good commit
%global commit          7b4d37603c11d2f84338a5da35b1f0676935eb57
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261101003451

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

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%dir %{_datadir}/astal
%{_datadir}/astal/gjs/

%files devel
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 0^20261101003451git7b4d376-2
- Move the in-app updater strip into %install

* Sat Nov 07 2026 Ackerman-00 <no-reply> - 0^20261101003451git7b4d376-1
- Pin to 7b4d376: upstream deprecated and deleted the GJS bindings in 9b67eb5; update.sh holds this pin
