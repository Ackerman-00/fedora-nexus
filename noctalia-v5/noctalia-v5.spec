# These will be automatically populated by update.sh
%global commit          b347de8e1ae24e61b24e28c40173a9a19ff5fb90
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260611041124

Name:           noctalia-v5
Version:        5.0.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        A lightweight Wayland shell and bar built on Wayland + OpenGL ES

License:        MIT
Packager:       Ackerman-00 <quietcraft@gmail.com>
URL:            https://github.com/noctalia-dev/noctalia
Source0:        %{url}/archive/%{commit}/noctalia-%{shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  meson
BuildRequires:  gcc-c++
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
BuildRequires:  glib2-devel
BuildRequires:  polkit-devel
BuildRequires:  librsvg2-devel
BuildRequires:  libqalculate-devel
BuildRequires:  libxml2-devel
BuildRequires:  jemalloc-devel

Conflicts:      noctalia
Conflicts:      noctalia-bin
Conflicts:      noctalia-shell < 5.0.0
Provides:       noctalia-shell = %{version}-%{release}
Provides:       noctalia = %{version}-%{release}

%description
Noctalia is a lightweight Wayland shell and bar built directly on Wayland + OpenGL ES, 
with no Qt or GTK dependency. This package tracks the bleeding-edge main branch (formerly the v5 experimental branch).

%prep
# The upstream tarball now extracts to noctalia-%{commit} due to the repo rename
%autosetup -n noctalia-%{commit}

%build
# Force C++23 standard to fix the std::string_view 'contains' compiler error
# Add -Wno-unused-result to bypass strict GCC warnings, matching the Arch PKGBUILD
export CXXFLAGS="%{optflags} -std=c++23 -Wno-unused-result"
export CFLAGS="%{optflags}"

# Ensure we are building a highly optimized release binary without heavy debug symbols
%meson -Db_ndebug=true
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_bindir}/noctalia
%{_datadir}/noctalia/

%changelog
* Thu Jun 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260611041124gitb347de8-1
- Nightly sync with upstream main branch (Commit: b347de8)

* Wed Jun 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260610215446git6053948-1
- Nightly sync with upstream main branch (Commit: 6053948)

* Wed Jun 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260610183143git496d400-1
- Nightly sync with upstream main branch (Commit: 496d400)

* Wed Jun 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260610154539git1ff5b38-1
- Nightly sync with upstream main branch (Commit: 1ff5b38)

* Wed Jun 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260610142840gitef41c00-1
- Nightly sync with upstream main branch (Commit: ef41c00)

* Wed Jun 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260610043910git72b216c-1
- Nightly sync with upstream main branch (Commit: 72b216c)

* Mon Jun 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260608041201gitaa420b7-1
- Update spec to reflect upstream repository rename to 'noctalia' and branch merge
