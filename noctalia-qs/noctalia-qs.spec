%global tag         v0.0.12
%global forgeurl    https://github.com/noctalia-dev/noctalia-qs
%forgemeta

Name:           noctalia-qs
Version:        %{fileref}
Release:        %autorelease
Summary:        Flexible QtQuick based desktop shell toolkit (Nexus Optimized)

License:        LGPL-3.0-only AND GPL-3.0-only
URL:            %{forgeurl}
Source0:        %{forgesource}

BuildRequires:  cmake
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6ShaderTools)
BuildRequires:  cmake(Qt6WaylandClient)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  kf6-qqc2-desktop-style
BuildRequires:  spirv-tools
BuildRequires:  vulkan-headers
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(jemalloc)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(pam)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(CLI11)
BuildRequires:  glib2-devel
BuildRequires:  polkit-devel

Conflicts:      quickshell
Provides:       quickshell = %{version}-%{release}
Provides:       desktop-notification-daemon
Provides:       PolicyKit-authentication-agent

%description
Custom high-performance Quickshell fork for Noctalia Shell.
Compiled specifically for the Nexus repository with jemalloc enabled and crash reporting stripped out for maximum performance.

%prep
%forgeautosetup -p1

%build
%cmake -GNinja \
    -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DDISTRIBUTOR="Fedora Nexus" \
    -DINSTALL_QML_PREFIX=%{_lib}/qt6/qml \
    -DUSE_JEMALLOC=ON \
    -DCRASH_REPORTER=OFF \
    -DNO_PCH=ON \
    -DWAYLAND=ON \
    -DWAYLAND_WLR_LAYERSHELL=ON \
    -DSCREENCOPY=ON \
    -DSERVICE_PIPEWIRE=ON \
    -DSERVICE_PAM=ON \
    -DSERVICE_POLKIT=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE LICENSE-GPL
%doc README.md
%{_bindir}/qs
%{_bindir}/quickshell
%{_datadir}/applications/dev.noctalia.noctalia-qs.desktop
%{_datadir}/icons/hicolor/scalable/apps/dev.noctalia.noctalia-qs.svg
%{_libdir}/qt6/qml/Quickshell

%changelog
%autochangelog
