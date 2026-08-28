# These will be automatically populated by update.sh
%global commit          0fa5fbf60ec025289fb13813d6d1833848bf2f30
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260828221150
# SceneFX submodule pin (noctalia-dev/scenefx, umbriel branch) - tracks the
# gitlink from upstream's tree; when upstream forgets to bump it after a
# scenefx push (breaking umbriel's own meson API check), update.sh falls
# back to the current umbriel-branch HEAD
%global scenefx_commit      2f46d54aa99d5bbe25a279017d47cb771f5210f3
%global scenefx_shortcommit %(c=%{scenefx_commit}; echo ${c:0:7})

# Fedora's default LTO flags (-flto=auto -ffat-lto-objects) trip a
# binutils/GCC linker-plugin bug when linking umbriel's test binaries
# against the statically vendored scenefx archive (subprojects/scenefx):
# the plugin claims some members as LTO IR (util_env.c.o) while others are
# pulled in as plain ELF objects (render_egl.c.o), leaving render_egl's
# env_parse_bool reference unresolvable:
#   undefined reference to `env_parse_bool' (link of action-registry-test)
# Proven by COPR build 10898364, local rpmbuild repro, `ld -y` trace
# ("definition of env_parse_bool ... symbol from plugin" vs unclaimed ELF
# reference), and a plugin-free relink that succeeds. Standard escape hatch
# applied per Fedora LTO policy; drop when scenefx/ld fix the claim logic.
%global _lto_cflags %{nil}

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
* Fri Aug 28 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20260828221150git0fa5fbf-1
- Nightly sync with upstream main branch (Commit: 0fa5fbf)
