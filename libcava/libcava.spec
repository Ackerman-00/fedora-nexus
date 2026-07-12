%define _lto_cflags %{nil}

Name:           libcava
Version:        0.10.7
Release:        2%{?dist}
Summary:        Fork of CAVA to build it as a shared library

License:        MIT
URL:            https://github.com/LukashonakV/cava
Source0:        %{url}/archive/%{version}/cava-%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  cmake
BuildRequires:  autoconf-archive
BuildRequires:  gcc
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  ncurses-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  iniparser-devel
BuildRequires:  libglvnd-devel
BuildRequires:  SDL2-devel
BuildRequires:  portaudio-devel

%description
Fork of CAVA to build it as a shared library. Does not provide the
cava executable — only the libcava shared library for integration
into other projects (e.g. waybar).

%package devel
Summary:        Development files for libcava
Requires:       libcava%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config file for developing with libcava.

%prep
%autosetup -n cava-%{version}

%build
%meson \
    -Dcava_font=false \
    -Dinput_sndio=disabled \
    -Dinput_jack=disabled
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libcava.so.*
%dir %{_datadir}/cava/
%{_datadir}/cava/*
%dir %{_datadir}/consolefonts/
%{_datadir}/consolefonts/cava.psf

%files devel
%{_libdir}/libcava.so
%{_includedir}/cava/
%{_libdir}/pkgconfig/libcava.pc

%changelog
* Sun Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.10.7-2
- Match upstream AUR PKGBUILD: release tarball, -Dcava_font=false only
- Build library only (default build_target=['lib'])
- Add all build dependencies available in Fedora main repos
- Drop LTO
- Disable input_sndio, input_jack (deps not in Fedora main repos)

* Sun Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.10.7-1
- Initial package for Fedora Nexus
