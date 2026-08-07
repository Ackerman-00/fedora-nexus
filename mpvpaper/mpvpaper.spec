Name:           mpvpaper
Version:        1.9
Release:        2%{?dist}
Summary:        A video wallpaper program for wlroots based Wayland compositors

License:        GPL-3.0-only AND MIT
URL:            https://github.com/GhostNaN/mpvpaper
Source0:        %{url}/archive/%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(mpv)

# mpvpaper shells out to `pidof` (src/main.c check_watch_list and
# check_paper_processes) to detect programs on the pause/stop watch lists and
# other running wallpaper daemons
Requires:       procps-ng

%description
mpvpaper is a video wallpaper program for wlroots based Wayland compositors.
It renders the video to a shared memory buffer, making it extremely efficient
with minimal CPU usage.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install
install -Dpm 0644 mpvpaper.man %{buildroot}%{_mandir}/man1/mpvpaper.1

%files
%{_bindir}/mpvpaper
%{_bindir}/mpvpaper-holder
%{_mandir}/man1/mpvpaper.1*

%changelog
* Fri Aug 07 2026 Ackerman-00 <quietcraft@gmail.com> - 1.9-2
- Add Requires: procps-ng. mpvpaper calls `pidof` via system() in
  check_watch_list (src/main.c:317) and check_paper_processes
  (src/main.c:1368) to implement --pause-list/--stop-list and to warn about
  other running wallpaper daemons. pidof is not part of a minimal Fedora
  install, so every check printed "sh: line 1: pidof: command not found"
  and the watch lists silently never matched

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 1.9-1
- Initial package
