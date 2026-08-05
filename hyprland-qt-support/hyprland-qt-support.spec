Name:           hyprland-qt-support
Version:        0.1.0
Release:        1%{?dist}
Summary:        A Qt6 Qml style provider for hypr* apps
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-qt-support
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Patch:          cmake.patch
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  qt6-rpm-macros
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickControls2)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  pkgconfig(hyprlang)

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake -DINSTALL_QMLDIR=%{_qt6_qmldir}
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprland-quick-style-impl.so
%{_libdir}/libhyprland-quick-style.so
%{_qt6_qmldir}/org/hyprland/

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)