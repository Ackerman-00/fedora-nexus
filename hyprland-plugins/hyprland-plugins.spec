%global commit0 00862ca3e2908857f9660adbba1b2d55796aaa43
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global bumpver 1
%global hyprland_ver 0.56.2

%global __provides_exclude_from ^(%{_libdir}/hyprland/.*\\.so)$

%global plugins %{shrink:
                borders-plus-plus
                csgo-vulkan-fix
                hyprbars
                hyprfocus
}

Name:           hyprland-plugins
Version:        0.1^%{bumpver}.git%{shortcommit0}
Release:        2%{?dist}
Summary:        Official plugins for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-plugins
Source:         %{url}/archive/%{commit0}/%{name}-%{commit0}.tar.gz
ExclusiveArch:  x86_64 aarch64
Packager:       Ackerman-00 <quietcraft@gmail.com>

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  hyprland-devel

Requires:       hyprland = %_hyprland_version

# print Recommends: for each plugin
%{lua:for w in rpm.expand('%plugins'):gmatch("%S+") do print("Recommends: hyprland-plugin-"..w..'\n') end}

%description
%{summary}.

%define _package() \%package -n hyprland-plugin-%1\
Summary:       %1 plugin for Hyprland\
Requires:      hyprland = %_hyprland_version\
\%description  -n hyprland-plugin-%1\
\%1 plugin for Hyprland.\
\%files -n     hyprland-plugin-%1\
\%%license LICENSE\
\%dir %{_libdir}/hyprland\
\%{_libdir}/hyprland/lib%1.so\

# expand %%_package for each plugin
%{lua:for w in rpm.expand('%plugins'):gmatch("%S+") do print(rpm.expand("%_package "..w)..'\n\n') end}

%prep
%autosetup -n hyprland-plugins-%{commit0}

%build
for plugin in %{plugins}
do
pushd $plugin
%cmake -DCMAKE_INSTALL_LIBDIR=%{_libdir}/hyprland
%cmake_build
popd
done

%install
for plugin in %{plugins}
do
pushd $plugin
%cmake_install
popd
done

%files

%changelog
* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1^1.git00862ca-2
- Rebuild: hyprland now available in COPR repo

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1^1.git00862ca-1
- Initial packaging for Fedora Nexus (Nexus Optimized)
- Builds against hyprland 0.56.2