# hyprland: BSD-3-Clause
# subprojects/hyprland-protocols: BSD-3-Clause
# subproject/udis86: BSD-2-Clause
# protocols/ext-workspace-unstable-v1.xml: HPND-sell-variant
# protocols/wlr-foreign-toplevel-management-unstable-v1.xml: HPND-sell-variant
# protocols/wlr-layer-shell-unstable-v1.xml: HPND-sell-variant
# protocols/idle.xml: LGPL-2.1-or-later
License:        BSD-3-Clause AND BSD-2-Clause AND HPND-sell-variant AND LGPL-2.1-or-later

Name:           hyprland
Version:        0.56.2
Release:        1%{?dist}
Summary:        Dynamic tiling Wayland compositor that doesn't sacrifice on its looks
URL:            https://github.com/hyprwm/Hyprland
Source0:        %{url}/releases/download/v%{version}/source-v%{version}.tar.gz
Source4:        macros.hyprland
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

%{lua:
hyprdeps = {
    "cmake",
    "gcc-c++",
    "ninja-build",
    "glslang",
    "muParser-devel",
    "glaze-static",
    "pkgconfig(aquamarine)",
    "pkgconfig(cairo)",
    "pkgconfig(egl)",
    "pkgconfig(gbm)",
    "pkgconfig(gio-2.0)",
    "pkgconfig(glesv2)",
    "pkgconfig(hwdata)",
    "pkgconfig(hyprcursor)",
    "pkgconfig(hyprgraphics)",
    "pkgconfig(hyprlang)",
    "pkgconfig(hyprutils)",
    "pkgconfig(hyprwayland-scanner)",
    "pkgconfig(hyprwire)",
    "pkgconfig(lcms2)",
    "pkgconfig(libdisplay-info)",
    "pkgconfig(libdrm)",
    "pkgconfig(libeis-1.0)",
    "pkgconfig(libinput) >= 1.28",
    "pkgconfig(libliftoff)",
    "pkgconfig(libseat)",
    "pkgconfig(libudev)",
    "pkgconfig(lua)",
    "pkgconfig(pango)",
    "pkgconfig(pangocairo)",
    "pkgconfig(pixman-1)",
    "pkgconfig(re2)",
    "pkgconfig(readline)",
    "pkgconfig(sdbus-c++)",
    "pkgconfig(systemd)",
    "pkgconfig(tomlplusplus)",
    "pkgconfig(uuid)",
    "pkgconfig(wayland-client)",
    "pkgconfig(wayland-protocols) >= 1.45",
    "pkgconfig(wayland-scanner)",
    "pkgconfig(wayland-server)",
    "pkgconfig(xcb-composite)",
    "pkgconfig(xcb-dri3)",
    "pkgconfig(xcb-errors)",
    "pkgconfig(xcb-ewmh)",
    "pkgconfig(xcb-icccm)",
    "pkgconfig(xcb-present)",
    "pkgconfig(xcb-render)",
    "pkgconfig(xcb-renderutil)",
    "pkgconfig(xcb-res)",
    "pkgconfig(xcb-shm)",
    "pkgconfig(xcb-util)",
    "pkgconfig(xcb-xfixes)",
    "pkgconfig(xcb-xinput)",
    "pkgconfig(xcb)",
    "pkgconfig(xcursor)",
    "pkgconfig(xkbcommon)",
    "pkgconfig(xwayland)",
    }
}

%define printbdeps(r) %{lua:
for _, dep in ipairs(hyprdeps) do
    print((rpm.expand("%{-r}") ~= "" and "Requires: " or "BuildRequires: ")..dep.."\\n")
end
}

%printbdeps

# udis86 is packaged in Fedora, but the copy bundled here is actually a
# modified fork.
Provides:       bundled(udis86) = 1.7.2

# glslang is a hard requirement; glaze 7.x is self-fetched by upstream when
# the system glaze (8.x) does not satisfy its <8 constraint.
Provides:       bundled(glaze) = 7.2.0

Requires:       xorg-x11-server-Xwayland%{?_isa}
Requires:       aquamarine%{?_isa} >= 0.9.2
Requires:       hyprcursor%{?_isa} >= 0.1.13
Requires:       hyprgraphics%{?_isa} >= 0.1.6
Requires:       hyprlang%{?_isa} >= 0.6.3
Requires:       hyprutils%{?_isa} >= 0.8.4

Obsoletes:      hyprland-nvidia < 1:0.32.3-2
Provides:       hyprland-nvidia = %{version}-%{release}
Obsoletes:      hyprland-legacyrenderer < 0.49.0

# Used in the default configuration
Recommends:     kitty
Recommends:     wofi
Recommends:     playerctl
Recommends:     brightnessctl
# Required for safe mode / welcome app since 0.53
Recommends:     hyprland-guiutils
# Lack of graphical drivers may hurt the common use case
Recommends:     mesa-dri-drivers
# Logind needs polkit to create a graphical session
Recommends:     polkit

Recommends:     (qt5-qtwayland if qt5-qtbase-gui)
Recommends:     (qt6-qtwayland if qt6-qtbase-gui)

%description
Hyprland is a dynamic tiling Wayland compositor that doesn't sacrifice
on its looks. It supports multiple layouts, fancy effects, has a
very flexible IPC model allowing for a lot of customization, a powerful
plugin system and more.
Compiled specifically for the Nexus repository from official upstream
release tarballs.

%package        devel
Summary:        Header and protocol files for %{name}
License:        BSD-3-Clause
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cpio
%printbdeps -r
Requires:       git-core
Requires:       pkgconfig(xkbcommon)

Obsoletes:      hyprland-nvidia-devel < 1:0.32.3-2
Provides:       hyprland-nvidia-devel = %{version}-%{release}
Obsoletes:      hyprland-legacyrenderer-devel < 0.49.0

%description    devel
%{summary}.

%prep
%autosetup -n hyprland-source -N
# Fedora names it lua.pc. The correct version is ensured in the BuildRequires section
sed -i 's/lua55/lua/g' CMakeLists.txt
%if 0%{?fedora} == 43
sed -i '/return (.* || std::ranges::starts_with(str_view, prefixes));/c\
    auto check = [&](auto prefix) { return std::string(str_view.begin(), str_view.end()).starts_with(prefix); };\
    return (... || check(prefixes));' src/helpers/MiscFunctions.cpp
%endif

cp -p subprojects/hyprland-protocols/LICENSE LICENSE-hyprland-protocols
cp -p subprojects/udis86/LICENSE LICENSE-udis86

sed -i \
  -e "s|@@HYPRLAND_VERSION@@|%{version}|g" \
  %{SOURCE4}

%build
%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DNO_TESTS=TRUE \
    -DBUILD_TESTING=FALSE
%cmake_build

%install
%cmake_install
install -Dpm644 %{SOURCE4} -t %{buildroot}%{_rpmconfigdir}/macros.d
rm -f %{buildroot}%{_datadir}/wayland-sessions/hyprland-uwsm.desktop

%files
%license LICENSE LICENSE-udis86 LICENSE-hyprland-protocols
%{_bindir}/[Hh]yprland
%{_bindir}/hyprctl
%{_bindir}/hyprpm
%{_bindir}/start-hyprland
%{_datadir}/hypr/
%{_datadir}/wayland-sessions/hyprland.desktop
%{_datadir}/xdg-desktop-portal/hyprland-portals.conf
%{_mandir}/man1/hyprctl.1*
%{_mandir}/man1/Hyprland.1*
%{bash_completions_dir}/hypr*
%{fish_completions_dir}/hypr*.fish
%{zsh_completions_dir}/_hypr*

%files devel
%{_datadir}/pkgconfig/hyprland.pc
%{_includedir}/hyprland/
%{_rpmconfigdir}/macros.d/macros.hyprland

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.56.2-1
- Initial packaging for Fedora Nexus (Nexus Optimized)