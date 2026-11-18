%global zsver     0.13.47
%global geo       0.13.45
%global utils     0.13.46
%global conf      0.13.14
%global render    0.13.45
%global wayland   0.13.45
%global theme     0.13.35
%global ui        0.13.45
%global desktop   0.13.44

%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0
%global _build_id_links none

Name:           zoolander-settings-git
Version:        %{zsver}
Release:        8%{?dist}
Summary:        Graphical settings app for the Zoolander compositor

License:        MIT
URL:            https://docs.otter-shell.org/zoolander/configuring/settings-app.md
Provides:       zoolander-settings = %{version}-%{release}
Conflicts:      zoolander-settings
Source0:        https://git.pika-os.com/api/v1/repos/otter-shell/zoolander-settings/archive/v%{zsver}.tar.gz#/zoolander-settings-v%{zsver}.tar.gz
# sha256: 2407dac55bc0c20ed9f6d82e22f374f09d5f45afe35b276556108439d70ff080
Source1:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-geo/archive/v%{geo}.tar.gz#/otter-geo-v%{geo}.tar.gz
# sha256: 306b9fbe64e6b9e7d06d80dd358453d107d1298274a216532b73dadf77f84ddd
Source2:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-utils/archive/v%{utils}.tar.gz#/otter-utils-v%{utils}.tar.gz
# sha256: c2668c1a6aefd49691686ed385636d49d2646ca46ae316254a63c5e294f54f73
Source3:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-conf/archive/v%{conf}.tar.gz#/otter-conf-v%{conf}.tar.gz
# sha256: 92b7141c65a2a9fea94cb3b3107c4de6392a6011df119dacb81da84760227c82
Source4:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-render/archive/v%{render}.tar.gz#/otter-render-v%{render}.tar.gz
# sha256: 3c8cd8afc059e05a640b46ecff0ff8c49e80370f6997e8e49422e74e977ce36e
Source5:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-wayland/archive/v%{wayland}.tar.gz#/otter-wayland-v%{wayland}.tar.gz
# sha256: 16129c52704191335fee19fcf3f54430930e7376ec8e34f81e4c4585ca5d4f66
Source6:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-theme/archive/v%{theme}.tar.gz#/otter-theme-v%{theme}.tar.gz
# sha256: fd28e9012c0c417f522bbf7654acf76d735dc8884148d0dd509205858eff26cf
Source7:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-ui/archive/v%{ui}.tar.gz#/otter-ui-v%{ui}.tar.gz
# sha256: 8595b2b2aebbae055c012fce60fd9299bd41e2de05c55d00e8790254ce585e70
Source8:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-desktop/archive/v%{desktop}.tar.gz#/otter-desktop-v%{desktop}.tar.gz
Source9:        LICENSE
# sha256: f115a091c7a4554849e153c0afa5c4ecf74de59ae017645263b76c1fe74df1c7

ExclusiveArch:  x86_64 aarch64

BuildRequires:  otr
BuildRequires:  gcc
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(fribidi)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  zlib-devel
BuildRequires:  wayland-devel

Requires:       zoolander-git
Requires:       rsms-inter-fonts

%description
The graphical settings app for Zoolander, built on the Otr toolchain. It edits
the compositor's Lua config in place, validates it with a running Zoolander and
reloads on Apply. The Otter library sources are vendored into this package and
statically linked; no separate sibling packages are needed.

%prep
# Sibling source layout
tar -xzf %{SOURCE0}
tar -xzf %{SOURCE1}
tar -xzf %{SOURCE2}
tar -xzf %{SOURCE3}
tar -xzf %{SOURCE4}
tar -xzf %{SOURCE5}
tar -xzf %{SOURCE6}
tar -xzf %{SOURCE7}
tar -xzf %{SOURCE8}

%build
cd zoolander-settings
# Baseline CPU
DESTDIR=%{_builddir}/staging OTR_CPU=baseline otr run otr/build.otr -- install \
    --prefix %{_prefix} --cpu baseline

%install
cp -a %{_builddir}/staging/usr %{buildroot}/
install -D -m 0644 %{SOURCE9} %{buildroot}%{_licensedir}/zoolander-settings-git/LICENSE

%files
%license %{_licensedir}/zoolander-settings-git/LICENSE
%{_bindir}/zoolander-settings
%{_datadir}/applications/
%{_datadir}/icons/hicolor/

%post
if [ "$1" -eq 1 ]; then
    echo
    echo "  zoolander-settings installed."
    echo "  Documentation: https://docs.otter-shell.org/zoolander/overview"
    echo
fi

%changelog
* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-8
- Require rsms-inter-fonts: the app's default font family is Inter; without it
  zoolander-settings exits with NoFontAvailable (verified in VM).


* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-7
- Ship the vendored LICENSE as Source9 and install from %{SOURCE9}; the
  previous relative path did not resolve at %install time (the tarball ships
  no license file) - COPR build 11337071/11337077 failed

* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-6
- Vendor the Otter project's MIT license text (identical to the LICENSE files
  shipped by otter-utils and otter-render): zoolander-settings ships no LICENSE
  file upstream, and the %license declaration crashed the build with
  "File not found" (COPR build 11337071)

* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-5
- Install the LICENSE file: the %license macro expands to a path that must be
  created by %install or %files fails ("File not found" - COPR build 11337009)

* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-4
- Stage the otr install into %{_builddir}/staging and copy into %{buildroot}
  from %install: rpm wipes %{buildroot} before the %install script, so the
  tree staged by %build never survived to %files (COPR build 11336995 failed:
  "File not found: .../usr/bin/zoolander-settings")

* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-3
- Give every Source a unique #/filename: all nine gitea archive URLs end in
  v<version>.tar.gz and four of them share v0.13.45, so they downloaded to one
  dest file (last-write-wins) and the ../../ sibling deps in otr.toml could not
  resolve (COPR build 11336940 failed on fedora-43/45/rawhide)

* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-2
- Extract sources with plain tar so the top-level dirs are siblings directly
  in BUILD; -1 used autosetup -c which nested them one level too deep and the
  ../../ relative deps in otr.toml could not resolve.

* Tue Nov 17 2026 Ackerman-00 <no-reply> - 0.13.47-1
- Initial package. Vendors the 9 pinned Otter library sources (from
  otter-zenith/pins.json) and links them statically, so a single RPM provides
  zoolander-settings without separate sibling packages.
- Requires zoolander; prints the docs URL in %post.
