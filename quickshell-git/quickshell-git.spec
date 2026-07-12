# These will be automatically populated by update.sh
%global commit          4df562dfb2475a9057f0f33a8db75808efad8670
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260710015838

Name:           quickshell-git
Version:        0.3.0^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Flexible toolkit for making desktop shells with QtQuick (Git Snapshot)

License:        LGPL-3.0-only
URL:            https://git.outfoxxed.me/quickshell/quickshell
Source0:        %{url}/archive/%{commit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  cli11-devel
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
%autosetup -n quickshell

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
* Sun Jul 12 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.0^20260710015838git4df562d-2
- Add BuildRequires: qt6-qtbase-private-devel for Qt6CorePrivate/Qt6QuickPrivate
- Fix INSTALL_QML_PREFIX double-slash by using %%{_lib} instead of %%{_libdir}

* Sun Jul 12 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.0^20260710015838git4df562d-1
- Initial quickshell-git package tracking master branch
