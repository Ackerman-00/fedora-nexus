Name:           hyprqt6engine
Version:        0.1.0
Release:        3%{?dist}
Summary:        Qt6 Theme Provider for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprqt6engine
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Patch:          fix-build.diff
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  qt6-rpm-macros
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  cmake(KF6ColorScheme)
BuildRequires:  cmake(KF6Config)
BuildRequires:  cmake(KF6IconThemes)
BuildRequires:  cmake(Qt6BuildInternals)
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  qt6-qtbase-private-devel

%description
%{summary}.

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
%{_libdir}/libhyprqt6engine-common.so
%{_qt6_plugindir}/platformthemes/libhyprqt6engine.so
%{_qt6_plugindir}/styles/libhypr-style.so

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0-3
- Rebuild: hyprlang now rebuilt against hyprutils 0.14.0

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0-2
- Rebuild: hyprutils 0.14.0 now available in COPR repo (fixes uintptr_t errors)

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)