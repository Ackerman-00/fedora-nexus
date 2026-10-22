# These will be automatically populated by update.sh
%global commit          e3534acf3275148355bf8b264f157a00f53bec86
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20261022105026

# Fedora LTO flags break linking; keep escape hatch.
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
# Pin localed=enabled; default auto fails silently.
BuildRequires:  pkgconfig(libsystemd) >= 243
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.1
# wlroots pinned to 0.20.x for umbrielfx layouts.
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server) >= 1.24
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.47
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput) >= 1.27
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0
# libdisplay-info: upstream floor, F43 needs relaxation.
%if 0%{?fedora} >= 44
BuildRequires:  pkgconfig(libdisplay-info) >= 0.3.0
%else
BuildRequires:  pkgconfig(libdisplay-info)
%endif
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
# Native DRM policy optional; off breaks [drm] config.
BuildRequires:  pkgconfig(libudev)

# Needs Xwayland on PATH; xwayland-satellite dropped.
Requires:       xorg-x11-server-Xwayland%{?_isa}
Requires:       xdg-desktop-portal-umbriel-git
Requires:       mesa-dri-drivers
Requires:       mesa-libEGL
# Portal framework - xdg-desktop-portal-umbriel-git is the Umbriel backend
Requires:       xdg-desktop-portal
# start-umbriel needs systemctl and dbus helpers.
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
# F43: relax libdisplay-info floor; remove at EOL.
%if 0%{?fedora} == 43
sed -i "s/dependency('libdisplay-info', version: '>=0.3.0')/dependency('libdisplay-info', version: '>=0.2.0')/" meson.build
%endif

%build
# -Dtests=disabled states release intent explicitly.
%meson -Db_lto=true -Dtests=disabled -Dtest_ipc=disabled -Dlocaled=enabled
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
* Thu Oct 22 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.0^20261022105026gite3534ac-1
- Nightly sync with upstream main branch (Commit: e3534ac)
