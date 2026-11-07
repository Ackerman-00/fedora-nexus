%global debug_package %{nil}
%global commit         1d07e318d8bcf51ca3f8b75980fbea15c0edb37c

Name:           ladybird-unstable
Version:        0.0.0
Release:        1.20261107git1d07e31%{?dist}
Summary:        Truly independent web browser (git master; unstable)
License:        BSD-2-Clause
URL:            https://ladybird.org
Source0:        https://github.com/LadybirdBrowser/ladybird/archive/%{commit}.tar.gz

BuildRequires:  autoconf-archive
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  ccache
BuildRequires:  cmake
BuildRequires:  curl
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  glslang
BuildRequires:  libdrm-devel
BuildRequires:  liberation-sans-fonts
BuildRequires:  libglvnd-devel
BuildRequires:  libtool
BuildRequires:  nasm
BuildRequires:  ncurses-devel
BuildRequires:  ninja-build
BuildRequires:  patchelf
BuildRequires:  perl-FindBin
BuildRequires:  perl-IPC-Cmd
BuildRequires:  perl-lib
BuildRequires:  perl-Time-Piece
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  python3
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtpositioning-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  tar
BuildRequires:  unzip
BuildRequires:  xcb-util-wm-devel
BuildRequires:  zip
BuildRequires:  rust
BuildRequires:  cargo

%description
Ladybird browser built from the git master branch (unstable).

%prep
%autosetup -n ladybird-%{commit}

%build
export LDFLAGS="$LDFLAGS -lstdc++"
python3 Meta/ladybird.py build --preset Release

%install
python3 Meta/ladybird.py install --preset Release

%files
%license LICENSE
%{_bindir}/Ladybird
%dir %{_datadir}/ladybird
%{_datadir}/ladybird/*

%post
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2>/dev/null || :

%changelog
* Sat Nov 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-1.20261107git1d07e31
- Initial import; link vcpkg ports against libstdc++ (RPM -fexceptions emits DW.ref.__gxx_personality_v0)
