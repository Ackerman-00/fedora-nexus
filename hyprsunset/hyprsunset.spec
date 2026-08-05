Name:           hyprsunset
Version:        0.4.0
Release:        2%{?dist}
Summary:        An application to enable a blue-light filter on Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsunset
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(hyprland-protocols)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprwayland-scanner)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.0-2
- Rebuild against hyprutils 0.14.0 (soname change)

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)