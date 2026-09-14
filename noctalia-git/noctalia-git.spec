# These will be automatically populated by update.sh
%global commit          2856ec3b1b384f243770240261a11831de51a923
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitdate         20260914124122
%global upstreamname    noctalia

Name:           noctalia-git
Version:        5.1.0^%{gitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        A sleek, customizable desktop shell crafted for Wayland

License:        Apache-2.0 AND MIT AND BSD-3-Clause AND HPND-sell-variant AND LGPL-2.1-or-later
URL:            https://github.com/noctalia-dev/%{upstreamname}
Source0:        %{url}/archive/%{commit}/%{upstreamname}-%{commit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  desktop-file-utils
# NOTE: deliberately NO dbus-daemon BuildRequires. Upstream meson.build
# registers upower_charge_limit_integration ONLY when dbus-run-session exists,
# and that test segfaults (SIGSEGV) in the mock chroot (COPR build 10982843:
# 118/119 OK, only the dbus-gated integration test FAILs). Fedora official
# noctalia.spec likewise omits dbus-daemon, so the test stays unregistered
# and the remaining 118 tests run green.
BuildRequires:  pipewire-devel
BuildRequires:  stb_image_resize2-devel
BuildRequires:  stb_image_write-devel
BuildRequires:  jemalloc-devel
BuildRequires:  libical-devel
BuildRequires:  libqalculate-devel
BuildRequires:  libEGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-ft)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_threads)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libsecret-1) >= 0.20
BuildRequires:  pkgconfig(libsodium) >= 1.0.18
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libwebpdemux)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(md4c)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(pam)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pangoft2)
BuildRequires:  pkgconfig(polkit-agent-1)
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(sdbus-c++)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wireplumber-0.5)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       hicolor-icon-theme
Requires:       dejavu-sans-fonts
Requires:       libwebp
# Noctalia segfaults at startup if it cannot connect to the pipewire daemon
# (cf. Fedora official noctalia.spec).
Requires:       pipewire
# The plugin system shells out to git at runtime (src/scripting/plugin_git.cpp).
Requires:       git-core

Recommends:     ddcutil
Recommends:     gpu-screen-recorder
Recommends:     power-profiles-daemon
# Noctalia talks to org.freedesktop.UPower AND org.freedesktop.UPower.PowerProfiles.
Recommends:     upower

Provides:       desktop-notification-daemon
Provides:       PolicyKit-authentication-agent
Conflicts:      noctalia

# Upstream does not offer a mechanism for building against system
# copies of these libraries (cf. Fedora official noctalia.spec).
Provides:       bundled(fzy)
Provides:       bundled(luau)
Provides:       bundled(material_color_utilities)
Provides:       bundled(wuffs)

%description
A sleek, customizable desktop shell crafted for Wayland.
Compiled specifically for the Nexus repository via automated Git snapshot.

%prep
%autosetup -n %{upstreamname}-%{commit}
# Manually insert commit hash
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

# Remove shebangs and execute permissions from template apply scripts to avoid
# rpmlint errors/warnings (cf. Fedora official noctalia.spec).
find assets/templates -type f -name '*.sh' \
    -exec sed -e '1 {/^#!/d}' -i '{}' + \
    -exec chmod -x '{}' +

%build
%meson -Dtests=enabled
%meson_build

%install
%meson_install

# Shell completions (cf. Fedora official noctalia.spec).
install -d -m 0755 %{buildroot}%{_datadir}/bash-completion/completions
%{buildroot}%{_bindir}/noctalia completions bash > %{buildroot}%{_datadir}/bash-completion/completions/noctalia
install -d -m 0755 %{buildroot}%{_datadir}/fish/vendor_completions.d
%{buildroot}%{_bindir}/noctalia completions fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/noctalia.fish
install -d -m 0755 %{buildroot}%{_datadir}/zsh/site-functions
%{buildroot}%{_bindir}/noctalia completions zsh > %{buildroot}%{_datadir}/zsh/site-functions/_noctalia

install -d %{buildroot}%{_licensedir}/%{name}/third_party
find third_party -type f \( -name "LICENSE*" -o -name "COPYING*" -o -name "NOTICE*" \) | while read -r file; do
    dest_dir="%{buildroot}%{_licensedir}/%{name}/$(dirname "$file")"
    install -d "$dest_dir"
    install -p -m 0644 "$file" "$dest_dir/"
done

%check
%meson_test
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.noctalia.Noctalia.desktop

%files
%license LICENSE
%doc README.md
%{_licensedir}/%{name}/third_party/
%{_bindir}/noctalia
%{_datadir}/noctalia/
%{_datadir}/applications/dev.noctalia.Noctalia.desktop
%{_datadir}/icons/hicolor/scalable/apps/noctalia.svg
%{_datadir}/bash-completion/completions/noctalia
%{_datadir}/fish/vendor_completions.d/noctalia.fish
%{_datadir}/zsh/site-functions/_noctalia

%changelog
* Mon Sep 14 2026 Ackerman-00 <quietcraft@gmail.com> - 5.1.0^20260914124122git2856ec3-1
- Nightly sync with upstream main branch (Commit: 2856ec3)
