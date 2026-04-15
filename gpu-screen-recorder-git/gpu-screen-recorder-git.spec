Name:           gpu-screen-recorder
Version:        5.12.5
Release:        1%{?dist}
Summary:        Shadowplay-like screen recorder for Linux (Nexus Optimized)

License:        GPL-3.0-or-later
URL:            https://git.dec05eba.com/%{name}/about

Source:         https://dec05eba.com/snapshot/%{name}.git.%{version}.tar.gz

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
# -c automatically handles unpredictable internal tarball folder names
%autosetup -c

%build
%meson -Dcapabilities=false
%meson_build

%install
%meson_install

%post
%systemd_user_post gpu-screen-recorder.service

%preun
%systemd_user_preun gpu-screen-recorder.service

%postun
%systemd_user_postun gpu-screen-recorder.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%caps(cap_sys_admin+ep) %{_bindir}/gsr-kms-server
%{_datadir}/%{name}/scripts/*.sh
%{_includedir}/gsr/plugin.h
%{_userunitdir}/%{name}.service
%{_modprobedir}/gsr-nvidia.conf
%{_mandir}/man1/gsr-kms-server.1*
%{_mandir}/man1/%{name}.1*

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 5.12.5-1
- Switched to stable releases matching Terra logic to fix build errors
