# These will be automatically populated by update.sh
%global commit          bcd02cbd1391e85f52c5ff63e00708b5b62f55ec
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260823095439

%global debug_package %{nil}
%global _vpath_srcdir lang/lua

Name:           astal-lua
Version:        0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
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

%files
%license LICENSE
%{lua_pkgdir}/astal/

%changelog
* Sun Aug 23 2026 Ackerman-00 <quietcraft@gmail.com> - 0^20260823095439gitbcd02cb-1
- Nightly sync with upstream main branch (Commit: bcd02cb)
