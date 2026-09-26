Name:           hyprland-protocols
Version:        0.7.1
Release:        3%{?dist}
Summary:        Wayland protocol extensions for Hyprland
BuildArch:      noarch
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-protocols
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  cmake

%description
%{summary}.

%package        devel
Summary:        Wayland protocol extensions for Hyprland
Requires:       %{name} = %{version}-%{release}

%description    devel
%{summary}.

%prep
%autosetup -p1

%build
# Upstream 0.7.1 dropped meson.build (CMake-only now, see upstream README
# "Building": cmake -S . -B ./build). The old meson build command failed
# with "Neither source directory ... contain a build file meson.build"
# (COPR 10988487). NOTE: never write a macro token in a comment - rpm
# macro-expands comment lines, and with meson-srpm-macros installed the
# meson build macro expansion injects shell commands into the build
# script (rpmbuild died with: syntax error near unexpected token `(').
%cmake
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_datadir}/pkgconfig/%{name}.pc
%{_datadir}/%{name}/

%files devel

%changelog
* Sat Sep 26 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.1-3
- Remove the macro token from the %build comment: rpm macro-expands comment
  lines, so whenever meson-srpm-macros is present in the environment the
  commented meson build command expanded into real shell lines and rpmbuild
  failed with "syntax error near unexpected token `('" before %cmake ran.
  COPR's minimal buildroot (cmake only) passed only by luck.
* Tue Sep 15 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.1-2
- Switch to CMake: upstream 0.7.1 removed meson.build (CMake-only build,
  COPR 10988487 failed with "Neither source directory ... contain a build
  file meson.build").
* Tue Sep 15 2026 Nexus Auto-Updater <bot@github.com> - 0.7.1-1
- Update to version 0.7.1

* Mon Aug 17 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.0-2
- Ship protocol definitions and pc file in the main package so `dnf install hyprland-protocols` works.
- Keep devel subpackage as compat wrapper.
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.7.0-1
- Initial packaging for Fedora Nexus (Nexus Optimized)