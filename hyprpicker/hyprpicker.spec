Name:           hyprpicker
Version:        0.4.7
Release:        2%{?dist}
Summary:        A wlroots-compatible Wayland color picker
# LICENSE: BSD-3-Clause
# protocols/wlr-layer-shell-unstable-v1.xml: HPND-sell-variant
License:        BSD-3-Clause AND HPND-sell-variant
URL:            https://github.com/hyprwm/hyprpicker
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprwayland-scanner)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

Recommends:     wl-clipboard

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_MANDIR=%{_mandir}
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.*

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.7-2
- Rebuild against hyprutils 0.14.0 (soname change)

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.4.7-1
- Initial packaging for Fedora Nexus (Nexus Optimized)