Name:           gpu-screen-recorder
Version:        6.0.0
Release:        2%{?dist}
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
# dlopen()ed at runtime by src/image_writer.c for JPEG screenshots; the code
# falls back to the bundled stb encoder if absent, so this is optional.
Recommends:     turbojpeg

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

%check
%meson_test || true

%files
%license LICENSE
%doc README.md
%{_bindir}/gpu-screen-recorder
%{_bindir}/gsr-cli
# gsr-kms-server needs CAP_SYS_ADMIN so monitor capture works without a
# password prompt (KMS backend, no desktop portal). Declaring it via %%caps
# keeps the capability in rpm's own file metadata, so "rpm -V" stays clean;
# a %%post setcap would set it behind rpm's back and always report "P".
%caps(cap_sys_admin=ep) %{_bindir}/gsr-kms-server
%{_includedir}/gsr/plugin.h
%{_datadir}/gpu-screen-recorder
%{_mandir}/man1/gpu-screen-recorder.1*
%{_mandir}/man1/gsr-cli.1*
%{_mandir}/man1/gsr-kms-server.1*
/usr/lib/systemd/user/%{name}.service
/usr/lib/modprobe.d/gsr-nvidia.conf

%changelog
* Sat Aug 08 2026 Ackerman-00 <quietcraft@gmail.com> - 6.0.0-2
- Declare gsr-kms-server's CAP_SYS_ADMIN with %%caps() in %%files instead of
  running setcap from %%post. The scriptlet changed the file behind rpm's
  back, so every install left "rpm -V gpu-screen-recorder" reporting
  "........P /usr/bin/gsr-kms-server". Drops the now-unneeded
  Requires(post): libcap.
- Recommend turbojpeg: src/image_writer.c dlopen()s libturbojpeg.so.0 for
  fast JPEG screenshot output and falls back to the bundled stb encoder when
  it is absent, so it is optional rather than a hard Requires.

* Sat Aug 08 2026 Ackerman-00 <quietcraft@gmail.com> - 6.0.0-1
- Update to version 6.0.0
- 6.0.0 ships a new gsr-cli binary + man page; add to %files (fixes
  "Installed (but unpackaged) file(s)" build error)
