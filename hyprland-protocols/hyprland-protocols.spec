Name:           hyprland-protocols
Version:        0.7.0
Release:        1%{?dist}
Summary:        Wayland protocol extensions for Hyprland
BuildArch:      noarch
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-protocols
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  meson

%description
%{summary}.

%package        devel
Summary:        Wayland protocol extensions for Hyprland

%description    devel
%{summary}.

%prep
%autosetup -p1

%build
%meson
%meson_build

%install
%meson_install

%files devel
%license LICENSE
%doc README.md
%{_datadir}/pkgconfig/%{name}.pc
%{_datadir}/%{name}/

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)