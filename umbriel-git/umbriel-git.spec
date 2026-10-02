# These will be automatically populated by update.sh
%global commit          3dc05322983a7a1108a1585fa9edb91909c4edf8
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261002130520

# Fedora's default LTO flags (-flto=auto -ffat-lto-objects) trip a
# binutils/GCC linker-plugin bug when linking umbriel's test binaries
# against its statically built umbrielfx archive:
# the plugin claims some members as LTO IR while others are pulled in as
# plain ELF objects, leaving references unresolvable
# (previously: vendored umbrielfx/util_env.c.o vs render_egl.c.o: env_parse_bool).
# Proven by COPR build 10898364; keep escape hatch until upstream/LD fixed.
%global _lto_cflags %{nil}

Name:           umbriel-git
Version:        0.1.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Wayland compositor with scrolling and dwindle layouts

License:        MIT
URL:            https://github.com/noctalia-dev/umbriel
Source0:        %{url}/archive/%{commit}/umbriel-%{shortcommit}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  meson >= 1.3
BuildRequires:  ninja-build
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.1
# umbrielfx compiles against wlroots private layouts: pinned to 0.20.x
# upstream (meson.build: >=0.20.1, <0.21.0). Revisit on upstream bump.
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server) >= 1.24
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.47
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput) >= 1.23
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0
BuildRequires:  pkgconfig(libdrm) >= 2.4.129
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(jemalloc)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-ewmh)
# Optional upstream (required: false): without it meson silently builds
# UMBRIEL_HAS_NATIVE_DRM_POLICY=0 and the [drm] exclusion config stops working.
BuildRequires:  pkgconfig(libudev)

# Native wlroots Xwayland integration: needs the Xwayland binary on PATH
# (upstream dropped xwayland-satellite; README/PACKAGING.md as of 2026-09).
Requires:       xorg-x11-server-Xwayland%{?_isa}
Requires:       xdg-desktop-portal-umbriel-git
Requires:       mesa-dri-drivers
Requires:       mesa-libEGL
# Portal framework - xdg-desktop-portal-umbriel-git is the Umbriel backend
Requires:       xdg-desktop-portal
# start-umbriel needs systemctl (managed path) + dbus session helpers.
# Verified on F44: dnf repoquery --whatprovides => systemd, dbus-daemon, dbus-tools.
Requires:       systemd
Requires:       dbus-daemon
Requires:       dbus-tools
# PACKAGING.md runtime table: "a usable font stack" for overlays/diagnostics.
Recommends:     liberation-fonts

Provides:       umbriel = %{version}-%{release}
Provides:       wayland-compositor
Conflicts:      umbriel

%description
Umbriel is a Wayland compositor designed for daily use, with scrolling and
dwindle layouts, per-output workspaces, window rules, blur, shadows, and
fluid animations. Built in C++23 on wlroots and the Noctalia SceneFX fork,
with X11 support from wlroots' native Xwayland integration (requires the
Xwayland binary on PATH) and portal screen capture and sharing
by xdg-desktop-portal-umbriel.
Compiled specifically for the Nexus repository via automated Git snapshot.

%prep
%autosetup -n umbriel-%{commit}

%build
# -Dtests=disabled states the release-build intent explicitly (PACKAGING.md;
# tests=auto already resolves off for release, same as nix/package.nix).
%meson -Db_lto=true -Dtests=disabled -Dtest_ipc=disabled
%meson_build

%install
%meson_install

%post
%systemd_user_post umbriel.service

%preun
%systemd_user_preun umbriel.service

%postun
%systemd_user_postun umbriel.service

%files
%license LICENSE
%doc README.md
%{_bindir}/umbriel
%{_bindir}/start-umbriel
%dir %{_datadir}/umbriel
%config(noreplace) %{_datadir}/umbriel/config.toml
%{_datadir}/umbriel/effects/
%{_datadir}/wayland-sessions/umbriel.desktop
%{_userunitdir}/umbriel.service
%{_userunitdir}/umbriel-session.target
%{_userunitdir}/umbriel-shutdown.target

%changelog
* Fri Oct 02 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20261002130520git3dc0532-1
- Nightly sync with upstream main branch (Commit: 3dc0532)
