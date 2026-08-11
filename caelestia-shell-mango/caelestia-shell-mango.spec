# These will be automatically populated by update.sh
%global commit          cae55ed689bec8445d187f8057527a5dd515dab8
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260811081721

# NOTE: This package is for MangoWM only. It will NOT work with
# other Wayland compositors (Hyprland, Sway, Niri, etc.).

Name:           caelestia-shell-mango
Version:        2.0.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
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

# === RUNTIME DEPENDENCIES ===
# Compositor (MangoWM only!)
Requires:       mangowm
# Quickshell shell runner
Requires:       quickshell-git
# Launcher
Requires:       app2unit
# Audio
Requires:       pipewire
# Audio visualiser (beattracker links libaubio.so.5; pulls fftw + portaudio transitively)
Requires:       aubio-lib
Requires:       libcava
# Monitor brightness (DDC) for displays without a backlight interface
Requires:       ddcutil
# Colour scheme/wallpaper/record via the CLI (services/Colours.qml, Wallpapers.qml,
# modules/controlcenter/appearance, launcher Schemes.qml, utils/SysInfo.qml)
Recommends:     caelestia-cli-mango >= 2.0.0
# Network
Requires:       NetworkManager
# Hardware monitoring
Requires:       lm_sensors
# Clipboard manager (modules/launcher/services/Clipboard.qml)
# cliphist is missing from Fedora 43, but this repo now ships it for every
# supported release, so it can be required unconditionally again.
Requires:       cliphist
# Screen recording (modules/utilities/Content.qml record card)
Requires:       gpu-screen-recorder
# Screenshot
Requires:       swappy
Requires:       wl-clipboard
# Active-window preview (components/images/MangoWindow.qml: grim -T <toplevel>)
Requires:       grim
# VPN status (services/VPN.qml: ip link show)
Requires:       iproute
# Keyboard layout switching (modules/bar/popouts/kblayout/KbLayoutModel.qml)
Requires:       setxkbmap
# Notifications
Requires:       libnotify
# Process monitoring
Requires:       procps-ng
# Disk info, etc
Requires:       util-linux
# XKB layout parsing
Requires:       libxml2
# Fingerprint auth
Requires:       fprintd
# Session management
Requires:       systemd
# Privilege escalation
Requires:       polkit
# Shell commands
Requires:       bash
# Fonts
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
    -DVERSION=2.0.0 \
    -DGIT_REVISION=%{shortcommit} \
    -DDISTRIBUTOR=fedora-copr

%cmake_build

%install
%cmake_install

# Create wrapper script that calls qs with correct config path
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
# Caelestia QML plugin (for Quickshell)
%dir %{_qt6_qmldir}/Caelestia/
%{_qt6_qmldir}/Caelestia/qmldir
%{_qt6_qmldir}/Caelestia/*.so
%{_qt6_qmldir}/Caelestia/*.qmltypes
%{_qt6_qmldir}/Caelestia/Internal/
%{_qt6_qmldir}/Caelestia/Models/
%{_qt6_qmldir}/Caelestia/Services/
# Shell config (QML files)
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
* Tue Aug 11 2026 Ackerman-00 <quietcraft@gmail.com> - 2.0.0^20260811081721gitcae55ed-1
- Nightly sync with upstream main branch (Commit: cae55ed)
