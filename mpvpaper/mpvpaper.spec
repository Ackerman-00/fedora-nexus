Name:           mpvpaper
Version:        1.9
Release:        1%{?dist}
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
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 1.9-1
- Initial package
