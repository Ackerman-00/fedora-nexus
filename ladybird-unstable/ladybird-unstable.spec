%global debug_package %{nil}
%global _lto_cflags %{nil}
# Bundled vcpkg/shared libs stay private.
%global __requires_exclude_from ^/opt/ladybird/.*$
%global __provides_exclude_from ^/opt/ladybird/.*$
%global __brp_mangle_shebangs_exclude_from ^/opt/ladybird/.*$
%global commit         c87319cd8b89404aff26d791fb6a2c8007fe1b65

Name:           ladybird-unstable
Version:        0.0.0
Release:        44.20261124gitc87319c%{?dist}
Summary:        Truly independent web browser (git master; unstable)
License:        BSD-2-Clause
URL:            https://ladybird.org
Source0:        https://github.com/LadybirdBrowser/ladybird/archive/%{commit}.tar.gz
Source1:        harfbuzz-overlay-portfile.cmake
Source2:        harfbuzz-overlay-vcpkg.json
Source3:        harfbuzz-overlay-fix-win32-build.patch
Source4:        harfbuzz-overlay-config.cmake.in
Source5:        harfbuzz-overlay-usage
Source6:        check-bundled-libs.py
# F43/F44 carry libicu 77 only; a matched 78 build is bundled there (F45+ uses the distro one)
%if 0%{?fedora} < 45
# sha256: f9b6f4a419a91f6f9933718ea20dc0f146472bf521f3b090f885a06564846ee3
Source7:        https://github.com/unicode-org/icu/archive/refs/tags/release-78.3.tar.gz
%endif

Requires:       libQt6Core.so.6()(64bit)
Requires:       libQt6Gui.so.6()(64bit)
Requires:       libQt6Positioning.so.6()(64bit)
Requires:       libQt6Widgets.so.6()(64bit)
Requires:       libdrm.so.2()(64bit)
%if 0%{?fedora} >= 45
Requires:       libicudata.so.78()(64bit)
Requires:       libicui18n.so.78()(64bit)
Requires:       libicuuc.so.78()(64bit)
%endif
Requires:       libgio-2.0.so.0()(64bit)
Requires:       libgobject-2.0.so.0()(64bit)
Requires:       libncurses.so.6()(64bit)
Requires:       libpulse.so.0()(64bit)
Requires:       libtinfo.so.6()(64bit)
Requires:       libvulkan.so.1()(64bit)
Requires:       libwayland-client.so.0()(64bit)
Requires:       libxcb-icccm.so.4()(64bit)
Requires:       libxcb.so.1()(64bit)
Requires:       hicolor-icon-theme
Recommends:     qt6-qtwayland
Recommends:     mesa-vulkan-drivers

BuildRequires:  autoconf-archive
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  binutils
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
BuildRequires:  patch
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
%if 0%{?fedora} < 45
BuildRequires:  make
%endif

%description
Ladybird browser built from the git master branch (unstable).

%prep
%autosetup -n ladybird-%{commit}
# cargo >= 1.100 nests build-script output as <crate>/<hash>/run/root-output; upstream glob still matches the old <crate>-<hash>/root-output
sed -i 's|${CRATE_NAME}-\*/root-output")|${CRATE_NAME}-*/root-output" "${CARGO_BUILD_SCRIPT_DIR}/${CRATE_NAME}/*/run/root-output")|' Meta/CMake/sync_rust_ffi_header.cmake
grep -q 'run/root-output' Meta/CMake/sync_rust_ffi_header.cmake
%if 0%{?fedora} < 45
tar -xzf %{SOURCE7} && mv icu-release-78.3 icu
%endif
# harfbuzz port: C driver link under -fexceptions needs libstdc++ (DW.ref personality); overlay adds -Dwith_libstdcxx=true
mkdir -p Meta/CMake/vcpkg/overlay-ports/harfbuzz
cp -p %{SOURCE1} Meta/CMake/vcpkg/overlay-ports/harfbuzz/portfile.cmake
cp -p %{SOURCE2} Meta/CMake/vcpkg/overlay-ports/harfbuzz/vcpkg.json
cp -p %{SOURCE3} Meta/CMake/vcpkg/overlay-ports/harfbuzz/fix-win32-build.patch
cp -p %{SOURCE4} Meta/CMake/vcpkg/overlay-ports/harfbuzz/harfbuzzConfig.cmake.in
cp -p %{SOURCE5} Meta/CMake/vcpkg/overlay-ports/harfbuzz/usage

%build
export VCPKG_FORCE_SYSTEM_BINARIES=1
python3 Meta/ladybird.py vcpkg --preset Release
# x86-64-v2: upstream defaults to -march=native, which bakes the builder's AVX-512 into published code
cmake --preset Release -S . -B Build/release -DBUILD_TESTING=OFF -DENABLE_INSTALL_FREEDESKTOP_FILES=OFF -DCMAKE_INSTALL_PREFIX=/opt/ladybird -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=OFF -DLADYBIRD_BASELINE_CPU_TARGET=ON
grep -q -- '-march=x86-64-v2' Build/release/build.ninja || {
  echo 'ERROR: x86-64-v2 baseline missing from the build' >&2
  exit 1
}
if grep -q -- '-march=native' Build/release/build.ninja; then
  echo 'ERROR: -march=native leaked into the build' >&2
  exit 1
fi
cmake --build Build/release --parallel %{?_smp_build_ncpus}
%if 0%{?fedora} < 45
cd icu/icu4c/source
export CFLAGS="%{optflags}" CXXFLAGS="%{optflags}"
./runConfigureICU Linux --prefix=/opt/ladybird --libdir=/opt/ladybird/lib64 --disable-static --disable-tests --disable-samples
make -j%{?_smp_build_ncpus}
cd -
%endif

%install
DESTDIR=%{buildroot} cmake --install Build/release --component ladybird_Runtime
DESTDIR=%{buildroot} cmake --install Build/release --component Lagom_Runtime
DESTDIR=%{buildroot} cmake --install Build/release --component ladybird_SystemIntegration
mkdir -p %{buildroot}/opt/ladybird/lib64
VCPKG_LIBS=$(find Build/release/vcpkg_installed/*-linux-dynamic/lib -maxdepth 1 -name '*.so*' -print)
[ -n "$VCPKG_LIBS" ] || { echo "FATAL: no vcpkg shared libraries found to bundle" >&2; exit 1; }
cp -a $VCPKG_LIBS %{buildroot}/opt/ladybird/lib64/
chmod -R u+w %{buildroot}/opt/ladybird
%if 0%{?fedora} < 45
cp -a icu/icu4c/source/lib/libicudata.so.78.3 icu/icu4c/source/lib/libicuuc.so.78.3 icu/icu4c/source/lib/libicui18n.so.78.3 %{buildroot}/opt/ladybird/lib64/
ln -sf libicudata.so.78.3 %{buildroot}/opt/ladybird/lib64/libicudata.so.78
ln -sf libicuuc.so.78.3 %{buildroot}/opt/ladybird/lib64/libicuuc.so.78
ln -sf libicui18n.so.78.3 %{buildroot}/opt/ladybird/lib64/libicui18n.so.78
# $ORIGIN only: an absolute runpath trips check-rpaths 0002, an empty one trips 0010
for lib in libicudata libicuuc libicui18n; do
  patchelf --set-rpath '$ORIGIN' %{buildroot}/opt/ladybird/lib64/$lib.so.78.3
  readelf -d %{buildroot}/opt/ladybird/lib64/$lib.so.78.3 | grep -qE '(RUNPATH|RPATH).*\[\$ORIGIN\]' \
    || { echo "FATAL: $lib.so.78.3 has no \$ORIGIN runpath, the loader cannot resolve its ICU siblings" >&2; exit 1; }
done
if readelf -d %{buildroot}/opt/ladybird/lib64/*.so.78.3 | grep -qE '(RUNPATH|RPATH).*\[/'; then
  echo 'FATAL: absolute RUNPATH on a bundled ICU library (rpm check-rpaths rejects it)' >&2
  exit 1
fi
%else
# system icu: vcpkg's patchelf step leaves libicudata with an empty dynamic section, and helpers re-exec without LD_LIBRARY_PATH
rm -f %{buildroot}/opt/ladybird/lib64/libicu*.so*
%endif
python3 %{SOURCE6} %{buildroot}/opt/ladybird/lib64

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license LICENSE
%if 0%{?fedora} < 45
%license icu/icu4c/LICENSE
%endif
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
* Tue Nov 24 2026 Ackerman-00 <no-reply> - 0.0.0-44.20261124gitc87319c
- Refresh snapshot 5d7cc30 -> c87319c (upstream commit dated 2026-11-24T04:33:28Z)

* Mon Nov 23 2026 Ackerman-00 <no-reply> - 0.0.0-43.20261123git5d7cc30
- Refresh snapshot 2fa7d18 -> 5d7cc30 (upstream commit dated 2026-11-23T03:10:24Z)

* Sun Nov 22 2026 Ackerman-00 <no-reply> - 0.0.0-42.20261122git2fa7d18
- Refresh snapshot ae95e25 -> 2fa7d18 (upstream commit dated 2026-11-22T21:24:08Z)

* Sun Nov 22 2026 Ackerman-00 <no-reply> - 0.0.0-41.20261122gitae95e25
- Refresh snapshot 1849944 -> ae95e25 (upstream commit dated 2026-11-22T04:27:29Z)

* Sat Nov 21 2026 Ackerman-00 <no-reply> - 0.0.0-40.20261121git1849944
- Refresh snapshot 48d36b1 -> 1849944 (upstream commit dated 2026-11-21T21:13:20Z)

* Sat Nov 21 2026 Ackerman-00 <no-reply> - 0.0.0-39.20261121git48d36b1
- Refresh snapshot 9932619 -> 48d36b1 (upstream commit dated 2026-11-21T01:33:26Z)

* Fri Nov 20 2026 Ackerman-00 <no-reply> - 0.0.0-38.20261120git9932619
- Refresh snapshot 1f052f2 -> 9932619 (upstream commit dated 2026-11-20T04:21:19Z)

* Thu Nov 19 2026 Ackerman-00 <no-reply> - 0.0.0-37.20261119git1f052f2
- Fix CPU baseline after upstream renamed the option: ENABLE_CI_BASELINE_CPU
  is gone at 1f052f2 (Meta/CMake/cmake_options.cmake declares
  LADYBIRD_BASELINE_CPU_TARGET), so -march=native came back and the guard
  failed build 11358583 on all four chroots
- Guard now also requires -march=x86-64-v2 in build.ninja, so a silently
  ignored option fails the build instead of shipping builder-tuned code

* Thu Nov 19 2026 Ackerman-00 <no-reply> - 0.0.0-36.20261119git1f052f2
- Refresh snapshot f2849cf -> 1f052f2 (upstream commit dated 2026-11-19T03:59:51Z)

* Wed Nov 18 2026 Ackerman-00 <no-reply> - 0.0.0-35.20261118gitf2849cf
- Refresh snapshot d9d53a0 -> f2849cf (upstream commit dated 2026-11-18T05:35:21Z)

* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.0.0-34.20261117gitd9d53a0
- Refresh snapshot ab5aaba -> d9d53a0 (upstream commit dated 2026-11-17T03:55:20Z)

* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.0.0-33.20261116gitab5aaba
- Fix cargo 1.100 build layout: widen sync_rust_ffi_header.cmake glob to
  <crate>/*/run/root-output (COPR rawhide builds 11331679 and 11332377 failed with
  "Failed to find RustFFI.h in Cargo build output for libtextcodec_rust")

* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.0.0-32.20261116gitab5aaba
- Refresh snapshot eb909f8 -> ab5aaba (upstream commit dated 2026-11-16T01:14:06Z); build-system
  files reviewed before the bump, COPR build verified after it

* Sun Nov 15 2026 Ackerman-00 <no-reply> - 0.0.0-31.20261115giteb909f8
- Refresh snapshot b872e60 -> eb909f8 (upstream commit dated 2026-11-15T20:09:38Z); build-system
  files reviewed before the bump, COPR build verified after it

* Sun Nov 15 2026 Ackerman-00 <no-reply> - 0.0.0-30.20261115gitb872e60
- Refresh snapshot e0b1146 -> b872e60 (upstream commit dated 2026-11-15T03:05:27Z); build-system
  files reviewed before the bump, COPR build verified after it

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 0.0.0-29.20261114gite0b1146
- Refresh snapshot fb7c852 -> e0b1146 (upstream commit dated 2026-11-14T20:15:01Z); build-system
  files reviewed before the bump, COPR build verified after it

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 0.0.0-28.20261114gitfb7c852
- Move the in-app updater strip into %install

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 0.0.0-27.20261114gitfb7c852
- Refresh snapshot 7824369 -> fb7c852 (upstream commit dated 2026-11-14T01:13:43Z); build-system
  files reviewed before the bump, COPR build verified after it

* Fri Nov 13 2026 Ackerman-00 <no-reply> - 0.0.0-26.20261113git7824369
- Refresh snapshot b1f1cd2 -> 7824369 (upstream commit dated 2026-11-13T00:55:41Z); build-system
  files reviewed before the bump, COPR build verified after it

* Thu Nov 12 2026 Ackerman-00 <no-reply> - 0.0.0-25.20261112gitb1f1cd2
- Refresh snapshot 3d43356 -> b1f1cd2 (upstream commit dated 2026-11-12T02:02:58Z); build-system
  files reviewed before the bump, COPR build verified after it

* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.0.0-24.20261111git3d43356
- Refresh snapshot 28ba84f -> 3d43356 (upstream commit dated 2026-11-11T22:34:36Z); build-system
  files reviewed before the bump, COPR build verified after it

* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.0.0-23.20261111git28ba84f
- Require hicolor-icon-theme: the package installs a scalable hicolor icon, and the
  other 28 icon-shipping specs here carry that Requires. Folded into this rebuild so
  the icon-dir fix and the changelog-scriptlet fix ship together.
* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.0.0-22.20261111git28ba84f
- Move the -21 entry below the %changelog tag and bump the revision so users get it:
  update.sh inserted entries above the tag, so the shipped %postun scriptlet carried
  three junk shell lines and the changelog lost that entry. update.sh now inserts after
  the tag, like the other packages do.
* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.0.0-21.20261111git28ba84f
- Refresh snapshot 6a488f6 -> 28ba84f (upstream commit dated 2026-11-11T02:54:44Z); build-system
  files reviewed before the bump, COPR build verified after it
* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.0.0-20.20261110git6a488f6
- F43/F44 only: set the bundled ICU runpath with patchelf after the copy instead of
  through ICU's LDFLAGS. -19 failed %install on f44 with
  "file '/opt/ladybird/lib64/libicudata.so.78.3' contains an empty runpath in []"
  (rpm check-rpaths 0010): ICU's data library link line re-expands the variable, so
  the quoted $ORIGIN arrived empty even though libicuuc/libicui18n kept theirs. The
  gate now asserts $ORIGIN on all three bundled ICU libraries, which also rejects an
  empty runpath.
* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.0.0-19.20261110git6a488f6
- F43/F44 only: link the bundled ICU with a relative $ORIGIN runpath instead of
  configure --enable-rpath. -18 failed %install on f43/f44 with
  "file '/opt/ladybird/lib64/libicudata.so.78.3' contains an invalid runpath
  '/opt/ladybird/lib64' in [$ORIGIN:/opt/ladybird/lib64]" (rpm check-rpaths 0002,
  absolute path); the build gate now asserts $ORIGIN and rejects an absolute
  runpath on a bundled ICU library.
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.0.0-18.20261110git6a488f6
- F43/F44 only: build the bundled ICU 78.3 with --enable-rpath and fail the build
  if a bundled ICU library has no libdir rpath. libicuuc NEEDs libicudata from the
  same directory but carried no RUNPATH, and the executable's RUNPATH is not
  transitive, so 0.0.0-16 died at launch with "libicudata.so.78: cannot open shared
  object file" (F45+ uses the distro libicu and was unaffected)
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.0.0-17.20261110git6a488f6
- Refresh snapshot 03ada6d -> 6a488f6 (115 commits upstream to 2026-11-10T16:21Z;
  top-level CMakeLists and compile_options.cmake unchanged, vcpkg builtin-baseline
  unchanged, only the vcpkg icu port moved 78.3#2 -> 78.3#3, so the harfbuzz
  overlay, the system-icu split and the x86-64-v2 gate carry over unchanged)
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.0.0-16.20261110git03ada6d
- F43/F44 only: the Fedora libicu there is 77, so the system-icu Requires
  made 0.0.0-15 uninstallable (dnf silently fell back to -14). Build Unicode
  ICU 78.3 in the spec and bundle it in both chroots; F45+ keeps the distro
  libicu 78. The bundled copy never sees vcpkg's patchelf, so the PT_DYNAMIC
  corruption cannot reach it, and the PT_DYNAMIC gate still checks it.

* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.0.0-15.20261110git03ada6d
- Use Fedora's icu instead of the bundled copy and gate every bundled library's PT_DYNAMIC: vcpkg's patchelf rewrite left libicudata's dynamic section 0x38 out of step with its PT_LOAD, so ld.so read DT_NULL there and the first process to relocate it died in elf_dynamic_do_Rela (Hub segfaulted, then "Failed to receive message_id: 2" / "Failed to connect to RequestServer" from every helper, which re-exec with a sanitised environment and so never saw the LD_LIBRARY_PATH workaround)
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.0.0-14.20261110git03ada6d
- Build for x86-64-v2 (upstream's ENABLE_CI_BASELINE_CPU) instead of -march=native, and fail the build if native leaks back in: the COPR builder has AVX-512, so the published libraries carried vrndscalesd and every launch died with SIGILL (ILL_ILLOPN) inside __llvm_libc_ladybird::math::pow during liblagom-gfx's static initializers, before main(), on any CPU without AVX-512 (Ryzen 5 5600G repro)
* Mon Nov 09 2026 Ackerman-00 <no-reply> - 0.0.0-13.20261109git03ada6d
- Rebuild the bundled libicudata from its own icudt78_dat blob and fail the build on any bundled library the loader cannot open: vcpkg's rpath rewrite left libicudata's PT_DYNAMIC one program header out of step, so every helper (RequestServer, WebContent, ...) segfaulted in ld.so before main() and the browser died with "Failed to connect to RequestServer"
* Mon Nov 09 2026 Ackerman-00 <no-reply> - 0.0.0-12.20261109git03ada6d
- Refresh snapshot 1d07e31 -> 03ada6d (426 commits upstream to 2026-11-09T14:56Z; vcpkg.json and top-level CMakeLists byte-identical to 1d07e31, builtin-baseline unchanged at 20ceb8adb, so the harfbuzz overlay and LTO escape hatch carry over unchanged)
* Mon Nov 09 2026 Ackerman-00 <no-reply> - 0.0.0-11.20261109git1d07e31
- Declare the runtime system Dependencies the bundled tree cannot carry (/opt/ladybird is excluded from autorequires): Qt6 core/gui/positioning/widgets, glib2, libdrm, pulseaudio-libs, ncurses, vulkan-loader, libwayland-client, xcb + icccm
- Recommend qt6-qtwayland (wayland platform plugin, this repo's compositor stack) and mesa-vulkan-drivers (software Vulkan, headless/CI)
* Mon Nov 09 2026 Ackerman-00 <no-reply> - 0.0.0-10.20261109git1d07e31
- Restore the missing %changelog entry for the fleet-rebuild Release; no upstream change (pin still 1d07e31)
* Mon Nov 09 2026 Ackerman-00 <no-reply> - 0.0.0-9.20261107git1d07e31
- VCPKG_FORCE_SYSTEM_BINARIES=1: vcpkg insisted on downloading its pinned cmake 4.4.3 from github.com (Kitware/CMake releases) and COPR's network path got 504/504 on it (build 11290048; the same github.com flakiness hit two other downloads this run); Fedora ships cmake 4.3.0, so use the system toolchain (cmake/ninja-build/git/patch; patch added to BuildRequires) instead of a per-build ~50MB download that can hard-fail the whole browser
* Mon Nov 09 2026 Ackerman-00 <no-reply> - 0.0.0-8.20261107git1d07e31
- Bundle the vcpkg shared libraries into /opt/ladybird/lib64 (RUNPATH says ../lib64); the previous cp into /opt/ladybird/lib/ failed silently against a nonexistent directory ("Not a directory", rpmbuild exit 0), so 0.0.0-7 shipped without libskia/libzmij/libavcodec-ladybird and dnf refused to install it
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0.0.0-7.20261107git1d07e31
- Fix COPR timeout (18000s, build 11287677 died at 3536/3536): build with -DBUILD_TESTING=OFF so test targets are never built, install upstream's Linux package layout (prefix /opt/ladybird, ladybird_Runtime+Lagom_Runtime+ladybird_SystemIntegration components), bundle the vcpkg shared libraries into /opt/ladybird/lib, and set -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=OFF so installed RUNPATHs are $ORIGIN-based; add lld (picked automatically by ladybird next to gcc for faster links)
- Spec previously installed to the cmake default prefix (/usr/local) with no DESTDIR and shipped only /usr/bin/Ladybird and share/ladybird; the real layout is /opt/ladybird plus /usr/bin/ladybird and freedesktop files (found by reading UI/cmake/InstallRules.cmake in Source0)
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0.0.0-6.20261107git1d07e31
- Drop LTO (_lto_cflags %{nil}): AK final link fails in COPR mock with undefined mi_heap_malloc/mi_malloc in ltrans partitions; deterministic across two builds (11285658, 11285927) while the same link passes in an isolated repro - partition-assignment-dependent weak-DSO resolution under LTO
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0.0.0-5.20261107git1d07e31
- Rebuild after 11285658 failed at the AK link (undefined mi_* refs); failure not reproducible in isolated repro (AK full link with exact flags+DSO order passes; vcpkg-installed libmimalloc-secure exports mi_heap_malloc/mi_malloc WEAK DEFAULT)
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0.0.0-4.20261107git1d07e31
- Overlay harfbuzz port: -Dwith_libstdcxx=true links the port's libharfbuzz with the C++ driver; triplet VCPKG_*_LINK_FLAGS never reached the port's meson link (11285527) and global -fno-exceptions breaks cpptrace (11285502)
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0.0.0-3.20261107git1d07e31
- Fix vcpkg harfbuzz link via triplet VCPKG_*_LINK_FLAGS (RPM -fexceptions DW.ref needs libstdc++; env LDFLAGS is stripped by vcpkg, triplet flags reach ports; global -fno-exceptions rejected, it breaks cpptrace)
* Sun Nov 08 2026 Ackerman-00 <no-reply> - 0.0.0-2.20261107git1d07e31
- Build vcpkg ports with -fno-exceptions (RPM -fexceptions emits DW.ref.__gxx_personality_v0 the ports link fails on, same fix as Fedora harfbuzz)
* Sat Nov 07 2026 Ackerman-00 <no-reply> - 0.0.0-1.20261107git1d07e31
- Initial import; link vcpkg ports against libstdc++ (RPM -fexceptions emits DW.ref.__gxx_personality_v0)
