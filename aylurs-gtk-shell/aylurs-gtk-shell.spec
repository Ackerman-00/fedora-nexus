Name:           aylurs-gtk-shell
Version:        3.1.2
Release:        1%{?dist}
Summary:        A customizable and extensible shell

License:        GPL-3.0-or-later
URL:            https://github.com/Aylur/ags
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://registry.npmjs.org/gnim/-/gnim-1.9.1.tgz

BuildRequires:  gcc
BuildRequires:  golang >= 1.24
BuildRequires:  meson
BuildRequires:  pkgconfig(gjs-1.0)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)
BuildRequires:  tar

Obsoletes:      aylurs-gtk-shell-git < 3.1.2

Requires:       gjs%{?_isa}
Requires:       gtk4-layer-shell%{?_isa}

Provides:       bundled(npm:gnim) = 1.9.1

%description
This program is essentially a library for gjs which allows defining GTK widgets
in a declarative way in JavaScript. It also provides services to interact with
the system so that these widgets can have functionality.

%prep
%autosetup -n ags-%{version} -p1
mkdir -p node_modules/gnim
tar -xzf %{SOURCE1} -C node_modules/gnim --strip=1

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%doc examples/
%{_bindir}/ags
%{_datadir}/ags/

%changelog
* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 3.1.2-1
- Rebase to 3.1.2 (Go CLI, gtk4-layer-shell, bundled gnim)
- Drop gvc subproject and TypeScript build (removed upstream in 3.0)