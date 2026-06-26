# These will be automatically populated by update.sh
%global commit          d956d3ed46eacabe0196b050d5476f193d75061c
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260626152427

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
* Fri Jun 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260626152427gitd956d3e-1
- Nightly sync with upstream main branch (Commit: d956d3e)

* Fri Jun 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260626120303gitf7371f4-1
- Nightly sync with upstream main branch (Commit: f7371f4)

* Fri Jun 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260626082113git4263897-1
- Nightly sync with upstream main branch (Commit: 4263897)

* Fri Jun 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260626034611git78e528b-1
- Nightly sync with upstream main branch (Commit: 78e528b)

* Thu Jun 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260625202712gitb4b74ef-1
- Nightly sync with upstream main branch (Commit: b4b74ef)

* Thu Jun 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260625181128git3878e85-1
- Nightly sync with upstream main branch (Commit: 3878e85)

* Thu Jun 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260625142959gitdc8ea32-1
- Nightly sync with upstream main branch (Commit: dc8ea32)

* Thu Jun 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260625101233git20c5a8f-1
- Nightly sync with upstream main branch (Commit: 20c5a8f)

* Thu Jun 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260625070451git88114eb-1
- Nightly sync with upstream main branch (Commit: 88114eb)

* Wed Jun 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260624211738git9350215-1
- Nightly sync with upstream main branch (Commit: 9350215)

* Wed Jun 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260624194334git842bd87-1
- Nightly sync with upstream main branch (Commit: 842bd87)

* Wed Jun 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260624173817git955a19d-1
- Nightly sync with upstream main branch (Commit: 955a19d)

* Wed Jun 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260624140834git90a1c78-1
- Nightly sync with upstream main branch (Commit: 90a1c78)

* Wed Jun 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260624052004git74fc383-1
- Nightly sync with upstream main branch (Commit: 74fc383)

* Wed Jun 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260624024717git13df671-1
- Nightly sync with upstream main branch (Commit: 13df671)

* Tue Jun 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260623222831git2b1fac0-1
- Nightly sync with upstream main branch (Commit: 2b1fac0)

* Tue Jun 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260623153425gitefb96e4-1
- Nightly sync with upstream main branch (Commit: efb96e4)

* Tue Jun 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260623140307git2b21b98-1
- Nightly sync with upstream main branch (Commit: 2b21b98)

* Tue Jun 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260623103923gitf3912d8-1
- Nightly sync with upstream main branch (Commit: f3912d8)

* Tue Jun 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260623073625git891ca9a-1
- Nightly sync with upstream main branch (Commit: 891ca9a)

* Tue Jun 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260623034559gita5eeef1-1
- Nightly sync with upstream main branch (Commit: a5eeef1)

* Mon Jun 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260622201316gita5a5ea6-1
- Nightly sync with upstream main branch (Commit: a5a5ea6)

* Mon Jun 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260622170228git50bb514-1
- Nightly sync with upstream main branch (Commit: 50bb514)

* Mon Jun 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260622120639gitff27db8-1
- Nightly sync with upstream main branch (Commit: ff27db8)

* Mon Jun 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260622044612git00f4789-1
- Nightly sync with upstream main branch (Commit: 00f4789)

* Sun Jun 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260621214530gitae8eb0d-1
- Nightly sync with upstream main branch (Commit: ae8eb0d)

* Sun Jun 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260621195154git68fa375-1
- Nightly sync with upstream main branch (Commit: 68fa375)

* Sun Jun 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260621175840gitf0d2617-1
- Nightly sync with upstream main branch (Commit: f0d2617)

* Sun Jun 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260621112128git7584f93-1
- Nightly sync with upstream main branch (Commit: 7584f93)

* Sun Jun 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260621094601git34905c9-1
- Nightly sync with upstream main branch (Commit: 34905c9)

* Sun Jun 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260621040441gitbb53b2c-1
- Nightly sync with upstream main branch (Commit: bb53b2c)

* Sat Jun 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260620225141gitc44150c-1
- Nightly sync with upstream main branch (Commit: c44150c)

* Sat Jun 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260620182435git5d813fa-1
- Nightly sync with upstream main branch (Commit: 5d813fa)

* Sat Jun 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260620165936git77e2a32-1
- Nightly sync with upstream main branch (Commit: 77e2a32)

* Sat Jun 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260620132122git947455f-1
- Nightly sync with upstream main branch (Commit: 947455f)

* Sat Jun 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260620111653gite61abbf-1
- Nightly sync with upstream main branch (Commit: e61abbf)

* Sat Jun 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260620091713git60bc281-1
- Nightly sync with upstream main branch (Commit: 60bc281)

* Sat Jun 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260620002112gita7af758-1
- Nightly sync with upstream main branch (Commit: a7af758)

* Fri Jun 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260619212023git67a99b5-1
- Nightly sync with upstream main branch (Commit: 67a99b5)

* Fri Jun 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260619211003git4719392-1
- Nightly sync with upstream main branch (Commit: 4719392)

* Fri Jun 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260619175040gitaa8448f-1
- Nightly sync with upstream main branch (Commit: aa8448f)

* Fri Jun 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260619152523gitf6088e6-1
- Nightly sync with upstream main branch (Commit: f6088e6)

* Thu Jun 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260618215216git7bc707b-1
- Nightly sync with upstream main branch (Commit: 7bc707b)

* Thu Jun 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260618143241git44d74a6-1
- Nightly sync with upstream main branch (Commit: 44d74a6)

* Thu Jun 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260618092147gitfaa49a9-1
- Nightly sync with upstream main branch (Commit: faa49a9)

* Thu Jun 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260617223522git751ca0c-1
- Nightly sync with upstream main branch (Commit: 751ca0c)

* Wed Jun 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260617212907git23d69b5-1
- Nightly sync with upstream main branch (Commit: 23d69b5)

* Wed Jun 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260617180924git08e74ff-1
- Nightly sync with upstream main branch (Commit: 08e74ff)

* Wed Jun 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260617110234gitfaebcd3-1
- Nightly sync with upstream main branch (Commit: faebcd3)

* Wed Jun 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260617032226git6b0e161-1
- Nightly sync with upstream main branch (Commit: 6b0e161)

* Tue Jun 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260616183828git28a38bf-1
- Nightly sync with upstream main branch (Commit: 28a38bf)

* Tue Jun 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260616162100git7a0cfab-1
- Nightly sync with upstream main branch (Commit: 7a0cfab)

* Tue Jun 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260616033846gitde82488-1
- Nightly sync with upstream main branch (Commit: de82488)

* Mon Jun 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260615220505git37e5a67-1
- Nightly sync with upstream main branch (Commit: 37e5a67)

* Mon Jun 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260615173737git0938085-1
- Nightly sync with upstream main branch (Commit: 0938085)

* Mon Jun 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260615121058git23bfea0-1
- Nightly sync with upstream main branch (Commit: 23bfea0)

* Mon Jun 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260615043125gitdeaae83-1
- Nightly sync with upstream main branch (Commit: deaae83)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614225323gitc6a7df9-1
- Nightly sync with upstream main branch (Commit: c6a7df9)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614211124git891db2a-1
- Nightly sync with upstream main branch (Commit: 891db2a)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614180933gitfbd80d4-1
- Nightly sync with upstream main branch (Commit: fbd80d4)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614165612gitcc1983d-1
- Nightly sync with upstream main branch (Commit: cc1983d)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614154933git61b07cb-1
- Nightly sync with upstream main branch (Commit: 61b07cb)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614100326gitbc92c41-1
- Nightly sync with upstream main branch (Commit: bc92c41)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614093831gitc08fd2d-1
- Nightly sync with upstream main branch (Commit: c08fd2d)

* Sun Jun 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260614042624git65e127f-1
- Nightly sync with upstream main branch (Commit: 65e127f)

* Sat Jun 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260613211747git90c91f2-1
- Nightly sync with upstream main branch (Commit: 90c91f2)

* Sat Jun 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260613192815git7fb6c33-1
- Nightly sync with upstream main branch (Commit: 7fb6c33)

* Sat Jun 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260613033659gite3d2926-1
- Nightly sync with upstream main branch (Commit: e3d2926)

* Fri Jun 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260612212048git600e194-1
- Nightly sync with upstream main branch (Commit: 600e194)

* Fri Jun 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260612154453git2070b4b-1
- Nightly sync with upstream main branch (Commit: 2070b4b)

* Fri Jun 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260612145127git8c7a9cf-1
- Nightly sync with upstream main branch (Commit: 8c7a9cf)

* Fri Jun 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260612013914git885b5f1-1
- Nightly sync with upstream main branch (Commit: 885b5f1)

* Thu Jun 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260611224332git20ff813-1
- Nightly sync with upstream main branch (Commit: 20ff813)

* Thu Jun 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260611194527git9403006-1
- Nightly sync with upstream main branch (Commit: 9403006)

* Thu Jun 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260611153442gitb4ae8ee-1
- Nightly sync with upstream main branch (Commit: b4ae8ee)

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
