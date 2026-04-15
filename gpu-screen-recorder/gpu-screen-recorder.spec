Name:           gpu-screen-recorder
Version:        5.12.3-1@2026-04-14_1776180408
Release:        1%{?dist}
Summary:        Shadowplay-like screen recorder for Linux (Nexus Optimized)

License:        GPL-3.0-or-later

# Using the AppImage mirror URL so the Python engine can track actual version tags
URL:            https://github.com/pkgforge-dev/gpu-screen-recorder-AppImage
Source:         https://dec05eba.com/snapshot/gpu-screen-recorder.git.%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libva-drm)
BuildRequires:  vulkan-headers
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  pkgconfig(libglvnd)
BuildRequires:  pipewire-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xdamage)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  systemd-rpm-macros

Requires(post): libcap
Requires:       libappindicator-gtk3

%description
An extremely fast hardware-accelerated screen recorder for Linux. 
Uses the GPU exclusively for video encoding to maintain near-zero CPU impact. 
Optimized for the Nexus repository for peak performance on Wayland.

%prep
%autosetup -c

%build
%meson -Dcapabilities=false
%meson_build

%install
%meson_install

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%postun
%systemd_user_postun %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%caps(cap_sys_admin+ep) %{_bindir}/gsr-kms-server
%{_datadir}/%{name}/
%{_includedir}/gsr/
%{_userunitdir}/%{name}.service
%{_mandir}/man1/*.1*

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 5.12.5-1
- Initial Optimized Build with tagged GitHub mirror for auto-updates
