%global commit          df91c7577e63c7d5a41c20053700060fff76b729
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260613132640

Name:           app2unit
Version:        1.0.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Launch desktop entries or commands as systemd user units

License:        GPL-3.0-only
URL:            https://github.com/Vladimir-csp/app2unit
Source0:        %{url}/archive/%{commit}.tar.gz

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  scdoc
BuildRequires:  gzip

Requires:       bash
Requires:       systemd

%description
Launch Desktop Entries (or arbitrary commands) as Systemd user units, and do it
fast. Performs a function similar to uwsm's app subcommand, but without the
costly startup of Python interpreter. If run on a fast shell (such as dash) with
system stored on an SSD, overhead can be as short as ~0.03s.

%prep
%autosetup -n app2unit-%{commit}

%build
%make_build

%install
%make_install prefix=%{_prefix}

%files
%license LICENSE
%doc README.md
%{_bindir}/app2unit
%{_bindir}/app2unit-open
%{_bindir}/app2unit-open-scope
%{_bindir}/app2unit-open-service
%{_bindir}/app2unit-term
%{_bindir}/app2unit-term-scope
%{_bindir}/app2unit-term-service
%{_mandir}/man1/app2unit.1*

%changelog
* Wed Jul 08 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.0^20260613132640gitdf91c75-1
- Initial package for Fedora Nexus
