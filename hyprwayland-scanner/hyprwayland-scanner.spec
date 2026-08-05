Name:           hyprwayland-scanner
Version:        0.4.6
Release:        1%{?dist}
Summary:        A Hyprland implementation of wayland-scanner, in and for C++
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwayland-scanner
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  cmake(pugixml)
BuildRequires:  gcc-c++

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}

%description    devel
%{summary}.

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%files devel
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/cmake/%{name}/

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.6-1
- Initial packaging for Fedora Nexus (Nexus Optimized)