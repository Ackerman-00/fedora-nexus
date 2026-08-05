Name:           hyprsysteminfo
Version:        0.2.0
Release:        3%{?dist}
Summary:        An application to display information about the running system
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsysteminfo
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickControls2)
BuildRequires:  cmake(Qt6WaylandClient)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  glaze-static
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  wayland-devel
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpci)
BuildRequires:  pkgconfig(pixman-1)

Requires:       /usr/bin/lscpu
Requires:       /usr/bin/lspci
Requires:       /usr/bin/free
Requires:       hyprland-qt-support%{?_isa}

%description
A tiny Qt6/QML application to display information about the running system,
or copy diagnostics data, without the terminal.

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-3
- Rebuild: COPR repo now has hyprtoolkit 0.5.4-2

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-2
- Rebuild: hyprtoolkit now available in COPR repo

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)