# These will be automatically populated by update.sh
%global commit          add2795134593faafce60e404a0a75df68e9ee0c
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260909215949

Name:           xwayland-satellite-git
# Epoch 1 is permanent: legacy 2026MMDD-dated builds sort ABOVE the current
# ^gitdate snapshots in rpm version comparison, so without it dnf keeps
# delivering stale builds. NEVER remove it.
Epoch:          1
Version:        0.8.2^%{gitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Rootless Xwayland integration for Wayland compositors (Git Snapshot)

License:        MPL-2.0
URL:            https://github.com/Supreeeme/xwayland-satellite
Source0:        %{url}/archive/%{commit}/xwayland-satellite-%{shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang
BuildRequires:  gcc
BuildRequires:  glibc-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-cursor)

Requires:       xorg-x11-server-Xwayland >= 23.1
Requires:       font(opensans)

Conflicts:      xwayland-satellite
Provides:       xwayland-satellite = %{version}-%{release}

%description
xwayland-satellite grants rootless Xwayland integration to any Wayland
compositor implementing xdg_wm_base and viewporter. This package tracks 
the bleeding-edge master branch.

%prep
%autosetup -n xwayland-satellite-%{commit}

# Dynamically fix the executable path in the systemd unit using system macros
sed -i 's|/usr/local/bin|%{_bindir}|g' resources/xwayland-satellite.service

# Remove vendored decoration font if it exists in the current git tree
rm -f OpenSans-Regular.ttf

%build
# Inject Fedora system optimization variables safely for static linkage
export CFLAGS="%{optflags} -ffat-lto-objects"
export CXXFLAGS="%{optflags} -ffat-lto-objects"
# Fedora-tuned Rust codegen (opt-level, single codegen unit, debuginfo for
# -debuginfo packages, frame pointers). Raw `cargo build` alone uses stock
# release defaults and skips all of this; there is no %cargo_build macro
# left on F44, so export RUSTFLAGS directly.
export RUSTFLAGS="%{build_rustflags}"

# We let Cargo handle the network fetch directly
cargo build --release --features systemd,fontconfig

%install
install -Dpm0755 target/release/xwayland-satellite -t %{buildroot}%{_bindir}
install -Dpm0644 resources/xwayland-satellite.service -t %{buildroot}%{_userunitdir}
install -Dpm0644 xwayland-satellite.man %{buildroot}%{_mandir}/man1/xwayland-satellite.1

%check
# Unit tests only: the testwl/ integration tests need a live Wayland session
# (same scope as Fedora official, which runs --lib). Re-export the %build
# flags - %check is a separate shell section, and without identical
# RUSTFLAGS cargo would rebuild the world with different codegen.
export CFLAGS="%{optflags} -ffat-lto-objects"
export CXXFLAGS="%{optflags} -ffat-lto-objects"
export RUSTFLAGS="%{build_rustflags}"
cargo test --release --features systemd,fontconfig --lib

%post
%systemd_user_post xwayland-satellite.service

%preun
%systemd_user_preun xwayland-satellite.service

%postun
%systemd_user_postun_with_reload xwayland-satellite.service

%files
%license LICENSE
%doc README.md
%{_bindir}/xwayland-satellite
%{_mandir}/man1/xwayland-satellite.1*
%{_userunitdir}/xwayland-satellite.service

%changelog
* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.2^20260909215949gitadd2795-2
- Run lib-only unit tests in %check (integration tests need a live session, same scope as Fedora official)
- Document permanent Epoch 1

* Thu Sep 10 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.2^20260909215949gitadd2795-1
- Nightly sync with upstream main branch (Commit: add2795)
