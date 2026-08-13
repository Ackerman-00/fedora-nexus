Name:           hyprutils
Version:        0.14.1
Release:        1%{?dist}
Summary:        Hyprland utilities library used across the ecosystem
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprutils
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(pixman-1)

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Development files for %{name}.

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
%{_libdir}/lib%{name}.so.*

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.14.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)