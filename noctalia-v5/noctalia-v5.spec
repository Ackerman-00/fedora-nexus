# These will be automatically populated by update.sh
%global commit          f3e21025133bddac470fbf45e677da73be42af98
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260503095250

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
* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503095250gitf3e2102-1
- Nightly sync with upstream v5 branch (Commit: f3e2102)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503091322gitc8c5830-1
- Nightly sync with upstream v5 branch (Commit: c8c5830)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503060255gitad53834-1
- Nightly sync with upstream v5 branch (Commit: ad53834)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503022752gitebddec7-1
- Nightly sync with upstream v5 branch (Commit: ebddec7)

* Sat May 02 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260502224029git035ca10-1
- Nightly sync with upstream v5 branch (Commit: 035ca10)


* Wed Apr 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260429125405gitfad804a-1
- Added glib2-devel and polkit-devel for new polkit-agent-1 dependency
