%global commit          cae55ed689bec8445d187f8057527a5dd515dab8
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260811081721
%global basever         2.1.0


Name:           caelestia-shell-mango
Version:        %{basever}^%{gitdate}git%{shortcommit}
Release:        3%{?dist}
Summary:        Desktop shell for MangoWM

License:        GPL-3.0-only
URL:            https://github.com/Ackerman-00/caelestia-shell-mango
Source0:        %{url}/archive/%{commit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  pkgconf-pkg-config
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  qt6-qtshadertools-devel
BuildRequires:  libglvnd-devel
BuildRequires:  wayland-devel
BuildRequires:  pipewire-devel
BuildRequires:  libqalculate-devel
BuildRequires:  aubio-devel
BuildRequires:  libcava-devel
BuildRequires:  fftw-devel

Requires:       mangowm
Requires:       quickshell
Requires:       app2unit
Requires:       pipewire
Requires:       aubio-lib
Requires:       libcava
Requires:       ddcutil
Requires:       brightnessctl
Recommends:     caelestia-cli-mango >= 2.0.0
Requires:       NetworkManager
Requires:       lm_sensors
Requires:       cliphist
Requires:       gpu-screen-recorder
Requires:       swappy
Requires:       wl-clipboard
Requires:       grim
Requires:       iproute
Requires:       setxkbmap
Requires:       libnotify
Requires:       procps-ng
Requires:       util-linux
Requires:       libxml2
Requires:       fprintd
Requires:       systemd
Requires:       polkit
Requires:       bash
Requires:       material-symbols-fonts
Recommends:     cascadia-code-nerd-fonts

Provides:       caelestia-shell = %{version}-%{release}
Conflicts:      caelestia-shell

%description
Caelestia Shell is a desktop shell built on Quickshell and Qt6.
Designed exclusively for MangoWM — will NOT work with Hyprland,
Sway, Niri, or other Wayland compositors.

This package tracks the main branch of caelestia-shell-mango.

Features:
- Application launcher (requires app2unit)
- Audio volume control via PipeWire IPC
- Desktop notifications
- On-screen display
- Sidebar with calendar, todo list, pomodoro timer
- Dashboard with media player, weather, system monitor
- Window info popout with move-to-workspace and float/kill controls

%prep
%autosetup -n caelestia-shell-mango-%{commit}

%build
export CFLAGS="%{optflags} -ffat-lto-objects"
export CXXFLAGS="%{optflags} -ffat-lto-objects"

%cmake -G Ninja \
    -DENABLE_MODULES="extras;plugin;shell" \
    -DINSTALL_LIBDIR=%{_libdir}/caelestia \
    -DINSTALL_QMLDIR=%{_qt6_qmldir} \
    -DINSTALL_QSCONFDIR=%{_datadir}/caelestia-shell \
    -DVERSION=%{basever} \
    -DGIT_REVISION=%{shortcommit} \
    -DDISTRIBUTOR=fedora-copr

%cmake_build

%install
%cmake_install

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/caelestia-shell << 'WRAPPER'
#!/bin/bash
export CAELESTIA_LIB_DIR="%{_libdir}/caelestia"
export CAELESTIA_XKB_RULES_PATH="/usr/share/X11/xkb/rules/base.lst"
exec /usr/bin/qs -p "%{_datadir}/caelestia-shell" "$@"
WRAPPER
chmod 755 %{buildroot}%{_bindir}/caelestia-shell

%post
if [ $1 -eq 1 ]; then
    echo ""
    echo "  Caelestia Shell installed!"
    echo "  → Read the repo for IPC commands, keybinds, and usage:"
    echo "    https://github.com/Ackerman-00/caelestia-shell-mango"
    echo ""
fi

%files
%license LICENSE
%doc README.md
%{_bindir}/caelestia-shell
%{_libdir}/caelestia/version
%dir %{_qt6_qmldir}/Caelestia/
%{_qt6_qmldir}/Caelestia/qmldir
%{_qt6_qmldir}/Caelestia/*.so
%{_qt6_qmldir}/Caelestia/*.qmltypes
%{_qt6_qmldir}/Caelestia/Internal/
%{_qt6_qmldir}/Caelestia/Models/
%{_qt6_qmldir}/Caelestia/Services/
%dir %{_datadir}/caelestia-shell/
%{_datadir}/caelestia-shell/shell.qml
%{_datadir}/caelestia-shell/LICENSE
%{_datadir}/caelestia-shell/assets/
%{_datadir}/caelestia-shell/components/
%{_datadir}/caelestia-shell/config/
%{_datadir}/caelestia-shell/modules/
%{_datadir}/caelestia-shell/services/
%{_datadir}/caelestia-shell/utils/

%changelog
* Sat Oct 03 2026 Ackerman-00 <quietcraft@gmail.com> - 2.1.0^20260811081721gitcae55ed-3
- Fix stale -DVERSION hardcode: the built version binary reported 2.0.0
  while the pinned commit cae55ed is the upstream v2.1.0 tag. Derive
  -DVERSION from a %global basever macro so Version and the CMake version
  can no longer diverge, and teach update.sh to resolve basever from the
  upstream tag pointing at HEAD

* Wed Aug 12 2026 Ackerman-00 <quietcraft@gmail.com> - 2.1.0^20260811081721gitcae55ed-2
- Require brightnessctl: Brightness.qml falls back to brightnessctl for
  displays that present a backlight interface (ddcutil covers DDC-only panels)

* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 2.1.0^20260811081721gitcae55ed-1
- Nightly sync with upstream main branch (Commit: cae55ed)
