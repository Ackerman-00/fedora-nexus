Name:           mangowm
Version:        0.18.2
Release:        2%{?dist}
Summary:        A modern, lightweight, high-performance Wayland compositor built on dwl
License:        GPL-3.0-or-later AND MIT AND X11 AND CC0-1.0
Packager:       Ackerman-00 <quietcraft@gmail.com>
URL:            https://github.com/mangowm/mango
Source:         %{url}/archive/%{version}.tar.gz

BuildRequires:  meson
# meson.build:104 requires find_program('find') unconditionally.
BuildRequires:  findutils
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)
# xwayland on by default; xcb-randr needs a BR.
BuildRequires:  pkgconfig(xcb-randr)
# Staging XMLs need a recent wayland-protocols.
BuildRequires:  pkgconfig(wayland-protocols) >= 1.41
BuildRequires:  pkgconfig(wayland-server) >= 1.23.1
# Codegen uses find_program; needs explicit wayland-scanner BR.
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput) >= 1.27.1
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  pkgconfig(libcjson)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libdrm)
# scenefx floor must use pkgconfig() form (NVR 0.5-2).
BuildRequires:  pkgconfig(scenefx-0.5) >= 0.5.0

Requires:       xorg-x11-server-Xwayland
Requires:       vulkan-loader
Recommends:     xdg-desktop-portal >= 1.18
Recommends:     xdg-desktop-portal-gtk

%global mangowc_ver 0.12.5-1

Conflicts:      mangowc < %{mangowc_ver}
Obsoletes:      mangowc < %{mangowc_ver}
Provides:       mangowc = %{mangowc_ver}
Provides:       wayland-compositor

%description
MangoWM is a modern, lightweight, high-performance Wayland compositor built on
dwl — crafted for speed, flexibility, and a customizable desktop experience.

%prep
%autosetup -n mango-%{version}

# Strip -U_FORTIFY_SOURCE so Fedora hardening applies.
sed -i "s/'-U_FORTIFY_SOURCE',//g" meson.build

%build
%meson
%meson_build

%install
%meson_install

%files
%doc README.md
%license LICENSE
%{_bindir}/mango
%{_bindir}/mmsg
%{_bindir}/mangonag
%{_mandir}/man1/mmsg.1*
%{_mandir}/man1/mangonag.1*
%config(noreplace) %{_sysconfdir}/mango/config.conf
%config(noreplace) %{_sysconfdir}/mango/config.toml
%{_datadir}/wayland-sessions/mango.desktop
%config(noreplace) %{_datadir}/xdg-desktop-portal/mango-portals.conf
# Mango activates it itself; see set_activation_env() in src/main.c
%{_userunitdir}/mango-session.target

%changelog
* Wed Oct 21 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.18.2-2
- BuildRequires findutils: meson.build:104 calls find_program('find')
  without required:false and uses it to enumerate src/*.c, so the build
  tool was only ever present because the buildroot happens to carry it.

* Sun Oct 18 2026 Ackerman-00 <quietcraft@gmail.com> - 0.18.2-1
- Auto-update to version 0.18.2
