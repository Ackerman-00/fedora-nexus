%global appid io.github.nolight132.sonora
# prebuilt binary: nothing to strip
%global debug_package %{nil}

Name:           sonora
Version:        0.51.0
Release:        2%{?dist}
Summary:        Native music streaming client

License:        GPL-3.0-or-later AND OFL-1.1 AND ISC AND MIT AND Apache-2.0 AND CC-BY-4.0
URL:            https://github.com/sonorahq/sonora
Source0:        %{url}/releases/download/v%{version}/sonora-v%{version}-x86_64-unknown-linux-gnu
# sha256: 5f5d19de73f6b2fcf001e5d412015bb7710fddecb54a6dc5599c4ffaaca455b1
Source1:        %{url}/archive/refs/tags/v%{version}.tar.gz
# sha256: af7b15060010f966630666214a21a1b7004c39d8c9a9c3e02e8510425960f5fa

ExclusiveArch:  x86_64

# dlopened by wgpu/wayland: invisible to autorequires
BuildRequires:  alsa-lib
BuildRequires:  libxcb
BuildRequires:  libxkbcommon
BuildRequires:  libxkbcommon-x11
Requires:       fontconfig
Requires:       hicolor-icon-theme
Requires:       libwayland-client
Requires:       libwayland-egl
Requires:       vulkan-loader
Requires(post): desktop-file-utils
Requires(post): gtk-update-icon-cache
Requires(postun): gtk-update-icon-cache
Recommends:     alsa-plugins-pulseaudio
Recommends:     mesa-vulkan-drivers
Recommends:     pipewire-alsa
Recommends:     webkit2gtk4.1

%description
Sonora is a native music streaming client, built with Rust and GPUI.
Stream from Apple Music, Spotify, YouTube Music, Deezer, Subsonic/Navidrome
and play local files - all in one app.

%prep
%setup -q -T -b 1

%build
install -m755 %{SOURCE0} sonora-cli
for sh in bash zsh fish; do
    ./sonora-cli completions "$sh" > "completion.$sh"
done

%install
install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/sonora

install -Dm644 assets/linux/sonora.desktop %{buildroot}%{_datadir}/applications/sonora.desktop
for icon in assets/linux/icons/hicolor/*/apps/sonora.png; do
    s=$(basename "$(dirname "$(dirname "$icon")")")
    install -Dm644 "$icon" %{buildroot}%{_datadir}/icons/hicolor/$s/apps/sonora.png
done
install -Dm644 assets/linux/sonora.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/sonora.svg

install -Dm644 completion.bash %{buildroot}%{_datadir}/bash-completion/completions/sonora
install -Dm644 completion.zsh %{buildroot}%{_datadir}/zsh/site-functions/_sonora
install -Dm644 completion.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/sonora.fish

sed -e "s/@VERSION@/%{version}/" -e "s/@DATE@/$(date -u +%F)/" \
    packaging/flatpak/%{appid}.metainfo.xml > %{appid}.metainfo.xml
install -Dm644 %{appid}.metainfo.xml %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

mkdir -p %{buildroot}%{_licensedir}/%{name}
install -Dm644 assets/icons/LICENSE %{buildroot}%{_licensedir}/%{name}/icons-LICENSE
install -Dm644 assets/icons/common/LICENSE %{buildroot}%{_licensedir}/%{name}/icons-common-LICENSE
install -Dm644 assets/icons/iconoir/LICENSE %{buildroot}%{_licensedir}/%{name}/icons-iconoir-LICENSE
install -Dm644 assets/icons/lucide/LICENSE %{buildroot}%{_licensedir}/%{name}/icons-lucide-LICENSE
install -Dm644 assets/icons/remix/LICENSE %{buildroot}%{_licensedir}/%{name}/icons-remix-LICENSE
install -Dm644 assets/icons/solar/LICENSE %{buildroot}%{_licensedir}/%{name}/icons-solar-LICENSE

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

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
%license docs/THIRD-PARTY.md
%license assets/fonts/LICENSE.txt
%{_licensedir}/%{name}/icons-LICENSE
%{_licensedir}/%{name}/icons-common-LICENSE
%{_licensedir}/%{name}/icons-iconoir-LICENSE
%{_licensedir}/%{name}/icons-lucide-LICENSE
%{_licensedir}/%{name}/icons-remix-LICENSE
%{_licensedir}/%{name}/icons-solar-LICENSE
%doc README.md
%doc CHANGELOG.md
%{_bindir}/sonora
%{_datadir}/applications/sonora.desktop
%{_datadir}/icons/hicolor/*/apps/sonora.png
%{_datadir}/icons/hicolor/scalable/apps/sonora.svg
%{_datadir}/bash-completion/completions/sonora
%{_datadir}/zsh/site-functions/_sonora
%{_datadir}/fish/vendor_completions.d/sonora.fish
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Sat Nov 28 2026 Ackerman-00 <no-reply> - 0.51.0-2
- Fix the metainfo path upstream moved to packaging/flatpak
- Ship docs/THIRD-PARTY.md, the 22x22 icon and the generated shell completions
- Declare the dlopened Vulkan, Wayland and fontconfig runtime deps

* Sat Nov 28 2026 Ackerman-00 <no-reply> - 0.51.0-1
- Repackage the upstream prebuilt x86_64 binary
