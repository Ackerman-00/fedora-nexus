Name:           mangowm
Version:        0.15.2
Release:        3%{?dist}
Summary:        A modern, lightweight, high-performance Wayland compositor built on dwl
License:        GPL-3.0-or-later AND MIT AND X11 AND CC0-1.0
Packager:       Ackerman-00 <quietcraft@gmail.com>
URL:            https://github.com/mangowm/mango
Source:         %{url}/archive/%{version}.tar.gz
# systemd user session target — enables graphical-session.target for portal services
Source1:        mango-session.target
Source2:        mango-session.service
# environment.d config — makes GSETTINGS_SCHEMA_DIR and GTK_THEME available
Source3:        60-mango.conf
# profile.d script — ensures env vars reach compositor when launched from TTY
Source4:        mango.sh
# wrapper — automatically imports env + starts session target before mango
Source5:        mango-wrapper.sh

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.41
BuildRequires:  pkgconfig(wayland-server) >= 1.23.1
BuildRequires:  pkgconfig(wlroots-0.20)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput) >= 1.27.1
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  pkgconfig(libcjson)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  scenefx-devel

Requires:       xorg-x11-server-Xwayland
Recommends:     xdg-desktop-portal >= 1.18
Recommends:     xdg-desktop-portal-gtk

Conflicts:      mangowc < %{version}
Obsoletes:      mangowc < %{version}
Provides:       mangowc = %{version}
Provides:       wayland-compositor

%description
MangoWM is a modern, lightweight, high-performance Wayland compositor built on
dwl — crafted for speed, flexibility, and a customizable desktop experience.

%prep
%autosetup -n mango-%{version}

%build
%meson
%meson_build

%install
%meson_install

# Rename real mango binary → mango.real (wrapper takes its place)
mv %{buildroot}%{_bindir}/mango %{buildroot}%{_bindir}/mango.real

# Install wrapper that imports env + starts session target before mango
install -Dpm0755 %{SOURCE5} %{buildroot}%{_bindir}/mango

# Install systemd user units (mango-session.target binds to graphical-session.target)
install -Dpm0644 %{SOURCE1} %{buildroot}%{_prefix}/lib/systemd/user/mango-session.target
install -Dpm0644 %{SOURCE2} %{buildroot}%{_prefix}/lib/systemd/user/mango-session.service

# Install environment.d config (GSETTINGS_SCHEMA_DIR + GTK_THEME fallback)
install -Dpm0644 %{SOURCE3} %{buildroot}%{_prefix}/lib/environment.d/60-mango.conf

# Install profile.d script (ensures env vars when mango is launched from TTY)
install -Dpm0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d/mango.sh

%files
%doc README.md
%license LICENSE
%{_bindir}/mango
%{_bindir}/mango.real
%{_bindir}/mmsg
%{_mandir}/man1/mmsg.1*
%{_sysconfdir}/mango/config.conf
%{_datadir}/wayland-sessions/mango.desktop
%{_datadir}/xdg-desktop-portal/mango-portals.conf
%{_prefix}/lib/systemd/user/mango-session.target
%{_prefix}/lib/systemd/user/mango-session.service
%{_prefix}/lib/environment.d/60-mango.conf
%{_sysconfdir}/profile.d/mango.sh

%changelog
* Sun Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.15.2-3
- Recommends xdg-desktop-portal and xdg-desktop-portal-gtk for portal integration
- Add mango-session.target / mango-session.service (systemd user units)
  to activate graphical-session.target, enabling portal services (GTK4 dark mode)
- Add 60-mango.conf (environment.d) to export GSETTINGS_SCHEMA_DIR and
  GTK_THEME=adw-gtk3-dark as fallback for GTK apps when portal is unavailable
- Replace mango binary with wrapper that imports Wayland env into systemd
  and starts mango-session.service automatically (renamed original to mango.real)
* Sun Jul 12 2026 Ackerman-00 <quietcraft@gmail.com> - 0.15.2-1
- Auto-update to version 0.15.2
