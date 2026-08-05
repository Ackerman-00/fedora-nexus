Name:           hyprland-guiutils
Version:        0.2.2
Release:        2%{?dist}
Summary:        Hyprland GUI utilities
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-guiutils
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(xkbcommon)

Obsoletes:      hyprland-qtutils <= 0.1.5

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprland-dialog
%{_bindir}/hyprland-donate-screen
%{_bindir}/hyprland-run
%{_bindir}/hyprland-update-screen
%{_bindir}/hyprland-welcome

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.2-2
- Rebuild: hyprtoolkit now available in COPR repo

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.2-1
- Initial packaging for Fedora Nexus (Nexus Optimized)