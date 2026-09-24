%global debug_package %{nil}
%global crate sonora
%global appid io.github.nolight132.sonora

Name:           sonora
Version:        0.39.0
Release:        1%{?dist}
Summary:        Native music streaming client
# Workspace is GPL-3.0-or-later; the binary embeds the Inter typeface
# (OFL-1.1) and four icon packs (Lucide ISC, Iconoir MIT, Remix Apache-2.0,
# Solar CC-BY-4.0) via include_bytes — see README "License" + THIRD-PARTY.md.
License:        GPL-3.0-or-later AND OFL-1.1 AND ISC AND MIT AND Apache-2.0 AND CC-BY-4.0
URL:            https://github.com/sonorahq/sonora
Source0:        https://github.com/sonorahq/sonora/archive/refs/tags/v%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  gcc-c++
# .cargo/config.toml passes -fuse-ld=mold on x86_64 (see CLAUDE.md "Building").
BuildRequires:  mold
# Git deps (sonorahq/gpui fork, ytmusic-rs, librespot/rodio patches) are
# locked in Cargo.lock but fetched at build time — cargo needs git.
BuildRequires:  git
BuildRequires:  pkgconf-pkg-config
# opusic-sys (Opus codec, audio stack) configures its bundled build with the
# cmake binary — proven by COPR F45 build 10999320 ("is `cmake` not installed?").
# Upstream docs omit it (their CI/dev boxes already carry it); not optional here.
BuildRequires:  cmake
# Native deps from upstream CLAUDE.md "Building" (Fedora set) + flatpak
# manifest: GPUI links x11/xcb/xkb/wayland/vulkan/fontconfig/freetype,
# cpal/rodio need alsa, rusqlite links system sqlite (non-Windows),
# widevine shim.cc compiles via the cc crate (needs gcc-c++ above).
BuildRequires:  alsa-lib-devel
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  sqlite-devel
BuildRequires:  libX11-devel
BuildRequires:  libxcb-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXi-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  libxkbcommon-x11-devel
BuildRequires:  wayland-devel
BuildRequires:  vulkan-loader-devel
BuildRequires:  dbus-devel

Requires:       hicolor-icon-theme
Requires(post): desktop-file-utils
Requires(post): gtk-update-icon-cache
Requires(postun): gtk-update-icon-cache
# GPUI is Vulkan-based: the ICD is a runtime requirement, loaded (not linked).
# Weak dep: default dnf installs it, NVIDIA-only boxes may drop it.
Recommends:     mesa-vulkan-drivers
# ALSA bridge for the sound server (AUR sonora note).
Recommends:     pipewire-alsa

%description
Sonora is a native music streaming client, built with Rust and GPUI.
Stream from Apple Music, Spotify, YouTube Music, Deezer, Subsonic/Navidrome
and play local files — all in one app.

%prep
%setup -q -n %{crate}-%{version}

%build
# Plain --release keeps Cargo's no-debuginfo default, hence debug_package
# nil above (matugen pattern). --locked pins the git deps (gpui fork etc.).
export CARGO_NET_OFFLINE=false
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked --package sonora

%install
install -Dm755 target/release/sonora %{buildroot}%{_bindir}/sonora

install -Dm644 assets/linux/sonora.desktop %{buildroot}%{_datadir}/applications/sonora.desktop
for s in 16x16 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    install -Dm644 assets/linux/icons/hicolor/$s/apps/sonora.png \
        %{buildroot}%{_datadir}/icons/hicolor/$s/apps/sonora.png
done
install -Dm644 assets/linux/sonora.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/sonora.svg

# Metainfo carries @VERSION@/@DATE@ placeholders (flatpak does the same).
sed -e "s/@VERSION@/%{version}/" -e "s/@DATE@/$(date -u +%F)/" \
    flatpak/io.github.nolight132.sonora.metainfo.xml > %{appid}.metainfo.xml
install -Dm644 %{appid}.metainfo.xml %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

%post
/usr/bin/update-desktop-database > /dev/null 2>&1 || :
/bin/touch --no-create %{_datadir}/icons/hicolor > /dev/null 2>&1 || :

%postun
/usr/bin/update-desktop-database > /dev/null 2>&1 || :
case "$1" in
    0)
        /bin/touch --no-create %{_datadir}/icons/hicolor > /dev/null 2>&1
        /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor > /dev/null 2>&1 || :
        ;;
esac

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor > /dev/null 2>&1 || :

%files
%license COPYING
%license THIRD-PARTY.md
%license assets/fonts/LICENSE.txt
%license assets/icons/LICENSE
%license assets/icons/common/LICENSE
%license assets/icons/iconoir/LICENSE
%license assets/icons/lucide/LICENSE
%license assets/icons/remix/LICENSE
%license assets/icons/solar/LICENSE
%doc README.md
%doc CHANGELOG.md
%{_bindir}/sonora
%{_datadir}/applications/sonora.desktop
%{_datadir}/icons/hicolor/16x16/apps/sonora.png
%{_datadir}/icons/hicolor/24x24/apps/sonora.png
%{_datadir}/icons/hicolor/32x32/apps/sonora.png
%{_datadir}/icons/hicolor/48x48/apps/sonora.png
%{_datadir}/icons/hicolor/64x64/apps/sonora.png
%{_datadir}/icons/hicolor/128x128/apps/sonora.png
%{_datadir}/icons/hicolor/256x256/apps/sonora.png
%{_datadir}/icons/hicolor/512x512/apps/sonora.png
%{_datadir}/icons/hicolor/scalable/apps/sonora.svg
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Thu Sep 24 2026 Ackerman-00 <quietcraft@gmail.com> - 0.39.0-1
- Auto-update to upstream stable release v0.39.0
