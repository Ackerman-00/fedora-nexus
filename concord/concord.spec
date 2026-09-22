%global debug_package %{nil}
%global crate concord

Name:           concord
Version:        2.6.0
Release:        1%{?dist}
Summary:        Feature-rich TUI client for Discord
License:        GPL-3.0-only
URL:            https://github.com/chojs23/concord
Source0:        https://github.com/chojs23/concord/archive/refs/tags/v%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  clang-devel
BuildRequires:  cmake
BuildRequires:  nasm
BuildRequires:  pkgconf-pkg-config
# Voice + stream-broadcast features (upstream README Fedora list — the same
# set cargo-dist CI uses via apt): alsa (cpal), pipewire (capture),
# libva (hardware H.264 encode via cros-codecs vaapi).
BuildRequires:  alsa-lib-devel
BuildRequires:  pipewire-devel
BuildRequires:  libva-devel

# Upstream README runtime requirements for Linux release builds.
Requires:       alsa-lib
Requires:       libva
Requires:       mesa-libEGL
Requires:       pipewire-libs
Requires:       xdg-desktop-portal
# External media playback uses mpv and is off by default (Display options).
# Weak dep: ignored on repos without mpv (RPMFusion-only), suggested where present.
Recommends:     mpv

%description
Concord is a feature-rich TUI client for Discord, written in Rust with
ratatui. Voice calls, screen sharing, notifications, and rich media
previews in the terminal.

%prep
%setup -q -n %{crate}-%{version}

%build
# Default cargo features (voice-playback + stream-broadcast) match upstream
# release builds (dist-workspace.toml). Plain --release keeps Cargo's
# no-debuginfo default, hence debug_package nil above (matugen pattern).
export CARGO_NET_OFFLINE=false
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
install -Dm755 target/release/concord %{buildroot}%{_bindir}/concord

%files
%license LICENSE
%doc README.md
%doc CHANGELOG.md
%doc docs/keymap-options.md
%doc docs/theme-options.md
%{_bindir}/concord

%changelog
* Tue Sep 22 2026 Ackerman-00 <quietcraft@gmail.com> - 2.6.0-1
- Auto-update to upstream stable release v2.6.0
