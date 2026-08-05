Name:           hyprcursor
Version:        0.1.13
Release:        1%{?dist}
Summary:        The hyprland cursor format, library and utilities
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprcursor
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libzip)
BuildRequires:  pkgconfig(tomlplusplus)

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
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprcursor-util
%{_libdir}/lib%{name}.so.*

%files devel
%{_includedir}/%{name}.hpp
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.13-1
- Initial packaging for Fedora Nexus (Nexus Optimized)