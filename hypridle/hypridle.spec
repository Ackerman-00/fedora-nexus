%global sdbus_version 2.3.1

Name:           hypridle
Version:        0.1.8
Release:        2%{?dist}
Summary:        Hyprland's idle daemon
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hypridle
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/Kistler-Group/sdbus-cpp/archive/v%{sdbus_version}/sdbus-%{sdbus_version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  cmake(hyprwayland-scanner)
BuildRequires:  pkgconfig(hyprland-protocols)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
%{summary}.

%prep
%autosetup -p1 -a1

%build
pushd sdbus-cpp-%{sdbus_version}
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{_builddir}/sdbus \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF
%cmake_build
cmake --install %{__cmake_builddir}
popd
export PKG_CONFIG_PATH=%{_builddir}/sdbus/lib64/pkgconfig

%cmake
%cmake_build

%install
%cmake_install
rm %{buildroot}%{_datadir}/hypr/hypridle.conf

%files
%license LICENSE
%doc README.md assets/example.conf
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%postun
%systemd_user_postun %{name}.service

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.8-2
- Add missing BuildRequires: pkgconfig(libsystemd) for sd-bus detection

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.8-1
- Initial packaging for Fedora Nexus (Nexus Optimized)