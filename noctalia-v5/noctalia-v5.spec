# These will be automatically populated by update.sh
%global commit          80f7da63d05067600634aeb8a495e954d0db534e
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260428

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

Conflicts:      noctalia-shell < 5.0.0
Provides:       noctalia-shell = %{version}-%{release}

%description
Noctalia is a lightweight Wayland shell and bar built directly on Wayland + OpenGL ES, 
with no Qt or GTK dependency. This package tracks the experimental unreleased v5 git branch.

%prep
%autosetup -n noctalia-shell-%{commit}

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_bindir}/noctalia
%{_datadir}/noctalia/

%changelog
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
