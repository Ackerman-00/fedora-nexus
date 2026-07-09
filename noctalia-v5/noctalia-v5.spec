# These will be automatically populated by update.sh
%global commit          c2aac465cf24ea0e924fbe405425dec1818db91d
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260709071837

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
BuildRequires:  wireplumber-devel
BuildRequires:  pkgconf
BuildRequires:  libglvnd-devel

# Explicit runtime requirement for privilege escalation 
Requires:       polkit

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
export CXXFLAGS="%{optflags} -std=c++23 -Wno-unused-result"
export CFLAGS="%{optflags}"

%meson -Db_ndebug=true -Dtests=disabled
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_bindir}/noctalia
%{_datadir}/noctalia/
%{_datadir}/applications/dev.noctalia.Noctalia.desktop
%{_datadir}/icons/hicolor/scalable/apps/noctalia.svg

%changelog
* Thu Jul 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260709071837gitc2aac46-1
- Nightly sync with upstream main branch (Commit: c2aac46)

* Thu Jul 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260709013919gitee18934-1
- Nightly sync with upstream main branch (Commit: ee18934)

* Wed Jul 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260708153813gitf63a44a-1
- Nightly sync with upstream main branch (Commit: f63a44a)

* Wed Jul 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260708112326git54c8cd4-1
- Nightly sync with upstream main branch (Commit: 54c8cd4)

* Wed Jul 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260708095320gite53f948-1
- Nightly sync with upstream main branch (Commit: e53f948)

* Wed Jul 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260708015819git099312d-1
- Nightly sync with upstream main branch (Commit: 099312d)

* Wed Jul 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260708014058git3bb2b58-1
- Nightly sync with upstream main branch (Commit: 3bb2b58)

* Tue Jul 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260707142404gitb57faef-1
- Nightly sync with upstream main branch (Commit: b57faef)

* Tue Jul 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260707135516git1331548-1
- Nightly sync with upstream main branch (Commit: 1331548)

* Tue Jul 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260707042227git831c513-1
- Nightly sync with upstream main branch (Commit: 831c513)

* Tue Jul 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260707020214gitee80e44-1
- Nightly sync with upstream main branch (Commit: ee80e44)

* Mon Jul 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260706170352git7a30ffa-1
- Nightly sync with upstream main branch (Commit: 7a30ffa)

* Mon Jul 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260706144839git0ed4225-1
- Nightly sync with upstream main branch (Commit: 0ed4225)

* Mon Jul 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260706041000gitb6fd0df-1
- Nightly sync with upstream main branch (Commit: b6fd0df)

* Mon Jul 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260706020348git6f1abe7-1
- Nightly sync with upstream main branch (Commit: 6f1abe7)

* Sun Jul 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260705194228gite56f6e8-1
- Nightly sync with upstream main branch (Commit: e56f6e8)

* Sun Jul 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260705151406git87db64f-1
- Nightly sync with upstream main branch (Commit: 87db64f)

* Sun Jul 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260705090247git2be5e68-1
- Nightly sync with upstream main branch (Commit: 2be5e68)

* Sun Jul 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260705025819git10b2007-1
- Nightly sync with upstream main branch (Commit: 10b2007)

* Sun Jul 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260705012538git79dcc65-1
- Nightly sync with upstream main branch (Commit: 79dcc65)

* Sat Jul 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260704201814git4d76b6d-1
- Nightly sync with upstream main branch (Commit: 4d76b6d)

* Sat Jul 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260704160949gitba882ba-1
- Nightly sync with upstream main branch (Commit: ba882ba)

* Sat Jul 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260704113034git737aa65-1
- Nightly sync with upstream main branch (Commit: 737aa65)

* Sat Jul 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260704065122gite1e904c-1
- Nightly sync with upstream main branch (Commit: e1e904c)

* Sat Jul 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260704063559git4aa9f43-1
- Nightly sync with upstream main branch (Commit: 4aa9f43)

* Sat Jul 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260704014215git707e049-1
- Nightly sync with upstream main branch (Commit: 707e049)

* Fri Jul 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260703190456git2abf875-1
- Nightly sync with upstream main branch (Commit: 2abf875)

* Fri Jul 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260703154855gita0d8efc-1
- Nightly sync with upstream main branch (Commit: a0d8efc)

* Fri Jul 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260703131922git8332ab8-1
- Nightly sync with upstream main branch (Commit: 8332ab8)

* Fri Jul 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260703102004git833a09d-1
- Nightly sync with upstream main branch (Commit: 833a09d)

* Fri Jul 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260703004702git6e7aa3b-1
- Nightly sync with upstream main branch (Commit: 6e7aa3b)
