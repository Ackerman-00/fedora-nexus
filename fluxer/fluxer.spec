%global appid app.fluxer.Fluxer

# Fluxer ships a private copy of the Electron/Chromium runtime under
# %%{_libdir}/fluxer. Those bundled .so files must never be advertised as
# system-wide Provides (they would let dnf pick fluxer as the provider of
# e.g. libvulkan.so.1 for unrelated packages), nor must their internal
# linkage become system Requires.
%global __provides_exclude_from ^%{_libdir}/%{name}/.*$
# With the bundled Provides pruned, the only auto-Requires that used to be
# satisfied by fluxer itself (libffmpeg.so, an Electron-private library, and
# libcbor.so.0.8 bundled under resources/app.asar.unpacked) must be dropped
# too, otherwise the package becomes uninstallable. All other auto-generated
# Requires are real system libraries and are kept.
%global __requires_exclude ^libffmpeg\\.so.*$|^libcbor\\.so.*$

Name:           fluxer
Version:        2026.904.135113
Release:        1%{?dist}
Summary:        Free and open source instant messaging and VoIP platform

License:        AGPL-3.0-or-later AND BSD
URL:            https://fluxer.app
Source0:        https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm

Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       libXtst
Requires:       libuuid
Requires:       nss
Requires:       xdg-utils

%global _enable_debug_packages 0

%description
Fluxer is a free and open source instant messaging and VoIP platform built for
friends, groups, and communities. Self-hosting and more.

%prep
%setup -T -c
rpm2cpio %{SOURCE0} | cpio -idmv
# Upstream Fluxer RPM ships as either "Fluxer" (stable) or "Fluxer Canary" (canary)
# with matching desktop/icon/binary names. Normalize to "Fluxer"/"fluxer" so the
# rest of the spec works for either channel.
if [ -d "opt/Fluxer Canary" ] && [ ! -e "opt/Fluxer" ]; then
  mv "opt/Fluxer Canary" "opt/Fluxer"
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
# Binary is fluxer (stable) or fluxer-canary (canary); ensure %{name} exists
if [ -f "opt/Fluxer/fluxer-canary" ] && [ ! -f "opt/Fluxer/fluxer" ]; then
  ln -s fluxer-canary "opt/Fluxer/fluxer"
fi

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
cp -a opt/Fluxer/* %{buildroot}%{_libdir}/%{name}/

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/sh
exec %{_libdir}/%{name}/%{name} "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

install -Dm0644 usr/share/applications/fluxer.desktop \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop

# Fix Exec= and Icon= for our relocation
sed -i 's|^Exec=.*|Exec=%{_bindir}/%{name} %U|' \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop
sed -i 's|^Icon=.*|Icon=%{appid}|' \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop

# Install all available icon sizes
for iconpath in usr/share/icons/hicolor/*/apps/fluxer.png; do
    size=$(echo "$iconpath" | cut -d/ -f5)
    install -Dm0644 "$iconpath" \
        %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/%{appid}.png
done

desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop || true

%files
%license opt/Fluxer/LICENSE.electron.txt
%doc opt/Fluxer/LICENSES.chromium.html
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png

%changelog
* Fri Sep 04 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.904.135113-1
- Update to version 2026.904.135113
