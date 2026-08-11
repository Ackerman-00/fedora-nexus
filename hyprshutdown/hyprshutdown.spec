Name:           hyprshutdown
Version:        0.1.1
Release:        1%{?dist}
Summary:        A graceful shutdown utility for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprshutdown
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  glaze-devel

%description
A graceful shutdown utility for Hyprland.

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
* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.1-1
- Initial packaging for Fedora Nexus (Nexus Optimized)
