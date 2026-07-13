# These will be automatically populated by update.sh
%global commit          a2b5c635d8c8c99b286967658d0d177044887eb8
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260712222532

Name:           xwayland-satellite-git
Version:        0.8.1^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
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

Requires:       xorg-x11-server-Xwayland
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

# We let Cargo handle the network fetch directly
cargo build --release --features systemd,fontconfig

%install
install -Dpm0755 target/release/xwayland-satellite -t %{buildroot}%{_bindir}
install -Dpm0644 resources/xwayland-satellite.service -t %{buildroot}%{_userunitdir}

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
%{_userunitdir}/xwayland-satellite.service

%changelog
* Mon Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.8.1^20260712222532gita2b5c63-1
- Nightly sync with upstream main branch (Commit: a2b5c63)
