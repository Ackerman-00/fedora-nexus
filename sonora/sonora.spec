%global appid io.github.nolight132.sonora
# prebuilt binary: nothing to strip
%global debug_package %{nil}

Name:           sonora
Version:        0.50.1
Release:        1%{?dist}
Summary:        Native music streaming client

License:        GPL-3.0-or-later AND OFL-1.1 AND ISC AND MIT AND Apache-2.0 AND CC-BY-4.0
URL:            https://github.com/sonorahq/sonora
Source0:        %{url}/releases/download/v%{version}/sonora-v%{version}-x86_64-unknown-linux-gnu
# sha256: 1ab011a1b8b84b68fb8df039462da4700805629500b8f1181a2c8d6a6c6cba19
Source1:        %{url}/archive/refs/tags/v%{version}.tar.gz
# sha256: 43a5e36942b32d88e8e712ef2829d9e5db3a89a85fa32b2d9378f506c50c675e

ExclusiveArch:  x86_64

Requires:       hicolor-icon-theme
Requires(post): desktop-file-utils
Requires(post): gtk-update-icon-cache
Requires(postun): gtk-update-icon-cache
Recommends:     mesa-vulkan-drivers
Recommends:     pipewire-alsa

%description
Sonora is a native music streaming client, built with Rust and GPUI.
Stream from Apple Music, Spotify, YouTube Music, Deezer, Subsonic/Navidrome
and play local files — all in one app.

%prep
%setup -q -T -b 1

%install
install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/sonora

install -Dm644 assets/linux/sonora.desktop %{buildroot}%{_datadir}/applications/sonora.desktop
for s in 16x16 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    install -Dm644 assets/linux/icons/hicolor/$s/apps/sonora.png \
        %{buildroot}%{_datadir}/icons/hicolor/$s/apps/sonora.png
done
install -Dm644 assets/linux/sonora.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/sonora.svg

sed -e "s/@VERSION@/%{version}/" -e "s/@DATE@/$(date -u +%F)/" \
    flatpak/io.github.nolight132.sonora.metainfo.xml > %{appid}.metainfo.xml
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
%license THIRD-PARTY.md
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
* Tue Nov 17 UTC 2026 Ackerman-00 <no-reply> - 0.50.1-1
- Repackage the upstream prebuilt x86_64 binary
