Name:           scenefx
Version:        0.5
Release:        3%{?dist}

Summary:        A drop-in replacement for the wlroots scene API for eye-candy effects
URL:            https://github.com/wlrfx/scenefx
License:        MIT
Packager:       Ackerman-00 <quietcraft@gmail.com>

Source0:        %{url}/archive/%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  glslang
BuildRequires:  meson >= 1.3

BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm) >= 17.1.0
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(libdrm) >= 2.4.129
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.41
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server) >= 1.24.0
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(xkbcommon) >= 1.8.0
BuildRequires:  pkgconfig(libglvnd)
BuildRequires:  pkgconfig(lcms2)

%description
%{summary}

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} == %{version}-%{release}
Suggests:       gcc
Suggests:       meson >= 0.58.0
Suggests:       pkgconfig(wayland-egl)

%description    devel
Development files for %{name}.

%prep
%autosetup -N

%build
MESON_OPTIONS=(
    -Dexamples=false
    -Dwerror=false
)
%meson "${MESON_OPTIONS[@]}"
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_libdir}/lib%{name}-*.so

%files  devel
%{_includedir}/%{name}-*/*
%{_libdir}/pkgconfig/%{name}-*.pc

%changelog
* Tue Oct 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.5-3
- Reconcile BuildRequires floors with upstream meson.build (meson >= 1.3,
  libdrm >= 2.4.129, pixman-1 >= 0.43.0, wayland-server >= 1.24.0,
  wayland-protocols >= 1.41, wlroots-0.20 >= 0.20.0) and pin auto-detected
  color-management with explicit pkgconfig(lcms2) (shipped 0.5-2 already
  linked liblcms2.so.2 via transitive luck)
* Mon Aug 03 2026 Ackerman-00 <quietcraft@gmail.com> - 0.5-2
- Add missing BuildRequires pkgconfig(xkbcommon) >= 1.8.0 (hard dependency in
  meson.build; previously resolved only via meson fallback)

* Wed Jul 08 2026 Ackerman-00 <quietcraft@gmail.com> - 0.5-1
- Auto-update to version 0.5
