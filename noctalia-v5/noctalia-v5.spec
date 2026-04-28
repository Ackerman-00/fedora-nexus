# These will be automatically populated by update.sh
%global commit          a240c194368a261eb540403c6ef5619343965586
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260428191225

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
* Tue Apr 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260428191225gita240c19-1
- Nightly sync with upstream v5 branch (Commit: a240c19)

* Tue Apr 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260428gitbab7834-1
- Nightly sync with upstream v5 branch (Commit: bab7834)

* Tue Apr 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260428gitc096e3a-1
- Nightly sync with upstream v5 branch (Commit: c096e3a)

* Tue Apr 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260428git7b980bd-1
- Nightly sync with upstream v5 branch (Commit: 7b980bd)

* Tue Apr 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260428gitdad32db-1
- Nightly sync with upstream v5 branch (Commit: dad32db)

* Tue Apr 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260428git0018c88-1
- Nightly sync with upstream v5 branch (Commit: 0018c88)
- Added CONFIG.md to documentation per upstream PKGBUILD

* Tue Apr 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260428git80f7da6-1
- Nightly sync with upstream v5 branch (Commit: 80f7da6)

* Mon Apr 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260427git6c26b03-1
- Nightly sync with upstream v5 branch (Commit: 6c26b03)

* Mon Apr 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260427gitff8c4a3-1
- Nightly sync with upstream v5 branch (Commit: ff8c4a3)

* Mon Apr 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260427git95c0492-1
- Nightly sync with upstream v5 branch (Commit: 95c0492)

* Mon Apr 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0-1
- Initial fedora-nexus nightly packaging for v5 branch
- Added assets directory to files list per upstream requirements
