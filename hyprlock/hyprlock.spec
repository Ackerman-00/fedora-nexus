%global sdbus_version 2.3.1

Name:           hyprlock
Version:        0.9.6
Release:        2%{?dist}
Summary:        Hyprland's GPU-accelerated screen locking utility
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprlock
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/Kistler-Group/sdbus-cpp/archive/v%{sdbus_version}/sdbus-%{sdbus_version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(hyprwayland-scanner)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprgraphics)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(opengl)
BuildRequires:  pkgconfig(pam)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(xkbcommon)

Provides:       bundled(sdbus-cpp) = %{sdbus_version}

%description
%{summary}.

%prep
%autosetup -p1
mkdir -p subprojects/sdbus-cpp
tar -xf %{SOURCE1} -C subprojects/sdbus-cpp --strip=1

%build
pushd subprojects/sdbus-cpp
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{_builddir}/sdbus \
    -DCMAKE_BUILD_TYPE=Release \
    -DSDBUSCPP_BUILD_DOCS=OFF \
    -DBUILD_SHARED_LIBS=OFF
%cmake_build
cmake --install %{_vpath_builddir}
popd
export PKG_CONFIG_PATH=%{_builddir}/sdbus/%{_lib}/pkgconfig

%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
rm %{buildroot}%{_datadir}/hypr/%{name}.conf

%files
%license LICENSE
%doc README.md assets/example.conf
%{_bindir}/%{name}
%config(noreplace) %{_sysconfdir}/pam.d/%{name}

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.6-2
- Add missing BuildRequires: pkgconfig(libsystemd) for sd-bus detection

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.6-1
- Initial packaging for Fedora Nexus (Nexus Optimized)