%global commit          e3146fa3e8bc8d2af63841786d8448e64493000c
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260518194701

Name:           libcava
Version:        0.10.7^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Console-based Audio Visualizer (shared library fork)

License:        MIT
URL:            https://github.com/LukashonakV/cava
Source0:        %{url}/archive/%{commit}.tar.gz

BuildRequires:  meson
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libspa-0.2)
BuildRequires:  desktop-file-utils
BuildRequires:  iniparser-devel

%description
Fork of CAVA to build it as a shared library. Includes both the libcava
shared library for development integration and the cava command-line
audio visualizer.

%package devel
Summary:        Development files for libcava
Requires:       libcava%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(fftw3)

%description devel
Headers and pkg-config file for developing with libcava.

%prep
%autosetup -n cava-%{commit}

%build
%meson \
    -Dbuild_target=lib,exe \
    -Dinput_pulse=enabled \
    -Dinput_pipewire=enabled \
    -Doutput_ncurses=disabled \
    -Dinput_alsa=disabled \
    -Dinput_portaudio=disabled \
    -Dinput_sndio=disabled \
    -Dinput_oss=disabled \
    -Dinput_jack=disabled \
    -Doutput_sdl=disabled \
    -Doutput_sdl_glsl=disabled
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_bindir}/cava
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
* Sun Jul 13 2026 Ackerman-00 <quietcraft@gmail.com> - 0.10.7^20260518194701gite3146fa-1
- Initial package for Fedora Nexus
