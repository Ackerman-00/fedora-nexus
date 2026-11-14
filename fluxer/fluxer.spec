%global appid app.fluxer.Fluxer

%global __provides_exclude_from ^%{_libdir}/%{name}/.*$
%global __requires_exclude ^libffmpeg\\.so.*$|^libcbor\\.so.*$
%global __urlhelper_localopts --http1.1 --retry 5 --retry-all-errors --retry-delay 5

Name:           fluxer
Version:        2026.1114.41034
Release:        4%{?dist}
Summary:        Free and open source instant messaging and VoIP platform

License:        AGPL-3.0-or-later AND BSD-2-Clause AND BSD-3-Clause AND 0BSD AND LGPL-2.1-or-later AND Apache-2.0 AND IJG AND MIT AND GPL-2.0-or-later AND ISC AND OpenSSL AND (MPL-1.1 OR GPL-2.0-only OR LGPL-2.0-only)
URL:            https://fluxer.app
Source0:        https://pkgs.fluxer.com/desktop/stable/linux/x64/%{version}/rpm
# sha256: 6e850ee8d4ba56432c2e593780d1044cdd42e77ef5da8708b6bbc9ed8601418d

Requires:           hicolor-icon-theme
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libsecret
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       libXtst
Requires:       libuuid
Requires:       nss
Requires:       pipewire-libs
Requires:       pulseaudio-libs
Requires:       xdg-utils

%global _enable_debug_packages 0

%description
Fluxer is a free and open source instant messaging and VoIP platform built for
friends, groups, and communities. Self-hosting and more.

%prep
%setup -T -c
rpm2cpio %{SOURCE0} | cpio -idmv
if [ -d "opt/Fluxer Canary" ] && [ ! -e "opt/Fluxer" ]; then
  mv "opt/Fluxer Canary" "opt/Fluxer"
fi
if [ -d "opt/fluxer-canary" ] && [ ! -e "opt/Fluxer" ]; then
  mv "opt/fluxer-canary" "opt/Fluxer"
fi
if [ -d "opt/fluxer" ] && [ ! -e "opt/Fluxer" ]; then
  mv "opt/fluxer" "opt/Fluxer"
fi
if [ -f "usr/share/applications/app.fluxer.FluxerDesktop.desktop" ] && [ ! -f "usr/share/applications/fluxer.desktop" ]; then
  cp "usr/share/applications/app.fluxer.FluxerDesktop.desktop" "usr/share/applications/fluxer.desktop"
fi
if [ -f "usr/share/applications/fluxer-canary.desktop" ] && [ ! -f "usr/share/applications/fluxer.desktop" ]; then
  cp "usr/share/applications/fluxer-canary.desktop" "usr/share/applications/fluxer.desktop"
fi
if ls usr/share/icons/hicolor/*/apps/fluxer-canary.png >/dev/null 2>&1; then
  for f in usr/share/icons/hicolor/*/apps/fluxer-canary.png; do
    dst=$(echo "$f" | sed 's/fluxer-canary/fluxer/')
    [ -f "$dst" ] || cp "$f" "$dst"
  done
fi
if [ -f "opt/Fluxer/fluxer-canary" ] && [ ! -f "opt/Fluxer/fluxer" ]; then
  ln -s fluxer-canary "opt/Fluxer/fluxer"
fi

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
cp -a opt/Fluxer/* %{buildroot}%{_libdir}/%{name}/

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec %{_libdir}/%{name}/%{name} "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

install -Dm0644 usr/share/applications/fluxer.desktop \
    %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop

sed -i 's|^Exec=.*|Exec=%{_bindir}/%{name} %U|' \
    %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop
sed -i 's|^Icon=.*|Icon=%{appid}|' \
    %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop

for iconpath in opt/Fluxer/resources/icons/[0-9]*x[0-9]*.png; do
    size=$(basename "$iconpath" .png)
    install -Dm0644 "$iconpath" \
        %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/%{appid}.png
done

desktop-file-validate %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop || true

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license opt/Fluxer/LICENSE.electron.txt
%doc opt/Fluxer/LICENSES.chromium.html
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%attr(4755, root, root) %{_libdir}/%{name}/chrome-sandbox

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 2026.1114.41034-4
- Declare the three runtime libraries upstream's own RPM requires and we
  dropped (Release 3): libsecret (Chromium keyring, dlopened so rpm never sees
  it), pipewire-libs (WebRTC screen share on Wayland) and pulseaudio-libs
  (audio client). Without them the app launches with its keyring, screen-share
  and audio features silently degraded. Evidence: rpm -qp --requires of the
  upstream Fluxer-2026.1114.41034 rpm lists all three.

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 2026.1114.41034-3
- Move the in-app updater strip into %install

* Sat Nov 14 2026 Ackerman-00 <no-reply> - 2026.1114.41034-2
- Pin Source0 to the immutable versioned path so the sha256 receipt names the artifact it ships (the latest/ path is republished several times an hour)
