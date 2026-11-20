%global zsver    0.13.50
%global geo      0.13.45
%global utils    0.13.46
%global conf     0.13.14
%global render   0.13.45
%global wayland  0.13.52
%global theme    0.13.50
%global ui       0.13.50
%global desktop  0.13.51

%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0
%global _build_id_links none

Name:           zoolander-settings-git
Version:        %{zsver}
Release:        1%{?dist}
Summary:        Graphical settings app for the Zoolander compositor

License:        MIT
URL:            https://docs.otter-shell.org/zoolander/configuring/settings-app.md
Provides:       zoolander-settings = %{version}-%{release}
Conflicts:      zoolander-settings
Source0:        https://git.pika-os.com/api/v1/repos/otter-shell/zoolander-settings/archive/v%{zsver}.tar.gz#/zoolander-settings-v%{zsver}.tar.gz
# sha256: 74d4ea08a9b5a99310a60dc8fb5ab46be5f1506ca8a137456fdff57c09ed9f17
Source1:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-geo/archive/v%{geo}.tar.gz#/otter-geo-v%{geo}.tar.gz
# sha256: 306b9fbe64e6b9e7d06d80dd358453d107d1298274a216532b73dadf77f84ddd
Source2:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-utils/archive/v%{utils}.tar.gz#/otter-utils-v%{utils}.tar.gz
# sha256: c2668c1a6aefd49691686ed385636d49d2646ca46ae316254a63c5e294f54f73
Source3:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-conf/archive/v%{conf}.tar.gz#/otter-conf-v%{conf}.tar.gz
# sha256: 92b7141c65a2a9fea94cb3b3107c4de6392a6011df119dacb81da84760227c82
Source4:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-render/archive/v%{render}.tar.gz#/otter-render-v%{render}.tar.gz
# sha256: 3c8cd8afc059e05a640b46ecff0ff8c49e80370f6997e8e49422e74e977ce36e
Source5:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-wayland/archive/v%{wayland}.tar.gz#/otter-wayland-v%{wayland}.tar.gz
# sha256: a175c88d497ab124f501757b2b1700c792faadfb53ca9818d4a60911a0729d60
Source6:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-theme/archive/v%{theme}.tar.gz#/otter-theme-v%{theme}.tar.gz
# sha256: 02f9244c7d6ba25ac3ee495e96c705166f7e5c2355b28244d228992a2423c6d7
Source7:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-ui/archive/v%{ui}.tar.gz#/otter-ui-v%{ui}.tar.gz
# sha256: 96d040e1c3562488994ae70b99b6524fcf56330e4ea3439bc840bc7cb8f74383
Source8:        https://git.pika-os.com/api/v1/repos/otter-shell/otter-desktop/archive/v%{desktop}.tar.gz#/otter-desktop-v%{desktop}.tar.gz
# sha256: f9ac5b1ca4baba16fcb19fdcaa113574bee38155dcc82245b7f05faff4f8512b
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
* Fri Nov 20 2026 Ackerman-00 <no-reply> - 0.13.50-1
- Update the Otter sources to their newest tags (settings 0.13.50,
  geo 0.13.45, utils 0.13.46, conf 0.13.14, render 0.13.45,
  wayland 0.13.52, theme 0.13.50, ui 0.13.50, desktop 0.13.51;
  sha256 of every archive verified)
