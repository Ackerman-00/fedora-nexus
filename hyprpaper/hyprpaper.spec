Name:           hyprpaper
Version:        0.8.4
Release:        4%{?dist}
Summary:        Blazing fast wayland wallpaper utility with IPC controls
# LICENSE: BSD-3-Clause
# protocols/wlr-layer-shell-unstable-v1.xml: HPND-sell-variant
License:        BSD-3-Clause AND HPND-sell-variant
URL:            https://github.com/hyprwm/hyprpaper
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hyprgraphics)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprwayland-scanner)
BuildRequires:  pkgconfig(hyprwire)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libmagic)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
Hyprpaper is a blazing fast wallpaper utility for Hyprland with the ability
to dynamically change wallpapers through sockets. It will work on all
wlroots-based compositors, though.

%prep
%autosetup -p1

%build
%cmake
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
* Wed Aug 12 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.4-4
- Add explicit BuildRequires pkgconfig(pixman-1): upstream CMakeLists
  requires pixman-1 in its pkg_check_modules

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.4-3
- Rebuild: COPR repo now has hyprtoolkit and hyprwire

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.4-2
- Rebuild: hyprtoolkit and hyprwire now available in COPR repo

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.4-1
- Initial packaging for Fedora Nexus (Nexus Optimized)