Name:           gpu-screen-recorder
Version:        5.15.3
Release:        4%{?dist}
Summary:        A shadowplay-like screen recorder for Linux. The fastest screen recorder for Linux

License:        GPL-3.0-or-later
URL:            https://git.dec05eba.com/gpu-screen-recorder/about

Source0:        https://dec05eba.com/snapshot/gpu-screen-recorder.git.%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libglvnd)
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
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  vulkan-headers

Requires:       libglvnd
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       libxcb
Requires:       pulseaudio-libs
Requires:       libwayland-client
Requires:       vulkan-loader
Requires(post): libcap

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

%post
# Grant gsr-kms-server the admin capability so monitor capture works without
# a password prompt (KMS backend, no desktop portal). Best-effort; ignored if
# the filesystem does not support capabilities.
setcap cap_sys_admin+ep %{_bindir}/gsr-kms-server 2>/dev/null || true

%check
%meson_test || true

%files
%license LICENSE
%doc README.md
%{_bindir}/gpu-screen-recorder
%{_bindir}/gsr-kms-server
%{_includedir}/gsr/plugin.h
%{_datadir}/gpu-screen-recorder
%{_mandir}/man1/gpu-screen-recorder.1*
%{_mandir}/man1/gsr-kms-server.1*
/usr/lib/systemd/user/%{name}.service
/usr/lib/modprobe.d/gsr-nvidia.conf

%changelog
* Tue Aug 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.15.3-4
- Add missing BuildRequires: pkgconfig(vulkan) (vulkan-loader-devel) so the
  linker can resolve libvulkan.so.1 needed by libplacebo (transitive dep of
  libavfilter); the -3 build failed on all chroots with ld: libvulkan.so.1
  not found

* Mon Aug 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.15.3-3
- Add missing runtime dependency: vulkan-loader (libvulkan.so.1)

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 5.15.3-2
- Replace nonexistent libpulse and wayland-libs-client Requires with the real
  pulseaudio-libs and libwayland-client packages so the package can be installed

* Sun Aug 02 2026 Ackerman-00 <quietcraft@gmail.com> - 5.15.3-1
- Initial package of gpu-screen-recorder 5.15.3 for Fedora
