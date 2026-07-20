%define _lto_cflags %{nil}

Name:           libcava
Version:        1.0.0
Release:        1%{?dist}
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
%autosetup %autosetup -n cava-%{version}

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

%files devel
%{_libdir}/libcava.so
%{_includedir}/cava/
%{_libdir}/pkgconfig/libcava.pc

%changelog
* Mon Jul 20 2026 Ackerman-00 <quietcraft@gmail.com> - 1.0.0-1
- Update to 1.0.0
