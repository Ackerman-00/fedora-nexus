Name:           otr
Version:        0.2.6
Release:        5%{?dist}
Summary:        The Otr programming language toolchain

License:        MIT
URL:            https://git.pika-os.com/general-packages/otr
Source0:        https://git.pika-os.com/api/v1/repos/general-packages/otr/archive/v%{version}.tar.gz#/otr-v%{version}.tar.gz
# sha256: a1e227aa3e576b5fa1ef9cf372cc87b569501ddf6914f0ffd43399f62fa6c67a

# bundled toolchain libs stay private
%global __provides_exclude_from ^%{_libdir}/%{name}/.*$
%global __requires_exclude_from ^%{_libdir}/%{name}/.*$
# bundled LLVM/mold payload: foreign ELF, no build-id note to link
%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0
%global _build_id_links none
# the payload ships AArch64 archives and stubs the host strip cannot read
%global __strip /bin/true

ExclusiveArch:  x86_64
# bundled LLVM payload is upstream-built against glibc 2.44 (Fedora 45+)
Requires:       glibc >= 2.44

BuildRequires:  ca-certificates
BuildRequires:  curl
BuildRequires:  dpkg
BuildRequires:  gcc-c++
BuildRequires:  libzstd-devel
BuildRequires:  python3
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zlib-devel

%description
Self-contained toolchain for the Otr language: the compiler and language
server, the standard library, a bundled clang toolchain, the TPDE fast
backend and the mold linker. Otter Shell is built with it.

%prep
%autosetup -n otr
# host WAF refuses the default curl UA
sed -i 's|curl -sfL --retry 3|curl -sfL --retry 3 -A "Mozilla/5.0 (X11; Linux x86_64)"|' tools/bootstrap.sh
# upstream pins a Debian pool file Debian has removed (404)
sed -i -e 's|musl-dev_1\.2\.6-1_arm64\.deb|musl-dev_1.2.6-2_arm64.deb|' \
       -e 's|899296d0ec8fe7ce838ab3d56f63734fee79d9c86e134cb730400d33387f4437|585378c79d19c3bdd0e89f742e1ef67ceff089057d179ea95557444a3649c1dd|' \
       tools/libc/bundle.sh
# Fedora baseline: upstream ships x86-64-v3 code
sed -i 's/"x86_64_v3"/"baseline"/' build.otr
sed -i 's/-march=x86-64-v3/-march=x86-64/' tools/tpde/build.sh tools/llvm/bundle.sh

%build
sh tools/bootstrap.sh > /tmp/otr-boot-path
OTR_BOOT=$(cat /tmp/otr-boot-path)
"$OTR_BOOT" run build.otr -- install --out out --boot "$OTR_BOOT"
out/bin/otr version | grep -qx "otr %{version}"

%install
install -d -m 0755 %{buildroot}%{_libdir}/otr/bin %{buildroot}%{_libdir}/otr/lib %{buildroot}%{_libdir}/otr/libexec/otr %{buildroot}%{_bindir}
cp -a out/bin/otr %{buildroot}%{_libdir}/otr/bin/
cp -a out/lib/libotr-tpde.so out/lib/otr %{buildroot}%{_libdir}/otr/lib/
cp -a out/libexec/otr/mold %{buildroot}%{_libdir}/otr/libexec/otr/
echo "otr v%{version}" > %{buildroot}%{_libdir}/otr/COMMIT
mkdir -p %{buildroot}%{_bindir}
ln -s $(realpath --relative-to=%{buildroot}%{_bindir} %{buildroot}%{_libdir}/otr/bin/otr) %{buildroot}%{_bindir}/otr

%files
# upstream archive ships no LICENSE file; debian/copyright carries the grant
%license debian/copyright
%doc README.md
%{_bindir}/otr
%{_libdir}/otr/

%changelog
* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.2.6-5
- Keep the bundled LLVM libraries private: without the provides/requires
  exclusion they advertise libstdc++.so.6 and libz.so.1 as system-wide
  capabilities, so dnf installs this toolchain instead of the real Fedora
  libraries in the F45 and rawhide buildroots and rpmbuild -bs cannot start.

* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.2.6-4
- BuildRequires for what the bundled toolchain compiles: gcc-c++ supplies the C++
  standard headers the LLVM gold plugin needs, zlib-devel and libzstd-devel its -lz
  and -lzstd link line, dpkg its dpkg-deb for unpacking the libc and musl archives
- Build for the x86-64 baseline instead of upstream's x86-64-v3, so the shipped
  toolchain does not execute AVX2 instructions on pre-Haswell CPUs
- Repoint the AArch64 musl-dev download: upstream pins
  musl-dev_1.2.6-1_arm64.deb, which Debian has removed from its pool (404)
- Do not require a build-id note from the bundled payload: brp-strip terminates
  the build on the toolchain's own binaries and on the AArch64 libc stubs it ships
- Ship the license upstream actually provides: the release tarball has no LICENSE
  file, so `%license LICENSE` could never resolve - debian/copyright names the
  copyright holder and the MIT grant the spec declares
- Skip the strip brp scripts: the payload carries AArch64 musl archives and
  stubs, which the host strip cannot read ("Unable to recognise the architecture")
- Require glibc >= 2.44: the bundled LLVM payload is upstream-built against it, so
  the toolchain builds and runs on Fedora 45 and rawhide only (builds on 43/44 die
  in stage 1 with "mold: fatal: could not open plugin file: LLVMgold.so: version
  `GLIBC_2.44' not found")

* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.2.6-3
- Bootstrap download sends a browser User-Agent: the release-asset host answers
  403 to the default curl UA and 206 to this one, so the toolchain fetch failed

* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.2.6-2
- Use %autosetup -n otr: %build ran in the wrong directory and never found
  tools/bootstrap.sh ("sh tools/bootstrap.sh: No such file or directory")

* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.2.6-1
- Initial package
