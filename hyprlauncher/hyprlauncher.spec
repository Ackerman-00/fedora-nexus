Name:           hyprlauncher
Version:        0.1.6
Release:        1%{?dist}
Summary:        A multipurpose and versatile launcher / picker for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprlauncher
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprwire)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libqalculate)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(xkbcommon)

%description
A multipurpose and versatile launcher / picker for Hyprland.

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
%{_bindir}/%{name}

%changelog
* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.6-1
- Initial packaging for Fedora Nexus (Nexus Optimized)
