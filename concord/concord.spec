%global crate concord

Name:           concord
Version:        2.7.1
Release:        2%{?dist}
Summary:        Feature-rich TUI client for Discord
License:        GPL-3.0-only
URL:            https://github.com/chojs23/concord
Source0:        https://github.com/chojs23/concord/archive/refs/tags/v%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  rust-srpm-macros
BuildRequires:  gcc
BuildRequires:  gcc-c++
# btls-sys: git apply on vendored BoringSSL
BuildRequires:  git-core
BuildRequires:  clang-devel
BuildRequires:  cmake
BuildRequires:  nasm
BuildRequires:  pkgconf-pkg-config
BuildRequires:  alsa-lib-devel
BuildRequires:  pipewire-devel
BuildRequires:  libva-devel

Requires:       alsa-lib
Requires:       libva
Requires:       mesa-libEGL
Requires:       pipewire-libs
Requires:       xdg-desktop-portal
Recommends:     mpv

%description
Concord is a feature-rich TUI client for Discord, written in Rust with
ratatui. Voice calls, screen sharing, notifications, and rich media
previews in the terminal.

%prep
%setup -q -n %{crate}-%{version}

%build
export CARGO_NET_OFFLINE=false
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
install -Dm755 target/release/concord %{buildroot}%{_bindir}/concord

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%doc README.md
%doc CHANGELOG.md
%doc docs/keymap-options.md
%doc docs/theme-options.md
%{_bindir}/concord

%changelog
* Mon Nov 16 2026 Ackerman-00 <no-reply> - 2.7.1-2
- Drop the MSRV rewrite: every chroot ships rustc >= 1.99.1 (F43/F44/F45
  1.99.1, rawhide 1.100.0), so the sed only rewrote a floor already satisfied

* Mon Nov 16 2026 Ackerman-00 <no-reply> - 2.7.1-1
- Auto-update to upstream stable release v2.7.1
