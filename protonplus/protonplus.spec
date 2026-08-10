%global tag         v0.6.2
%global app_id      com.vysp3r.ProtonPlus
%global forgeurl    https://github.com/vysp3r/ProtonPlus
%forgemeta
%undefine distprefix

Name:           protonplus
Version:        %{fileref}
Release:        1%{?dist}
Summary:        A modern compatibility tools manager
ExclusiveArch:  x86_64

License:        GPL-3.0-or-later
URL:            https://protonplus.vysp3r.com
Source0:        %{forgesource}

BuildRequires:  gettext
BuildRequires:  meson >= 1.0.0
BuildRequires:  vala
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  pkgconfig(appstream)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.6
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(sdl3) >= 3.2.0

Requires:       hicolor-icon-theme
Requires:       vulkan-loader
Requires:       which

%description
ProtonPlus is a modern compatibility tools manager for Linux. It allows you to easily manage and update various compatibility tools like Proton, Wine, DXVK, and VKD3D across different launchers.

%prep
%forgeautosetup

%build
%meson
%meson_build

%install
%meson_install
%find_lang %{app_id}

%check
%meson_test

%files -f %{app_id}.lang
%license LICENSE.md
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/glib-2.0/schemas/%{app_id}.gschema.xml
%{_datadir}/icons/hicolor/*/apps/%{app_id}.png
%{_metainfodir}/%{app_id}.metainfo.xml

%changelog
* Mon Aug 10 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.2-1
- Update to upstream 0.6.2
- The auto-updater had picked up the intermediate tag v0.6.1-1, whose dash is an
  illegal character in an RPM Version, so COPR could not even parse the spec
  (build 10841179: "line 8: Illegal char '-' (0x2d) in: Version: 0.6.1-1")
- Add an update.sh that skips tags which are not plain dotted versions, so the
  generic scanner can never wedge this package again

* Sun Aug 09 2026 Ackerman-00 <quietcraft@gmail.com> - 0.6.0-2
- Add missing BuildRequires for upstream 0.6.0 (sdl3, appstream, cairo,
  gio-unix-2.0, libnotify); the auto-updater bumped the tag but the build
  failed because meson could not find these new dependencies
- Replace %autorelease with an explicit Release so the NVR changed
