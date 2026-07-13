Name:           mangowm
Version:        0.15.2
Release:        6%{?dist}
Summary:        A modern, lightweight, high-performance Wayland compositor built on dwl
License:        GPL-3.0-or-later AND MIT AND X11 AND CC0-1.0
Packager:       Ackerman-00 <quietcraft@gmail.com>
URL:            https://github.com/mangowm/mango
Source:         %{url}/archive/%{version}.tar.gz

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

%files
%doc README.md
%license LICENSE
%{_bindir}/mango
%{_bindir}/mmsg
%{_mandir}/man1/mmsg.1*
%{_sysconfdir}/mango/config.conf
%{_datadir}/wayland-sessions/mango.desktop
%{_datadir}/xdg-desktop-portal/mango-portals.conf

%changelog
* Mon Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.15.2-6
- Strip back to upstream-clean packaging: remove wrapper/rename, systemd
  session units, environment.d, and profile.d. Mango sets XDG_CURRENT_DESKTOP
  and imports env to systemd/dbus internally via set_activation_env().
  Select "Mango" from DM or run `mango` from TTY — no wrapper needed.
* Mon Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.15.2-5
- Fix wrapper: exec -a mango so argv[0] is "mango" instead of "mango.real"
  (fixes fastfetch WM detection showing mango.real)
- Fix wrapper: export XDG_CURRENT_DESKTOP=mango and XDG_SESSION_TYPE=wayland
  before exec; mango already sets these internally but having them early
  prevents any window of missing env for systemd/portal activation
- Fix session service: remove redundant ExecStartPre that set
  XDG_CURRENT_DESKTOP — mango's built-in set_activation_env() already
  runs dbus-update-activation-environment + systemctl --user import-environment
  for XDG_CURRENT_DESKTOP and other vars (matches upstream docs: "Mango now
  handles this automatically")
* Mon Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.15.2-4
- Fix wrapper: unset stale WAYLAND_DISPLAY/DISPLAY from TTY env before exec
  (prevents wlroots from selecting Wayland backend and crashing)
- Fix session service: import only XDG_CURRENT_DESKTOP, not stale display vars
- Fix env.conf: remove WAYLAND_DISPLAY — wlroots sets it automatically;
  setting it before wlroots init caused backend selection failure
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
