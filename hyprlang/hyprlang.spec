Name:           hyprlang
Version:        0.6.8
Release:        2%{?dist}
Summary:        The official implementation library for the hypr config language
License:        LGPL-3.0-only
URL:            https://github.com/hyprwm/hyprlang
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprutils)

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Development files for %{name}.

%prep
%autosetup -p1
sed 's/.*/%{version}/' -i VERSION

%build
%cmake
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprlang.so.2
%{_libdir}/libhyprlang.so.%{version}

%files devel
%{_includedir}/hyprlang.hpp
%{_libdir}/libhyprlang.so
%{_libdir}/pkgconfig/hyprlang.pc

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.8-2
- Rebuild against hyprutils 0.14.0 (soname change)

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.8-1
- Initial packaging for Fedora Nexus (Nexus Optimized)