# pinned: upstream deleted lang/lua in 9b67eb5
%global live_hold_reason upstream deleted lang/lua in 9b67eb5; held at last good commit
%global commit          7b4d37603c11d2f84338a5da35b1f0676935eb57
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261101003451

%global debug_package %{nil}
%global _vpath_srcdir lang/lua

Name:           astal-lua
Version:        0^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Lua bindings for libastal
BuildArch:      noarch

License:        LGPL-2.1-only
URL:            https://github.com/Aylur/astal
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  lua-devel

Requires:       astal
Requires:       astal-io
Requires:       lua-lgi
%{?lua_requires}

%description
%{summary}.

%prep
%autosetup -n astal-%{commit} -p1

%build

%install
pushd %{_vpath_srcdir}
mkdir -p %{buildroot}%{lua_pkgdir}
cp -pr astal %{buildroot}%{lua_pkgdir}

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%{lua_pkgdir}/astal/

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 0^20261101003451git7b4d376-2
- Move the in-app updater strip into %install

* Sat Nov 07 2026 Ackerman-00 <no-reply> - 0^20261101003451git7b4d376-1
- Pin to 7b4d376: upstream deprecated and deleted the Lua bindings in 9b67eb5; update.sh holds this pin
