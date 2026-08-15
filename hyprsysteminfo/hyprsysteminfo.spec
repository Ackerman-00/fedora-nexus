Name:           hyprsysteminfo
Version:        0.2.0
Release:        5%{?dist}
Summary:        An application to display information about the running system
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsysteminfo
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  glaze-static
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpci)
BuildRequires:  pkgconfig(pixman-1)

%description
A tiny hyprtoolkit/Wayland application to display information about the running
system, or copy diagnostics data, without the terminal.

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
* Sat Aug 15 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-5
- Rebuild: restore fc44 build that failed during the mass rebuild because
  hyprtoolkit-devel was missing from the COPR repo; hyprtoolkit 0.5.4-3 is
  now published

* Wed Aug 12 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-4
- Drop stale Qt6/QML BuildRequires and lscpu/lspci/free/hyprland-qt-support
  Requires: upstream v0.2.0 is a hyprtoolkit-based rewrite that reads
  /proc and /sys and uses libpci directly (no Qt, no shelled-out tools)

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-3
- Rebuild: COPR repo now has hyprtoolkit 0.5.4-2

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-2
- Rebuild: hyprtoolkit now available in COPR repo

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)