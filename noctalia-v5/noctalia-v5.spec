# These will be automatically populated by update.sh
%global commit          2f28b9610cb4d2aee12c30b027e7be47ddb33d89
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260501123950

Name:           noctalia-v5
Version:        5.0.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        A lightweight Wayland shell and bar built on Wayland + OpenGL ES

License:        MIT
Packager:       Ackerman-00 <quietcraft@gmail.com>
URL:            https://github.com/noctalia-dev/noctalia-shell
Source0:        %{url}/archive/%{commit}/noctalia-shell-%{shortcommit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  just
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libEGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel
BuildRequires:  cairo-devel
BuildRequires:  pango-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  sdbus-cpp-devel
BuildRequires:  pipewire-devel
BuildRequires:  pam-devel
BuildRequires:  libcurl-devel
BuildRequires:  libwebp-devel
# New dependencies added upstream for polkit integration
BuildRequires:  glib2-devel
BuildRequires:  polkit-devel

Conflicts:      noctalia
Conflicts:      noctalia-bin
Conflicts:      noctalia-shell < 5.0.0
Provides:       noctalia-shell = %{version}-%{release}
Provides:       noctalia = %{version}-%{release}

%description
Noctalia is a lightweight Wayland shell and bar built directly on Wayland + OpenGL ES, 
with no Qt or GTK dependency. This package tracks the experimental unreleased v5 git branch.

%prep
%autosetup -n noctalia-shell-%{commit}

%build
# Let Fedora's meson macro handle LTO, optimization levels, and hardened flags automatically
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md CONFIG.md
%{_bindir}/noctalia
%{_datadir}/noctalia/

%changelog
* Fri May 01 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260501123950git2f28b96-1
- Nightly sync with upstream v5 branch (Commit: 2f28b96)

* Fri May 01 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260501052549gite9c40a2-1
- Nightly sync with upstream v5 branch (Commit: e9c40a2)

* Fri May 01 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260501034522gitc236689-1
- Nightly sync with upstream v5 branch (Commit: c236689)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430220932git9b96c7d-1
- Nightly sync with upstream v5 branch (Commit: 9b96c7d)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430185337gitfad660f-1
- Nightly sync with upstream v5 branch (Commit: fad660f)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430141248git829e73d-1
- Nightly sync with upstream v5 branch (Commit: 829e73d)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430140220git310813a-1
- Nightly sync with upstream v5 branch (Commit: 310813a)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430122436git95e36b0-1
- Nightly sync with upstream v5 branch (Commit: 95e36b0)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430114608git4e30cc8-1
- Nightly sync with upstream v5 branch (Commit: 4e30cc8)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430055310git5c2d9ea-1
- Nightly sync with upstream v5 branch (Commit: 5c2d9ea)

* Thu Apr 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260430021745gitf5e19f0-1
- Nightly sync with upstream v5 branch (Commit: f5e19f0)

* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429221730git2931042-1
- Nightly sync with upstream v5 branch (Commit: 2931042)

* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429210104gitc094762-1
- Nightly sync with upstream v5 branch (Commit: c094762)

* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429192923git6e6a45a-1
- Nightly sync with upstream v5 branch (Commit: 6e6a45a)

* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429174118git24abc9a-1
- Nightly sync with upstream v5 branch (Commit: 24abc9a)

* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429140144git660c232-1
- Nightly sync with upstream v5 branch (Commit: 660c232)

* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429125405gitfad804a-1
- Nightly sync with upstream v5 branch (Commit: fad804a)
- Added glib2-devel and polkit-devel for new polkit-agent-1 dependency
