# These will be automatically populated by update.sh
%global commit          feb3e43f1475e0865bb89cbd1e898b34d1d2ccf6
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260802200721

Name:           niri-git
Epoch:          1
Version:        26.04^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        A scrollable-tiling Wayland compositor (Nexus Optimized Git Snapshot)

License:        GPL-3.0-or-later
URL:            https://github.com/YaLTeR/niri
Source0:        %{url}/archive/%{commit}/niri-%{shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang
BuildRequires:  systemd-rpm-macros
BuildRequires:  mesa-libEGL-devel
BuildRequires:  pkgconfig(cairo-gobject)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libpipewire-0.3)

Requires:       xwayland-satellite-git
Requires:       mesa-dri-drivers
Requires:       mesa-libEGL
Requires:       libwayland-server

# Core portal service (at least one backend must be installed)
Requires:       xdg-desktop-portal
# Screencasting (niri feature) and GTK file picker backends
Recommends:     xdg-desktop-portal-gnome
Recommends:     xdg-desktop-portal-gtk
Recommends:     gnome-keyring

Provides:       niri = %{version}-%{release}
Provides:       wayland-compositor
Conflicts:      niri

%description
A scrollable-tiling Wayland compositor.
Compiled specifically for the Nexus repository via automated Git snapshot. Stripped of all secondary GUI bloat (waybar, swaylock, mako) and synchronized with our custom Xwayland bridge for peak performance.

%prep
%autosetup -n niri-%{commit}

%build
# Set the commit string for the binary
export NIRI_BUILD_COMMIT="%{shortcommit}"

# Inject Fedora system optimization variables safely
export CFLAGS="%{optflags} -ffat-lto-objects"
export CXXFLAGS="%{optflags} -ffat-lto-objects"

# Let Cargo handle the raw compilation natively
cargo build --release --features default

# Generate shell completions safely by isolating runtime context
export XDG_RUNTIME_DIR=$(mktemp -d)
target/release/niri completions bash > ./niri.bash
target/release/niri completions fish > ./niri.fish
target/release/niri completions zsh > ./_niri

%install
# Install the core binaries
install -Dpm0755 target/release/niri -t %{buildroot}%{_bindir}
install -Dpm0755 resources/niri-session -t %{buildroot}%{_bindir}

# Install standard Wayland session and systemd configurations
install -Dpm0644 resources/niri.desktop -t %{buildroot}%{_datadir}/wayland-sessions
install -Dpm0644 resources/niri-portals.conf -t %{buildroot}%{_datadir}/xdg-desktop-portal
install -Dpm0644 resources/niri.service -t %{buildroot}%{_userunitdir}
install -Dpm0644 resources/niri-shutdown.target -t %{buildroot}%{_userunitdir}

# Install completions
install -Dpm0644 niri.bash %{buildroot}%{_datadir}/bash-completion/completions/niri
install -Dpm0644 niri.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/niri.fish
install -Dpm0644 _niri %{buildroot}%{_datadir}/zsh/site-functions/_niri

%files
%license LICENSE
%doc README.md
%doc resources/default-config.kdl
%{_bindir}/niri
%{_bindir}/niri-session
%{_datadir}/wayland-sessions/niri.desktop
%{_datadir}/xdg-desktop-portal/niri-portals.conf
%{_userunitdir}/niri.service
%{_userunitdir}/niri-shutdown.target
%{_datadir}/bash-completion/completions/niri
%{_datadir}/fish/vendor_completions.d/niri.fish
%{_datadir}/zsh/site-functions/_niri

%changelog
* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 1:26.04^20260802200721gitfeb3e43-1
- Bump Epoch to 1 so current ^gitdate snapshots sort above the legacy
  2026MMDD-dated builds (dnf was installing the stale 20260605 snapshot)

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 26.04^20260802200721gitfeb3e43-1
- Nightly sync with upstream main branch (Commit: feb3e43)
