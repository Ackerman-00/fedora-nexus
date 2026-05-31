# These will be automatically populated by update.sh
%global commit          0af9e966e86c83c914b201070df7a1d0b886ab79
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260531035951

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
* Sun May 31 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260531035951git0af9e96-1
- Nightly sync with upstream v5 branch (Commit: 0af9e96)

* Sat May 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260530225140git3c14a5f-1
- Nightly sync with upstream v5 branch (Commit: 3c14a5f)

* Sat May 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260530205233gitbfbf8a2-1
- Nightly sync with upstream v5 branch (Commit: bfbf8a2)

* Sat May 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260530180656git6ec1ae7-1
- Nightly sync with upstream v5 branch (Commit: 6ec1ae7)

* Sat May 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260530164648gitff0a1c6-1
- Nightly sync with upstream v5 branch (Commit: ff0a1c6)

* Sat May 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260530120856gitdf68ad7-1
- Nightly sync with upstream v5 branch (Commit: df68ad7)

* Sat May 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260530045931gitbd74c34-1
- Nightly sync with upstream v5 branch (Commit: bd74c34)

* Sat May 30 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260530012329git5beec2c-1
- Nightly sync with upstream v5 branch (Commit: 5beec2c)

* Fri May 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260529203633git2df6432-1
- Nightly sync with upstream v5 branch (Commit: 2df6432)

* Fri May 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260529183517git19e6ddc-1
- Nightly sync with upstream v5 branch (Commit: 19e6ddc)

* Fri May 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260529140302git9c89685-1
- Nightly sync with upstream v5 branch (Commit: 9c89685)

* Fri May 29 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260529005020git0e4bb96-1
- Nightly sync with upstream v5 branch (Commit: 0e4bb96)

* Thu May 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260528222400gitf1bfaaf-1
- Nightly sync with upstream v5 branch (Commit: f1bfaaf)

* Thu May 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260528193527git5dab086-1
- Nightly sync with upstream v5 branch (Commit: 5dab086)

* Thu May 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260528153342git6fa8377-1
- Nightly sync with upstream v5 branch (Commit: 6fa8377)

* Thu May 28 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260528023430git6df784d-1
- Nightly sync with upstream v5 branch (Commit: 6df784d)

* Wed May 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260527232509git88880de-1
- Nightly sync with upstream v5 branch (Commit: 88880de)

* Wed May 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260527202717git990010c-1
- Nightly sync with upstream v5 branch (Commit: 990010c)

* Wed May 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260527181755git0acfc23-1
- Nightly sync with upstream v5 branch (Commit: 0acfc23)

* Wed May 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260527123553gitcc1b0a8-1
- Nightly sync with upstream v5 branch (Commit: cc1b0a8)

* Wed May 27 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260527033839git22fb36c-1
- Nightly sync with upstream v5 branch (Commit: 22fb36c)

* Tue May 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260526225056gite28eff4-1
- Nightly sync with upstream v5 branch (Commit: e28eff4)

* Tue May 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260526205249git10a7978-1
- Nightly sync with upstream v5 branch (Commit: 10a7978)

* Tue May 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260526175912gitbc6dc1a-1
- Nightly sync with upstream v5 branch (Commit: bc6dc1a)

* Tue May 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260526135155gita801b16-1
- Nightly sync with upstream v5 branch (Commit: a801b16)

* Tue May 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260526041157git1079688-1
- Nightly sync with upstream v5 branch (Commit: 1079688)

* Tue May 26 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260526033659git86780c5-1
- Nightly sync with upstream v5 branch (Commit: 86780c5)

* Mon May 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260525225214git2c2d0b1-1
- Nightly sync with upstream v5 branch (Commit: 2c2d0b1)

* Mon May 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260525184916gitfbef575-1
- Nightly sync with upstream v5 branch (Commit: fbef575)

* Mon May 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260525171745gitfaf3b7d-1
- Nightly sync with upstream v5 branch (Commit: faf3b7d)

* Mon May 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260525145724git217f9ea-1
- Nightly sync with upstream v5 branch (Commit: 217f9ea)

* Mon May 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260525042420gite54ca24-1
- Nightly sync with upstream v5 branch (Commit: e54ca24)

* Mon May 25 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260525041108gitddfb5cc-1
- Nightly sync with upstream v5 branch (Commit: ddfb5cc)

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260524224812gitf25e0f2-1
- Nightly sync with upstream v5 branch (Commit: f25e0f2)

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260524204730git8aa1869-1
- Nightly sync with upstream v5 branch (Commit: 8aa1869)

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260524191919gitd782ff7-1
- Nightly sync with upstream v5 branch (Commit: d782ff7)

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260524143541git5daaf2d-1
- Nightly sync with upstream v5 branch (Commit: 5daaf2d)

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260524134133git1233c66-1
- Nightly sync with upstream v5 branch (Commit: 1233c66)

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260524050358gitfcd8a62-1
- Nightly sync with upstream v5 branch (Commit: fcd8a62)

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260524040006gitc561e1d-1
- Nightly sync with upstream v5 branch (Commit: c561e1d)

* Sat May 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260523225023git6a2b151-1
- Nightly sync with upstream v5 branch (Commit: 6a2b151)

* Sat May 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260523192839git2e683ba-1
- Nightly sync with upstream v5 branch (Commit: 2e683ba)

* Sat May 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260523184501git3ab592a-1
- Nightly sync with upstream v5 branch (Commit: 3ab592a)

* Sat May 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260523135000gita365a75-1
- Nightly sync with upstream v5 branch (Commit: a365a75)

* Sat May 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260523101851git2d33ade-1
- Nightly sync with upstream v5 branch (Commit: 2d33ade)

* Sat May 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260523045159gitd90351e-1
- Nightly sync with upstream v5 branch (Commit: d90351e)

* Sat May 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260523033129gitce1a645-1
- Nightly sync with upstream v5 branch (Commit: ce1a645)

* Fri May 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260522222336git25e0dd1-1
- Nightly sync with upstream v5 branch (Commit: 25e0dd1)

* Fri May 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260522204055git59c8568-1
- Nightly sync with upstream v5 branch (Commit: 59c8568)

* Fri May 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260522192118gitcbb9519-1
- Nightly sync with upstream v5 branch (Commit: cbb9519)

* Fri May 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260522121856git1cb3da2-1
- Nightly sync with upstream v5 branch (Commit: 1cb3da2)

* Fri May 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260522044051gitf04e6e8-1
- Nightly sync with upstream v5 branch (Commit: f04e6e8)

* Fri May 22 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260522022526git7c0daaa-1
- Nightly sync with upstream v5 branch (Commit: 7c0daaa)

* Thu May 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260521230557gite102697-1
- Nightly sync with upstream v5 branch (Commit: e102697)

* Thu May 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260521210951git3b70428-1
- Nightly sync with upstream v5 branch (Commit: 3b70428)

* Thu May 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260521194740git4eb37bb-1
- Nightly sync with upstream v5 branch (Commit: 4eb37bb)

* Thu May 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260521141452git2a75dce-1
- Nightly sync with upstream v5 branch (Commit: 2a75dce)

* Thu May 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260521123849gite5c5327-1
- Nightly sync with upstream v5 branch (Commit: e5c5327)

* Thu May 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260521090931gitdb23d04-1
- Nightly sync with upstream v5 branch (Commit: db23d04)

* Thu May 21 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260521031826git364b573-1
- Nightly sync with upstream v5 branch (Commit: 364b573)

* Wed May 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260520220412git9ae7abe-1
- Nightly sync with upstream v5 branch (Commit: 9ae7abe)

* Wed May 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260520214659git3e5161c-1
- Nightly sync with upstream v5 branch (Commit: 3e5161c)

* Wed May 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260520175810gite1e7160-1
- Nightly sync with upstream v5 branch (Commit: e1e7160)

* Wed May 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260520151932git8d5d8a3-1
- Nightly sync with upstream v5 branch (Commit: 8d5d8a3)

* Wed May 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260520052638gite056619-1
- Nightly sync with upstream v5 branch (Commit: e056619)

* Wed May 20 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260520021355git005219f-1
- Nightly sync with upstream v5 branch (Commit: 005219f)

* Tue May 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260519200721git363d752-1
- Nightly sync with upstream v5 branch (Commit: 363d752)

* Tue May 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260519154010git931c37c-1
- Nightly sync with upstream v5 branch (Commit: 931c37c)

* Tue May 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260519152303git388712d-1
- Nightly sync with upstream v5 branch (Commit: 388712d)

* Tue May 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260519111900git28ebbb9-1
- Nightly sync with upstream v5 branch (Commit: 28ebbb9)

* Tue May 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260519044949git2a94e7f-1
- Nightly sync with upstream v5 branch (Commit: 2a94e7f)

* Tue May 19 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260519034235gitd3c6f28-1
- Nightly sync with upstream v5 branch (Commit: d3c6f28)

* Mon May 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260518214901git7c17669-1
- Nightly sync with upstream v5 branch (Commit: 7c17669)

* Mon May 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260518203450gitf1fae8f-1
- Nightly sync with upstream v5 branch (Commit: f1fae8f)

* Mon May 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260518175946git0a8069d-1
- Nightly sync with upstream v5 branch (Commit: 0a8069d)

* Mon May 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260518152847gitae148fc-1
- Nightly sync with upstream v5 branch (Commit: ae148fc)

* Mon May 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260518045050gitcce1141-1
- Nightly sync with upstream v5 branch (Commit: cce1141)

* Mon May 18 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260518035913gitc9d02ed-1
- Nightly sync with upstream v5 branch (Commit: c9d02ed)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517222850git5707ca0-1
- Nightly sync with upstream v5 branch (Commit: 5707ca0)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517180308git15503b5-1
- Nightly sync with upstream v5 branch (Commit: 15503b5)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517164018git10687a6-1
- Nightly sync with upstream v5 branch (Commit: 10687a6)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517133822gita6b3f19-1
- Nightly sync with upstream v5 branch (Commit: a6b3f19)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517105716gitd13190a-1
- Nightly sync with upstream v5 branch (Commit: d13190a)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517092505git2aa2cdb-1
- Nightly sync with upstream v5 branch (Commit: 2aa2cdb)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517051058git198fc68-1
- Nightly sync with upstream v5 branch (Commit: 198fc68)

* Sun May 17 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260517030520gitc664e13-1
- Nightly sync with upstream v5 branch (Commit: c664e13)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516224257gitf0c3e4e-1
- Nightly sync with upstream v5 branch (Commit: f0c3e4e)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516205121git26cd1c3-1
- Nightly sync with upstream v5 branch (Commit: 26cd1c3)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516184109gitf80051c-1
- Nightly sync with upstream v5 branch (Commit: f80051c)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516151809git9841a82-1
- Nightly sync with upstream v5 branch (Commit: 9841a82)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516145151git1a3dcb2-1
- Nightly sync with upstream v5 branch (Commit: 1a3dcb2)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516124933gita892378-1
- Nightly sync with upstream v5 branch (Commit: a892378)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516105658git42322d0-1
- Nightly sync with upstream v5 branch (Commit: 42322d0)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516051641git43b26d7-1
- Nightly sync with upstream v5 branch (Commit: 43b26d7)

* Sat May 16 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260516021519gita80cb8c-1
- Nightly sync with upstream v5 branch (Commit: a80cb8c)

* Fri May 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260515211443git00f3894-1
- Nightly sync with upstream v5 branch (Commit: 00f3894)

* Fri May 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260515195444git4ebb8e5-1
- Nightly sync with upstream v5 branch (Commit: 4ebb8e5)

* Fri May 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260515190743git13c1827-1
- Nightly sync with upstream v5 branch (Commit: 13c1827)

* Fri May 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260515174222git3e4d9e8-1
- Nightly sync with upstream v5 branch (Commit: 3e4d9e8)

* Fri May 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260515140826git2f26923-1
- Nightly sync with upstream v5 branch (Commit: 2f26923)

* Fri May 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260515043132git698f9be-1
- Nightly sync with upstream v5 branch (Commit: 698f9be)

* Fri May 15 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260515033924git55affaa-1
- Nightly sync with upstream v5 branch (Commit: 55affaa)

* Thu May 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260514223807git3f3b8eb-1
- Nightly sync with upstream v5 branch (Commit: 3f3b8eb)

* Thu May 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260514190639gite3d9fee-1
- Nightly sync with upstream v5 branch (Commit: e3d9fee)

* Thu May 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260514174034gita9c8801-1
- Nightly sync with upstream v5 branch (Commit: a9c8801)

* Thu May 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260514141642git105818c-1
- Nightly sync with upstream v5 branch (Commit: 105818c)

* Thu May 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260514081933git0dce2e0-1
- Nightly sync with upstream v5 branch (Commit: 0dce2e0)

* Thu May 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260514033004git4d8f04c-1
- Nightly sync with upstream v5 branch (Commit: 4d8f04c)

* Wed May 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260513191937git5615a9c-1
- Nightly sync with upstream v5 branch (Commit: 5615a9c)

* Wed May 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260513173029gite9d53f3-1
- Nightly sync with upstream v5 branch (Commit: e9d53f3)

* Wed May 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260513165515gita5cf193-1
- Nightly sync with upstream v5 branch (Commit: a5cf193)

* Wed May 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260513144119git8fcee63-1
- Nightly sync with upstream v5 branch (Commit: 8fcee63)

* Wed May 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260513100116gitce1917f-1
- Nightly sync with upstream v5 branch (Commit: ce1917f)

* Wed May 13 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260513030510git674ac11-1
- Nightly sync with upstream v5 branch (Commit: 674ac11)

* Tue May 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260512214758git1ec2642-1
- Nightly sync with upstream v5 branch (Commit: 1ec2642)

* Tue May 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260512205119gitb6d2ec6-1
- Nightly sync with upstream v5 branch (Commit: b6d2ec6)

* Tue May 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260512144833git165083c-1
- Nightly sync with upstream v5 branch (Commit: 165083c)

* Tue May 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260512133912git05d47ca-1
- Nightly sync with upstream v5 branch (Commit: 05d47ca)

* Tue May 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260512055018gitb2afbd6-1
- Nightly sync with upstream v5 branch (Commit: b2afbd6)

* Tue May 12 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260512025441gitb93543e-1
- Nightly sync with upstream v5 branch (Commit: b93543e)

* Mon May 11 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260511215403gitcf77db6-1
- Nightly sync with upstream v5 branch (Commit: cf77db6)

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
