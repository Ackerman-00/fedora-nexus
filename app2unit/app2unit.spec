%global commit          47e23ec6ab9e97bbe335c32fb640744a29bf32f7
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260801195144

Name:           app2unit
Version:        1.4.4^%{gitdate}git%{shortcommit}
Release:        3%{?dist}
Summary:        Launch desktop entries or commands as systemd user units

License:        GPL-3.0-only
URL:            https://github.com/Vladimir-csp/app2unit
Source0:        %{url}/archive/%{commit}.tar.gz

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  scdoc
BuildRequires:  gzip

Requires:       systemd
Requires:       xdg-terminal-exec
Requires:       xdg-utils

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

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

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
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 1.4.4^20260801195144git47e23ec-3
- Move the in-app updater strip into %install

* Wed Nov 11 2026 Ackerman-00 <no-reply> - 1.4.4^20260801195144git47e23ec-2
- Declare the runtime tools the shipped script calls: xdg-terminal-exec is the
  -T handler and the command exits 1 without it (app2unit:1491), xdg-utils
  provides xdg-mime for -O/--open (app2unit:1506,1524). Drop Requires bash:
  every shipped script is #!/bin/sh with no bashism.
* Sat Aug 01 2026 Ackerman-00 <no-reply> - 1.4.4^20260801195144git47e23ec-1
- Nightly sync with upstream master branch (Commit: 47e23ec)
