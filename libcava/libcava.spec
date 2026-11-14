%define _lto_cflags %{nil}

Name:           libcava
Version:        1.0.0
Release:        2%{?dist}
Summary:        Fork of CAVA to build it as a shared library

License:        MIT
URL:            https://github.com/LukashonakV/cava
Source0:        %{url}/archive/%{version}.tar.gz

BuildRequires:  meson
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
    -Dbuild_target=lib \
    -Dcava_font=false \
    -Dinput_sndio=disabled \
    -Dinput_jack=disabled
%meson_build

%install
%meson_install

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%doc README.md
%{_libdir}/libcava.so.*

%files devel
%{_libdir}/libcava.so
%{_includedir}/cava/
%{_libdir}/pkgconfig/libcava.pc

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 1.0.0-2
- Move the in-app updater strip into %install

* Mon Jul 20 2026 Ackerman-00 <no-reply> - 1.0.0-1
- Update to 1.0.0
