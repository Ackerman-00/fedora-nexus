# These will be automatically populated by update.sh
%global commit          86b4275879b32bf58dc89035452313919cd89bd2
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260914015902

Name:           quickshell-git
Version:        0.3.1^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Flexible toolkit for making desktop shells with QtQuick (Git Snapshot)

# Code is LGPL, Hyprland protocols are BSD-3-Clause, wlr protocols are HPND-sell-variant
# (cf. Fedora official quickshell.spec).
License:        LGPL-3.0-or-later and BSD-3-Clause and HPND-sell-variant
URL:            https://github.com/quickshell-mirror/quickshell
Source0:        %{url}/archive/%{commit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  desktop-file-utils
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
Provides:       desktop-notification-daemon
Provides:       PolicyKit-authentication-agent

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
# NOTE: CRASH_HANDLER stays OFF (same intent as Fedora official's breakpad
# bcond): the handler needs breakpad, which is unpackaged in Fedora.
# GIT_REVISION is intentionally not passed: current upstream CMakeLists has
# no such variable (official's flag is from the older tree).

%cmake_build

%install
%cmake_install

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/org.quickshell.desktop

%files
%license LICENSE*
%doc README.md BUILD.md CONTRIBUTING.md HACKING.md changelog/
%{_bindir}/quickshell
%{_bindir}/qs
%{_datadir}/applications/org.quickshell.desktop
%{_datadir}/icons/hicolor/scalable/apps/org.quickshell.svg
%dir %{_libdir}/qt6/qml/Quickshell/
%{_libdir}/qt6/qml/Quickshell/*

%changelog
* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.1^20260914015902git86b4275-2
- Full SPDX License expression; ship LICENSE-GPL and contributor docs via glob
- Validate desktop file in %check; Provide notification-daemon and polkit-auth-agent

* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 0.3.1^20260914015902git86b4275-1
- Nightly sync with upstream master branch (Commit: 86b4275)
