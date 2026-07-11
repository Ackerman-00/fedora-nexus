# Version of the .so library
%global abi_ver 0.20
# libliftoff does not bump soname on API changes
%global liftoff_ver 0.5.0

Name:           wlroots
Version:        0.20.2
Release:        1%{?dist}
Summary:        A modular Wayland compositor library

# Convert tilde to dash for source tag (e.g. 0.20.0~rc2 -> 0.20.0-rc2)
%global tag     %(v='%{version}'; echo "${v//'~'/-}")

License:        MIT
URL:            https://gitlab.freedesktop.org/wlroots/wlroots
Source0:        %{url}/-/releases/%{tag}/downloads/%{name}-%{tag}.tar.gz

# Fedora patches
# Following patch is required for phoc.
Patch:          Revert-layer-shell-error-on-0-dimension-without-anch.patch

BuildRequires:  gcc
BuildRequires:  glslang
BuildRequires:  meson >= 1.3

BuildRequires:  (pkgconfig(libliftoff) >= %{liftoff_ver} with pkgconfig(libliftoff) < 0.6)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm) >= 21.1
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libdisplay-info) >= 0.2.0
BuildRequires:  pkgconfig(libdrm) >= 2.4.129
BuildRequires:  pkgconfig(libinput) >= 1.21.0
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pixman-1) >= 0.46.0
BuildRequires:  pkgconfig(vulkan) >= 1.2.182
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.47
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server) >= 1.24.0
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-composite)
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-errors)
BuildRequires:  pkgconfig(xcb-ewmh)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-render)
BuildRequires:  pkgconfig(xcb-renderutil)
BuildRequires:  pkgconfig(xcb-res)
BuildRequires:  pkgconfig(xcb-shm)
BuildRequires:  pkgconfig(xcb-xfixes) >= 1.15
BuildRequires:  pkgconfig(xcb-xinput)
BuildRequires:  pkgconfig(xkbcommon) >= 1.8.0
BuildRequires:  pkgconfig(xwayland)
Requires:       libliftoff%{?_isa} >= %{liftoff_ver}

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} == %{version}-%{release}

%description    devel
Development files for %{name}.

%prep
%autosetup -N -n %{name}-%{tag}
%autopatch -p1 -M99

%build
MESON_OPTIONS=(
    -Dexamples=false
)

%{meson} "${MESON_OPTIONS[@]}"
%{meson_build}

%install
%{meson_install}

%check
%{meson_test}

%files
%license LICENSE
%doc README.md
%{_libdir}/libwlroots-%{abi_ver}.so

%files  devel
%{_includedir}/wlroots-%{abi_ver}/wlr
%{_libdir}/pkgconfig/wlroots-%{abi_ver}.pc

%changelog
* Sat Jul 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0.20.2-1
- Initial package of wlroots 0.20.2 for Fedora 43
