# These will be automatically populated by update.sh
%global commit          1a4716cde794a59928d9d9fc15f2afc7a95de360
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260820110829

Name:           quickshell-git
Version:        0.3.1^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Flexible toolkit for making desktop shells with QtQuick (Git Snapshot)

License:        LGPL-3.0-only
URL:            https://github.com/quickshell-mirror/quickshell
Source0:        %{url}/archive/%{commit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  cli11-devel
BuildRequires:  pkgconf-pkg-config
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  qt6-qtshadertools-devel
BuildRequires:  libglvnd-devel
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libxcb-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libgbm-devel
BuildRequires:  libdrm-devel
BuildRequires:  pam-devel
BuildRequires:  polkit-devel
BuildRequires:  pipewire-devel
BuildRequires:  jemalloc-devel
BuildRequires:  hicolor-icon-theme
BuildRequires:  spirv-tools
BuildRequires:  vulkan-headers

Requires:       hicolor-icon-theme
Requires:       qt6-qtbase
Requires:       qt6-qtdeclarative
Requires:       qt6-qtsvg
Requires:       qt6-qtwayland
Requires:       jemalloc
Requires:       polkit

Provides:       quickshell = %{version}-%{release}
Conflicts:      quickshell

%description
Quickshell is a flexible toolkit for making desktop shells with QtQuick.
This package tracks the bleeding-edge master branch.

%prep
%autosetup -n quickshell-%{commit}

%build
export CFLAGS="%{optflags} -ffat-lto-objects"
export CXXFLAGS="%{optflags} -ffat-lto-objects"

%cmake -G Ninja \
    -D DISTRIBUTOR='Fedora' \
    -D CRASH_HANDLER=OFF \
    -D CMAKE_BUILD_TYPE=RelWithDebInfo \
    -D INSTALL_QML_PREFIX=%{_lib}/qt6/qml

%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/quickshell
%{_bindir}/qs
%{_datadir}/applications/org.quickshell.desktop
%{_datadir}/icons/hicolor/scalable/apps/org.quickshell.svg
%dir %{_libdir}/qt6/qml/Quickshell/
%{_libdir}/qt6/qml/Quickshell/*

%changelog
* Fri Aug 21 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.1^20260820110829git1a4716c-1
- Nightly sync with upstream master branch (Commit: 1a4716c)
