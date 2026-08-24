# These will be automatically populated by update.sh
%global commit          4f9db98ba6c64458723b9273a6b7f15739ce824d
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260824125130
# SceneFX submodule pin (noctalia-dev/scenefx, umbriel branch) - tracks the
# gitlink from upstream's tree; when upstream forgets to bump it after a
# scenefx push (breaking umbriel's own meson API check), update.sh falls
# back to the current umbriel-branch HEAD
%global scenefx_commit      dcf4614b177e1a6619a6eea47825f78f8884ac3b
%global scenefx_shortcommit %(c=%{scenefx_commit}; echo ${c:0:7})

Name:           umbriel-git
Version:        0.1.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Wayland compositor with scrolling and dwindle layouts (Nexus Optimized Git Snapshot)

License:        MIT
URL:            https://github.com/noctalia-dev/umbriel
Source0:        %{url}/archive/%{commit}/umbriel-%{shortcommit}.tar.gz
# GitHub archives exclude git submodules; umbriel requires the patched
# SceneFX fork API (scenefx-0.5, umbriel branch). Vendored into
# subprojects/scenefx during %%prep and linked statically via the meson
# subproject fallback (never installed: %%meson_install --skip-subprojects).
Source1:        https://github.com/noctalia-dev/scenefx/archive/%{scenefx_commit}/scenefx-%{scenefx_shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc-c++
BuildRequires:  meson >= 1.3
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(wlroots-0.20)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.32
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput) >= 1.23
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(jemalloc)

Requires:       xwayland-satellite-git
Requires:       xdg-desktop-portal-umbriel-git
Requires:       mesa-dri-drivers
Requires:       mesa-libEGL
Requires:       libwayland-server
# Portal framework - xdg-desktop-portal-umbriel-git is the Umbriel backend
Requires:       xdg-desktop-portal

Provides:       umbriel = %{version}-%{release}
Provides:       wayland-compositor
Conflicts:      umbriel

%description
Umbriel is a Wayland compositor designed for daily use, with scrolling and
dwindle layouts, per-output workspaces, window rules, blur, shadows, and
fluid animations. Built in C++23 on wlroots and the Noctalia SceneFX fork,
with Xwayland support provided by xwayland-satellite and portal screen
capture and sharing by xdg-desktop-portal-umbriel.
Compiled specifically for the Nexus repository via automated Git snapshot.

%prep
%autosetup -n umbriel-%{commit} -a1
# GitHub archive tarballs ship submodules as empty directories; swap in the
# pinned SceneFX fork so meson builds it as the subproject fallback.
rm -rf subprojects/scenefx
mv scenefx-%{scenefx_commit} subprojects/scenefx

%build
%meson -Db_lto=true
%meson_build

%install
%meson_install --skip-subprojects

%files
%license LICENSE
%doc README.md
%{_bindir}/umbriel
%{_bindir}/start-umbriel
%dir %{_datadir}/umbriel
%{_datadir}/umbriel/config.toml
%{_datadir}/wayland-sessions/umbriel.desktop
%{_userunitdir}/umbriel.service
%{_userunitdir}/umbriel-session.target
%{_userunitdir}/umbriel-shutdown.target

%changelog
* Mon Aug 24 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260824125130git4f9db98-1
- Nightly sync with upstream main branch (Commit: 4f9db98)
