Name:           waypaper
Version:        2.8
Release:        1%{?dist}
Summary:        GUI wallpaper manager for Wayland and Xorg Linux systems

License:        GPL-3.0-only
URL:            https://github.com/anufrievroman/waypaper
Source0:        %{url}/archive/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  gzip

Requires:       python3-gobject
Requires:       python3-platformdirs
Requires:       python3-Pillow
Requires:       python3-imageio
Requires:       python3-imageio-ffmpeg
Requires:       python3-screeninfo
Requires:       gtk3

%description
Waypaper is a GUI wallpaper manager for Wayland and Xorg Linux systems. It
supports a wide range of backends including swaybg, hyprpaper, swww, mpvpaper,
wallutils, swhkd, and Xorg-only backends, and supports GIFs and videos as
animated wallpapers.

%prep
%autosetup

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
install -Dpm 0644 data/waypaper.desktop %{buildroot}%{_datadir}/applications/waypaper.desktop
install -Dpm 0644 data/waypaper.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/waypaper.svg
install -Dpm 0644 data/waypaper.1.gz %{buildroot}%{_mandir}/man1/waypaper.1.gz

%files
%pyproject_save_files waypaper
%{_datadir}/applications/waypaper.desktop
%{_iconsdir}/hicolor/scalable/apps/waypaper.svg
%{_mandir}/man1/waypaper.1.gz

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-1
- Initial package