%global commit          4d214891017fa7b893df1140d24f76defba0eb88
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           gpu-screen-recorder-git
Version:        20260415
Release:        1%{?dist}
Summary:        Shadowplay-like screen recorder for Linux (Nexus Git Snapshot)

License:        GPL-3.0-or-later
URL:            https://git.dec05eba.com/gpu-screen-recorder/about
Source0:        https://dec05eba.com/snapshot/gpu-screen-recorder.git.%{commit}.tar.gz

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

Provides:       gpu-screen-recorder = %{version}-%{release}
Conflicts:      gpu-screen-recorder

%description
Bleeding-edge Git snapshot of gpu-screen-recorder. 
Uses the GPU exclusively for video encoding to maintain near-zero CPU impact. 
Optimized for the Nexus repository for peak performance on Wayland.

%prep

%setup -q -n gpu-screen-recorder.git.%{commit}

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
%{_bindir}/gpu-screen-recorder

%caps(cap_sys_admin+ep) %{_bindir}/gsr-kms-server
%{_datadir}/gpu-screen-recorder/
%{_includedir}/gsr/
%{_userunitdir}/gpu-screen-recorder.service
%{_mandir}/man1/*.1*

%changelog
* Wed Apr 15 2026 Nexus Bot <bot@github.com> - 20260415-1
- Initial Automated Git Snapshot Build for Nexus
