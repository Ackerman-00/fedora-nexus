Name:           waypaper
Version:        2.8
Release:        8%{?dist}
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
BuildRequires:  python3-pip
BuildRequires:  python3-installer
BuildRequires:  gzip

Requires:       python3-gobject
Requires:       python3-platformdirs
Requires:       python3-pillow
Requires:       python3-imageio
Requires:       (ffmpeg or ffmpeg-free)
Requires:       gobject-introspection
Requires:       gtk3
# waypaper shells out to pgrep/pkill (procps-ng) and killall (psmisc) to
# detect and stop running wallpaper backends (changer.py, options.py, app.py)
Requires:       procps-ng
Requires:       psmisc

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
tar -xzf %{SOURCE2} --strip-components=1 imageio_ffmpeg-0.6.0/imageio_ffmpeg

%build
%pyproject_wheel

%install
%pyproject_install
# Strip vendored deps from wheel metadata so RPM doesn't auto-generate
# unresolvable python3.Xdist(screeninfo)/imageio-ffmpeg requires
for f in %{buildroot}%{python3_sitelib}/waypaper-*.dist-info/METADATA; do
  [ -f "$f" ] && sed -i '/^Requires-Dist: screeninfo$/d' "$f" && sed -i '/^Requires-Dist: imageio-ffmpeg$/d' "$f" || true
done
install -Dpm 0644 data/waypaper.desktop %{buildroot}%{_datadir}/applications/waypaper.desktop
install -Dpm 0644 data/waypaper.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/waypaper.svg
install -Dpm 0644 data/waypaper.1.gz %{buildroot}%{_mandir}/man1/waypaper.1.gz
cp -a screeninfo %{buildroot}%{python3_sitelib}/
cp -a imageio_ffmpeg %{buildroot}%{python3_sitelib}/

%files
%{_bindir}/waypaper
%{python3_sitelib}/waypaper/
%{python3_sitelib}/waypaper-%{version}.dist-info/
%{python3_sitelib}/screeninfo/
%{python3_sitelib}/imageio_ffmpeg/
%{_datadir}/applications/waypaper.desktop
%{_iconsdir}/hicolor/scalable/apps/waypaper.svg
%{_mandir}/man1/waypaper.1.gz

%changelog
* Fri Aug 07 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-8
- Add Requires: procps-ng and psmisc. waypaper invokes pgrep/pkill and
  killall to detect and stop running wallpaper backends
  (changer.py seek_and_destroy, options.py get_monitor_names_with_*,
  app.py hyprpaper/mpvpaper/gslapper kill paths). Neither tool is part of
  a minimal Fedora install, so backend detection failed with
  "Exception: [Errno 2] No such file or directory: 'pgrep'"

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-7
- Add Requires: gobject-introspection (provides xlib-2.0.typelib needed by
  python3-gobject's gi import of Gdk, fixing "Typelib file for namespace
  'xlib', version '2.0' not found" crash on launch)

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-6
- Use boolean requires (ffmpeg or ffmpeg-free): installs on stock Fedora
  (ffmpeg-free) and on RPM Fusion systems (full ffmpeg) without conflicts

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-5
- Fix pyproject-rpm-macros 1.22 compatibility: replace %pyproject_save_files
  with explicit file listings
- Strip vendored screeninfo/imageio-ffmpeg from wheel METADATA to prevent
  RPM auto-generating unresolvable python3.14dist() requires

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-4
- Fix imageio_ffmpeg sdist extraction: --strip-components=2 stripped the
  imageio_ffmpeg/ directory level, scattering the module files into the
  top-level build dir and breaking the %install copy

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-3
- Add python3-pip BuildRequire: %pyproject_wheel imports pip to install
  build-system requires in its temp env

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-2
- Fetch vendored screeninfo and imageio-ffmpeg from PyPI sdists via
  remote Source1/Source2 URLs (auto-downloaded by COPR) instead of
  %{_sourcedir} copies of committed directories

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 2.8-1
- Initial package