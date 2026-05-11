# These will be automatically populated by update.sh
%global commit          d26c14295222dde411e73c5f85a70f0b8064bcaf
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260511211048

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
BuildRequires:  librsvg2-devel

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
* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511211048gitd26c142-1
- Nightly sync with upstream v5 branch (Commit: d26c142)

* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511182221gita217532-1
- Nightly sync with upstream v5 branch (Commit: a217532)

* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511175130gitb8baf32-1
- Nightly sync with upstream v5 branch (Commit: b8baf32)

* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511141652giteddceb1-1
- Nightly sync with upstream v5 branch (Commit: eddceb1)

* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511105734git213b60a-1
- Nightly sync with upstream v5 branch (Commit: 213b60a)

* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511035848git4bb6842-1
- Nightly sync with upstream v5 branch (Commit: 4bb6842)

* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511033328git6740260-1
- Nightly sync with upstream v5 branch (Commit: 6740260)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510224847gitd9218d2-1
- Nightly sync with upstream v5 branch (Commit: d9218d2)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510203346git773c20b-1
- Nightly sync with upstream v5 branch (Commit: 773c20b)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510164833gitb62f6fe-1
- Nightly sync with upstream v5 branch (Commit: b62f6fe)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510143745git4d70b4f-1
- Nightly sync with upstream v5 branch (Commit: 4d70b4f)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510115445git32c6be9-1
- Nightly sync with upstream v5 branch (Commit: 32c6be9)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510105029gitedce19b-1
- Nightly sync with upstream v5 branch (Commit: edce19b)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510082047gite43535c-1
- Nightly sync with upstream v5 branch (Commit: e43535c)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510045723git7de0769-1
- Nightly sync with upstream v5 branch (Commit: 7de0769)

* Sun May 10 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260510033222gitcd673dd-1
- Nightly sync with upstream v5 branch (Commit: cd673dd)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509214332gitebef1ab-1
- Nightly sync with upstream v5 branch (Commit: ebef1ab)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509204946git9483785-1
- Nightly sync with upstream v5 branch (Commit: 9483785)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509174556git88752c0-1
- Nightly sync with upstream v5 branch (Commit: 88752c0)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509162422git96b5ce5-1
- Nightly sync with upstream v5 branch (Commit: 96b5ce5)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509135305git5f6c6e2-1
- Nightly sync with upstream v5 branch (Commit: 5f6c6e2)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509122124git401dcde-1
- Nightly sync with upstream v5 branch (Commit: 401dcde)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509053039git72ae75e-1
- Nightly sync with upstream v5 branch (Commit: 72ae75e)

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260509025549git77fd820-1
- Nightly sync with upstream v5 branch (Commit: 77fd820)

* Fri May 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260508125436git20b6b16-1
- Nightly sync with upstream v5 branch (Commit: 20b6b16)

* Fri May 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260508100125git00ecd50-1
- Nightly sync with upstream v5 branch (Commit: 00ecd50)

* Fri May 08 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260508020043git9475eb5-1
- Nightly sync with upstream v5 branch (Commit: 9475eb5)

* Thu May 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260507191636git0408f95-1
- Nightly sync with upstream v5 branch (Commit: 0408f95)

* Thu May 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260507130212git1faa2f9-1
- Nightly sync with upstream v5 branch (Commit: 1faa2f9)

* Thu May 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260507102111git25fc1ea-1
- Nightly sync with upstream v5 branch (Commit: 25fc1ea)

* Thu May 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260507011830git1b2dec3-1
- Nightly sync with upstream v5 branch (Commit: 1b2dec3)

* Thu May 07 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506232906gitac6bd4b-1
- Nightly sync with upstream v5 branch (Commit: ac6bd4b)

* Wed May 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506225432gitb257105-1
- Nightly sync with upstream v5 branch (Commit: b257105)

* Wed May 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506175832git8cb73cb-1
- Nightly sync with upstream v5 branch (Commit: 8cb73cb)

* Wed May 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506174003gite7668fc-1
- Nightly sync with upstream v5 branch (Commit: e7668fc)

* Wed May 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506141904git7556f23-1
- Nightly sync with upstream v5 branch (Commit: 7556f23)

* Wed May 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506075655git8f7e585-1
- Nightly sync with upstream v5 branch (Commit: 8f7e585)

* Wed May 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506061923git3c07a0a-1
- Nightly sync with upstream v5 branch (Commit: 3c07a0a)

* Wed May 06 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260506024624git5691203-1
- Nightly sync with upstream v5 branch (Commit: 5691203)

* Tue May 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260505211654gitcd66344-1
- Nightly sync with upstream v5 branch (Commit: cd66344)

* Tue May 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260505170933git296da60-1
- Nightly sync with upstream v5 branch (Commit: 296da60)

* Tue May 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260505040900gite7a557e-1
- Nightly sync with upstream v5 branch (Commit: e7a557e)

* Tue May 05 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260505030316git44f05e8-1
- Nightly sync with upstream v5 branch (Commit: 44f05e8)

* Mon May 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260504225814gitdafe329-1
- Nightly sync with upstream v5 branch (Commit: dafe329)

* Mon May 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260504204850git91c1658-1
- Nightly sync with upstream v5 branch (Commit: 91c1658)

* Mon May 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260504151756git1dbfadd-1
- Nightly sync with upstream v5 branch (Commit: 1dbfadd)

* Mon May 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260504141251gitc48a100-1
- Nightly sync with upstream v5 branch (Commit: c48a100)

* Mon May 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260504094730git1c8abec-1
- Nightly sync with upstream v5 branch (Commit: 1c8abec)

* Mon May 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260504042554gitf855983-1
- Nightly sync with upstream v5 branch (Commit: f855983)

* Mon May 04 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260504030805git8083d29-1
- Nightly sync with upstream v5 branch (Commit: 8083d29)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503223330git42bf745-1
- Nightly sync with upstream v5 branch (Commit: 42bf745)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503194742git1c2e0fb-1
- Nightly sync with upstream v5 branch (Commit: 1c2e0fb)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503190138gitcc5d81e-1
- Nightly sync with upstream v5 branch (Commit: cc5d81e)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503164259git40fe2b3-1
- Nightly sync with upstream v5 branch (Commit: 40fe2b3)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503143336git55c2753-1
- Nightly sync with upstream v5 branch (Commit: 55c2753)

* Sun May 03 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260503131532gite0ceff9-1
- Nightly sync with upstream v5 branch (Commit: e0ceff9)

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
