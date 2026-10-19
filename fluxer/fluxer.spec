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
Version:        2026.1018.223338
Release:        2%{?dist}
Summary:        Free and open source instant messaging and VoIP platform

# License set proven from the pinned artifact (sha256 de3c4e3c...): the app
# itself declares AGPL-3.0-or-later (app.asar package.json), bundled npm deps
# add MIT/ISC/0BSD/(Apache-2.0 AND BSD-3-Clause), and the bundled Electron +
# Chromium runtime ships LICENSES.chromium.html, whose Fedora package
# (chromium.spec) is the reference for the rest of the expression. The previous
# "AGPL-3.0-or-later AND BSD" was invalid: bare BSD is not an SPDX identifier
# and is not in Fedora's fedora-spdx-licenses.toml (629 lines, 623 ids).
License:        AGPL-3.0-or-later AND BSD-2-Clause AND BSD-3-Clause AND 0BSD AND LGPL-2.1-or-later AND Apache-2.0 AND IJG AND MIT AND GPL-2.0-or-later AND ISC AND OpenSSL AND (MPL-1.1 OR GPL-2.0-only OR LGPL-2.0-only)
URL:            https://fluxer.app
Source0:        https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm
# Rolling "latest" URL: pin the hash of the served artifact so rebuilds and
# the sweep verify fixed bits. Refreshed by update.sh on every version bump.
# sha256: de3c4e3c0b4f543beb59aa57b92b3a7395b6f56b5ac34f379d22c12b46001e37

Requires:           hicolor-icon-theme
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
# Upstream Fluxer RPM ships as either "Fluxer" (stable), "Fluxer Canary"
# (canary, mixed case) or "fluxer-canary" (canary, lowercase, since 2026.919)
# with matching desktop/icon/binary names. Normalize to "Fluxer"/"fluxer" so the
# rest of the spec works for any channel.
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
# Automatically force native Wayland rendering if detected (same wrapper
# vesktop/stoat-desktop/heroic/splayer-next ship; upstream's fluxer-launcher
# passes no ozone flags, so without this Fluxer falls back to XWayland on
# Wayland sessions with blurry rendering and broken taskbar matching)
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec %{_libdir}/%{name}/%{name} "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

# Upstream renamed fluxer.desktop to app.fluxer.FluxerDesktop.desktop (2026.1004,
# normalized to fluxer.desktop in %prep). Install it under its upstream basename
# so StartupWMClass=app.fluxer.FluxerDesktop keeps matching the window - renaming
# the file would break taskbar matching.
install -Dm0644 usr/share/applications/fluxer.desktop \
    %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop

# Fix Exec= and Icon= for our relocation
sed -i 's|^Exec=.*|Exec=%{_bindir}/%{name} %U|' \
    %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop
sed -i 's|^Icon=.*|Icon=%{appid}|' \
    %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop

# Upstream hicolor set collapsed to a single 1024x1024 png, a bucket hicolor's
# index.theme does not declare (largest fixed size is 512x512), so Icon= never
# resolves. Install the bundled resources size set (16-512) into real buckets.
for iconpath in opt/Fluxer/resources/icons/[0-9]*x[0-9]*.png; do
    size=$(basename "$iconpath" .png)
    install -Dm0644 "$iconpath" \
        %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/%{appid}.png
done

desktop-file-validate %{buildroot}%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop || true

%files
%license opt/Fluxer/LICENSE.electron.txt
%doc opt/Fluxer/LICENSES.chromium.html
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/applications/app.fluxer.FluxerDesktop.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
# Electron aborts at startup ("SUID sandbox helper binary was found, but is
# not configured correctly", setuid_sandbox_host.cc:166) unless chrome-sandbox
# is SUID root 4755 - proven FATAL rc=133 as non-root under xvfb 2026-10-02;
# same fix vesktop/stoat-desktop already ship, matches Google Chrome's rpm.
%attr(4755, root, root) %{_libdir}/%{name}/chrome-sandbox

%changelog
* Mon Oct 19 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 2026.1018.223338-2
- Replace the invalid License: "AGPL-3.0-or-later AND BSD" with the real
  bundled license set. Bare "BSD" is not an SPDX identifier (Fedora's
  fedora-spdx-licenses.toml lists BSD-2-Clause/BSD-3-Clause/BSD-4-Clause but no
  bare BSD). Evidence from the pinned artifact (sha256 de3c4e3c...):
  app.asar's package.json declares AGPL-3.0-or-later, bundled npm deps add
  MIT/ISC/0BSD/(Apache-2.0 AND BSD-3-Clause), and the bundled Chromium runtime
  ships LICENSES.chromium.html covering BSD-2/3-Clause, IJG, Openssl, MPL-1.1
  and the GPL/LGPL family (chromium.spec is the Fedora reference wording).
* Mon Oct 19 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.1018.223338-1
- Update to version 2026.1018.223338
