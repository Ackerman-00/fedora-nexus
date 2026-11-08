%global debug_package %{nil}
%global _lto_cflags %{nil}
%global commit         1d07e318d8bcf51ca3f8b75980fbea15c0edb37c

Name:           ladybird-unstable
Version:        0.0.0
Release:        7.20261107git1d07e31%{?dist}
Summary:        Truly independent web browser (git master; unstable)
License:        BSD-2-Clause
URL:            https://ladybird.org
Source0:        https://github.com/LadybirdBrowser/ladybird/archive/%{commit}.tar.gz
Source1:        harfbuzz-overlay-portfile.cmake
Source2:        harfbuzz-overlay-vcpkg.json
Source3:        harfbuzz-overlay-fix-win32-build.patch
Source4:        harfbuzz-overlay-config.cmake.in
Source5:        harfbuzz-overlay-usage

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
BuildRequires:  lld
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
# harfbuzz port: C driver link under -fexceptions needs libstdc++ (DW.ref personality); overlay adds -Dwith_libstdcxx=true
mkdir -p Meta/CMake/vcpkg/overlay-ports/harfbuzz
cp -p %{SOURCE1} Meta/CMake/vcpkg/overlay-ports/harfbuzz/portfile.cmake
cp -p %{SOURCE2} Meta/CMake/vcpkg/overlay-ports/harfbuzz/vcpkg.json
cp -p %{SOURCE3} Meta/CMake/vcpkg/overlay-ports/harfbuzz/fix-win32-build.patch
cp -p %{SOURCE4} Meta/CMake/vcpkg/overlay-ports/harfbuzz/harfbuzzConfig.cmake.in
cp -p %{SOURCE5} Meta/CMake/vcpkg/overlay-ports/harfbuzz/usage

%build
python3 Meta/ladybird.py vcpkg --preset Release
cmake --preset Release -S . -B Build/release -DBUILD_TESTING=OFF -DENABLE_INSTALL_FREEDESKTOP_FILES=OFF -DCMAKE_INSTALL_PREFIX=/opt/ladybird -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=OFF
cmake --build Build/release --parallel %{?_smp_build_ncpus}

%install
DESTDIR=%{buildroot} cmake --install Build/release --component ladybird_Runtime
DESTDIR=%{buildroot} cmake --install Build/release --component Lagom_Runtime
DESTDIR=%{buildroot} cmake --install Build/release --component ladybird_SystemIntegration
find Build/release/vcpkg_installed/*-linux-dynamic/lib -maxdepth 1 -name '*.so*' -exec cp -a {} %{buildroot}/opt/ladybird/lib/ \;
chmod -R u+w %{buildroot}/opt/ladybird

%files
%license LICENSE
/opt/ladybird
%{_bindir}/ladybird
%{_datadir}/applications/org.ladybird.Ladybird.desktop
%{_datadir}/dbus-1/services/org.ladybird.Ladybird.service
%{_datadir}/icons/hicolor/scalable/apps/org.ladybird.Ladybird.svg
%{_metainfodir}/org.ladybird.Ladybird.metainfo.xml

%post
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2>/dev/null || :

%postun
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2>/dev/null || :

%changelog
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-7.20261107git1d07e31
- Fix COPR timeout (18000s, build 11287677 died at 3536/3536): build with -DBUILD_TESTING=OFF so test targets are never built, install upstream's Linux package layout (prefix /opt/ladybird, ladybird_Runtime+Lagom_Runtime+ladybird_SystemIntegration components), bundle the vcpkg shared libraries into /opt/ladybird/lib, and set -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=OFF so installed RUNPATHs are $ORIGIN-based; add lld (picked automatically by ladybird next to gcc for faster links)
- Spec previously installed to the cmake default prefix (/usr/local) with no DESTDIR and shipped only /usr/bin/Ladybird and share/ladybird; the real layout is /opt/ladybird plus /usr/bin/ladybird and freedesktop files (found by reading UI/cmake/InstallRules.cmake in Source0)
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-6.20261107git1d07e31
- Drop LTO (_lto_cflags %{nil}): AK final link fails in COPR mock with undefined mi_heap_malloc/mi_malloc in ltrans partitions; deterministic across two builds (11285658, 11285927) while the same link passes in an isolated repro - partition-assignment-dependent weak-DSO resolution under LTO
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-5.20261107git1d07e31
- Rebuild after 11285658 failed at the AK link (undefined mi_* refs); failure not reproducible in isolated repro (AK full link with exact flags+DSO order passes; vcpkg-installed libmimalloc-secure exports mi_heap_malloc/mi_malloc WEAK DEFAULT)
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-4.20261107git1d07e31
- Overlay harfbuzz port: -Dwith_libstdcxx=true links the port's libharfbuzz with the C++ driver; triplet VCPKG_*_LINK_FLAGS never reached the port's meson link (11285527) and global -fno-exceptions breaks cpptrace (11285502)
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-3.20261107git1d07e31
- Fix vcpkg harfbuzz link via triplet VCPKG_*_LINK_FLAGS (RPM -fexceptions DW.ref needs libstdc++; env LDFLAGS is stripped by vcpkg, triplet flags reach ports; global -fno-exceptions rejected, it breaks cpptrace)
* Sun Nov 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-2.20261107git1d07e31
- Build vcpkg ports with -fno-exceptions (RPM -fexceptions emits DW.ref.__gxx_personality_v0 the ports link fails on, same fix as Fedora harfbuzz)
* Sat Nov 07 2026 Ackerman-00 <quietcraft@gmail.com> - 0.0.0-1.20261107git1d07e31
- Initial import; link vcpkg ports against libstdc++ (RPM -fexceptions emits DW.ref.__gxx_personality_v0)
