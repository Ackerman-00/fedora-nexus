# These will be automatically populated by update.sh
%global commit          d8ba5a01cac5ba8617bf262249829b4aa5945369
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260823001909
%global upstreamname    noctalia

Name:           noctalia-git
Version:        5.0.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        A sleek, customizable desktop shell crafted for Wayland

License:        MIT
URL:            https://github.com/noctalia-dev/%{upstreamname}
Source0:        %{url}/archive/%{commit}/%{upstreamname}-%{commit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  desktop-file-utils
BuildRequires:  json-devel
BuildRequires:  md4c-devel
BuildRequires:  pipewire-devel
BuildRequires:  sdbus-cpp-devel
BuildRequires:  stb_image_resize2-devel
BuildRequires:  stb_image_write-devel
BuildRequires:  tomlplusplus-devel
BuildRequires:  wireplumber-devel
BuildRequires:  jemalloc-devel
BuildRequires:  libical-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libsecret-devel
BuildRequires:  libsodium-devel
BuildRequires:  libjxl-devel
BuildRequires:  libqalculate-devel
BuildRequires:  libEGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_threads)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libsecret-1)
BuildRequires:  pkgconfig(libsodium)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(md4c)
BuildRequires:  pkgconfig(pam)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(polkit-agent-1)
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(sdbus-c++)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wireplumber-0.5)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       hicolor-icon-theme
Requires:       dejavu-sans-fonts
Requires:       libwebp

Recommends:     ddcutil
Recommends:     gpu-screen-recorder
Recommends:     power-profiles-daemon

Provides:       desktop-notification-daemon
Provides:       PolicyKit-authentication-agent
Conflicts:      noctalia

%description
A sleek, customizable desktop shell crafted for Wayland.
Compiled specifically for the Nexus repository via automated Git snapshot.

%prep
%autosetup -n %{upstreamname}-%{commit}
# Manually insert commit hash
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

%build
%meson
%meson_build

%install
%meson_install
install -d %{buildroot}%{_licensedir}/%{name}/third_party
find third_party -type f \( -name "LICENSE*" -o -name "COPYING*" -o -name "NOTICE*" \) | while read -r file; do
    dest_dir="%{buildroot}%{_licensedir}/%{name}/$(dirname "$file")"
    install -d "$dest_dir"
    install -p -m 0644 "$file" "$dest_dir/"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.noctalia.Noctalia.desktop

%files
%doc README.md
%license LICENSE
%{_licensedir}/%{name}/third_party/
%{_bindir}/noctalia
%{_datadir}/noctalia/
%{_datadir}/applications/dev.noctalia.Noctalia.desktop
%{_datadir}/icons/hicolor/scalable/apps/noctalia.svg

%changelog
* Sun Aug 23 2026 Ackerman-00 <quietcraft@gmail.com> - 5.0.0^20260823001909gitd8ba5a0-1
- Nightly sync with upstream main branch (Commit: d8ba5a0)
