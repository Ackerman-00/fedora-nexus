Name:           hyprpolkitagent
Version:        0.2.0
Release:        2%{?dist}
Summary:        A simple polkit authentication agent for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpolkitagent
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprgraphics)
BuildRequires:  pkgconfig(hyprlang)
# Upstream 0.2.0 needs hyprtoolkit 0.6.0 API (CTextboxElement::setText/
# setPassword, CButtonElement::setEnabled - absent in 0.5.4, proven by
# local compile failure against repo's 0.5.4 + headers present in 0.6.0)
BuildRequires:  pkgconfig(hyprtoolkit) >= 0.6.0
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(sdbus-c++) >= 2
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  systemd-rpm-macros

# Runtime: upstream spawns polkit-agent-helper-1 via findHelperPath()
# (src/core/PolkitListener.cpp candidates incl. /usr/lib/polkit-1/...)
Requires:       polkit

%description
A simple polkit authentication agent for Hyprland, written with hyprtoolkit.

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
%{_datadir}/dbus-1/services/org.hyprland.%{name}.service
%{_libexecdir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
* Wed Sep 09 2026 Nexus Auto-Updater <bot@github.com> - 0.2.0-2
- Upstream 0.2.0 replaced Qt/QML frontend with hyprtoolkit: add BRs
  hyprtoolkit/hyprgraphics/hyprlang/pixman-1/libdrm/sdbus-c++/xkbcommon,
  drop unused Qt6/polkit-qt BRs and hyprland-qt-support Requires,
  Require polkit (agent-helper binary spawned at runtime)

* Wed Sep 09 2026 Nexus Auto-Updater <bot@github.com> - 0.2.0-1
- Update to version 0.2.0

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.3-2
- Rebuild against hyprutils 0.14.0 (soname change)

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.3-1
- Initial packaging for Fedora Nexus (Nexus Optimized)