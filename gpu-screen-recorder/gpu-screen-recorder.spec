Name:           gpu-screen-recorder
Version:        6.1.7
Release:        2%{?dist}
Summary:        A shadowplay-like screen recorder for Linux. The fastest screen recorder for Linux

License:        GPL-3.0-or-later
URL:            https://git.dec05eba.com/gpu-screen-recorder/about

Source0:        https://dec05eba.com/snapshot/gpu-screen-recorder.git.%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  pkgconfig(libswresample)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(libva-drm)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xdamage)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  vulkan-headers
BuildRequires:  vulkan-loader-devel

Requires:       libglvnd
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       libxcb
Requires:       pulseaudio-libs
Requires:       libwayland-client
Requires:       vulkan-loader
Recommends:     turbojpeg
Recommends:     xdotool
Recommends:     /usr/bin/pactl
Recommends:     (ffmpeg or ffmpeg-free)
Recommends:     psmisc
Recommends:     /usr/bin/notify-send

%description
GPU Screen Recorder is a shadowplay-like screen recorder for Linux. It can
record or stream the screen (or a window or a region) at high FPS with low
overhead using hardware video encoding on NVIDIA, AMD or Intel GPUs. It works
on both X11 and Wayland.

%prep
%autosetup -c

%build
%meson -Dcapabilities=false
%meson_build

%install
%meson_install

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true
%check
%meson_test || true

%files
%license LICENSE
%doc README.md
%{_bindir}/gpu-screen-recorder
%{_bindir}/gsr-cli
%caps(cap_sys_admin=ep) %{_bindir}/gsr-kms-server
%{_includedir}/gsr/plugin.h
%{_datadir}/gpu-screen-recorder
%{_mandir}/man1/gpu-screen-recorder.1*
%{_mandir}/man1/gsr-cli.1*
%{_mandir}/man1/gsr-kms-server.1*
/usr/lib/systemd/user/%{name}.service
/usr/lib/modprobe.d/gsr-nvidia.conf

%changelog
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 6.1.7-2
- Add vulkan-loader-devel BuildRequires: libavfilter-free 8.1.3 Requires libplacebo.so.360, whose build-time resolution under -Wl,--no-allow-shlib-undefined needs libvulkan.so.1 present; dnf builddep left it out and the link failed (undefined vkGetInstanceProcAddr)
* Tue Nov 03 2026 Ackerman-00 <no-reply> - 6.1.7-1
- Update to version 6.1.7
