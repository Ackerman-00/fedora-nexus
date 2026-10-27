Name:           mangowm
Version:        0.18.3
Release:        2%{?dist}
Summary:        A modern, lightweight, high-performance Wayland compositor built on dwl
License:        GPL-3.0-or-later AND MIT AND X11 AND CC0-1.0
Packager:       Ackerman-00 <quietcraft@gmail.com>
URL:            https://github.com/mangowm/mango
Source:         %{url}/archive/%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  findutils
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-randr)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.41
BuildRequires:  pkgconfig(wayland-server) >= 1.23.1
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
BuildRequires:  pkgconfig(scenefx-0.5) >= 0.5.0

Requires:       xorg-x11-server-Xwayland
Requires:       vulkan-loader
Requires:       hicolor-icon-theme
Requires(post): gtk-update-icon-cache
Requires(postun): gtk-update-icon-cache
Recommends:     xdg-desktop-portal >= 1.18
Recommends:     xdg-desktop-portal-gtk
Recommends:     xdg-desktop-portal-wlr

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

sed -i "s/'-U_FORTIFY_SOURCE',//g" meson.build

%build
%meson
%meson_build

%install
%meson_install
install -Dpm0644 assets/mango.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/mango.svg

%post
/bin/touch --no-create %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
/usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor >/dev/null 2>&1 || :

%postun
case "$1" in
    0)
        /bin/touch --no-create %{_datadir}/icons/hicolor >/dev/null 2>&1
        /usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor >/dev/null 2>&1 || :
        ;;
esac

%posttrans
/usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor >/dev/null 2>&1 || :

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
%{_datadir}/icons/hicolor/scalable/apps/mango.svg
%config(noreplace) %{_datadir}/xdg-desktop-portal/mango-portals.conf
%{_userunitdir}/mango-session.target

%changelog
* Sun Oct 25 2026 Ackerman-00 <quietcraft@gmail.com> - 0.18.3-2
- Install the mango session icon so Icon=mango resolves
- Recommend xdg-desktop-portal-wlr for the wlr ScreenCast/Screenshot backend

* Sat Oct 24 2026 Ackerman-00 <quietcraft@gmail.com> - 0.18.3-1
- Auto-update to version 0.18.3
