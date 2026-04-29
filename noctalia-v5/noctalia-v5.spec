# These will be automatically populated by update.sh
%global commit          660c2321d11fd370240cff19b5db59548000dadd
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260429140144

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
* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429140144git660c232-1
- Nightly sync with upstream v5 branch (Commit: 660c232)

* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429125405gitfad804a-1
- Nightly sync with upstream v5 branch (Commit: fad804a)
- Added glib2-devel and polkit-devel for new polkit-agent-1 dependency
