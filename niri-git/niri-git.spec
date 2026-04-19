%global commit          5a450880615afeb242b66737bba0aba62559b9d1
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           niri-git
Version:        20260419
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

# Core portal implementations required for Niri screencasting and dialogs
Recommends:     xdg-desktop-portal-gtk
Recommends:     xdg-desktop-portal-gnome
Recommends:     gnome-keyring

Provides:       niri = %{version}-%{release}
Conflicts:      niri

%description
A scrollable-tiling Wayland compositor.
Compiled specifically for the Nexus repository via automated Git snapshot. Stripped of all secondary GUI bloat (waybar, swaylock, mako) and synchronized with our custom Xwayland bridge for peak performance.

%prep
%autosetup -n niri-%{commit}

%build
# Set the commit string for the binary
export NIRI_BUILD_COMMIT="%{version}"

# Let Cargo handle the raw compilation natively
cargo build --release

# Generate shell completions
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
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 20260415-1
- Initial Automated Git Snapshot Build
