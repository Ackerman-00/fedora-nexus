Name:           waypaper
Version:        2.8
Release:        2%{?dist}
Summary:        GUI wallpaper manager for Wayland and Xorg Linux systems

License:        GPL-3.0-only AND MIT AND BSD-2-Clause
URL:            https://github.com/anufrievroman/waypaper
Source0:        %{url}/archive/%{version}.tar.gz
Source1:        https://files.pythonhosted.org/packages/source/s/screeninfo/screeninfo-0.8.1.tar.gz
Source2:        https://files.pythonhosted.org/packages/source/i/imageio-ffmpeg/imageio_ffmpeg-0.6.0.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  gzip

Requires:       python3-gobject
Requires:       python3-platformdirs
Requires:       python3-Pillow
Requires:       python3-imageio
Requires:       ffmpeg-free
Requires:       gtk3

%description
Waypaper is a GUI wallpaper manager for Wayland and Xorg Linux systems. It
supports a wide range of backends including swaybg, hyprpaper, swww, mpvpaper,
wallutils, swhkd, and Xorg-only backends, and supports GIFs and videos as
animated wallpapers. The screeninfo and imageio-ffmpeg Python modules are
vendored from their PyPI sdists since they are not packaged in Fedora;
imageio-ffmpeg falls back to the system ffmpeg binary.

%prep
%autosetup
tar -xzf %{SOURCE1} --strip-components=1 screeninfo-0.8.1/screeninfo
tar -xzf %{SOURCE2} --strip-components=2 imageio_ffmpeg-0.6.0/imageio_ffmpeg

%build
%pyproject_wheel

%install
%pyproject_install
install -Dpm 0644 data/waypaper.desktop %{buildroot}%{_datadir}/applications/waypaper.desktop
install -Dpm 0644 data/waypaper.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/waypaper.svg
install -Dpm 0644 data/waypaper.1.gz %{buildroot}%{_mandir}/man1/waypaper.1.gz
cp -a screeninfo %{buildroot}%{python3_sitelib}/
cp -a imageio_ffmpeg %{buildroot}%{python3_sitelib}/

%files
%pyproject_save_files waypaper
%{python3_sitelib}/screeninfo
%{python3_sitelib}/imageio_ffmpeg
%{_datadir}/applications/waypaper.desktop
%{_iconsdir}/hicolor/scalable/apps/waypaper.svg
%{_mandir}/man1/waypaper.1.gz

%changelog
* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-2
- Fetch vendored screeninfo and imageio-ffmpeg from PyPI sdists via
  remote Source1/Source2 URLs (auto-downloaded by COPR) instead of
  %{_sourcedir} copies of committed directories

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-1
- Initial package