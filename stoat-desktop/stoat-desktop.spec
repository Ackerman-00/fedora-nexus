# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}

# Prevent RPM from trying to auto-generate dependencies from the bundled Electron libraries
%global __requires_exclude_from ^/opt/Stoat/.*$
%global __provides_exclude_from ^/opt/Stoat/.*$

# Bundled prebuilt native modules carry build-machine RUNPATHs (Nix store paths)
# that trip check-rpaths error 0002; all NEEDED libs resolve from the system.
%global __brp_check_rpaths %{nil}

Name:           stoat-desktop
Version:        1.5.3
Release:        3%{?dist}
Summary:        Open source, user-first chat platform desktop client

License:        AGPL-3.0-only AND MIT AND BSD-2-Clause
URL:            https://github.com/stoatchat/for-desktop
Source0:        %{url}/releases/download/v%{version}/Stoat-linux-x64-%{version}.zip
Source1:        stoat-desktop.desktop
Source2:        stoat.png
Source3:        chat.stoat.StoatDesktop.metainfo.xml

ExclusiveArch:  x86_64

BuildRequires:  unzip

Requires:       gtk3
Requires:       nss
Requires:       at-spi2-core
Requires:       cups-libs
Requires:       dbus-libs
Requires:       systemd-libs
Requires:       libX11
Requires:       libxcb
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXext
Requires:       libXfixes
Requires:       libXrandr
Requires:       libxkbcommon
Requires:       mesa-libgbm
Requires:       pipewire-libs
Requires:       alsa-lib
Requires:       libsecret
Requires:       libappindicator-gtk3
Requires:       xdg-utils

%description
Stoat is an open source, user-first chat platform. Send messages, share
images, mention users, and join voice channels — all from a native desktop
application. Packaged from the upstream pre-built Electron bundle for the
Nexus repository.

%prep
%setup -q -c -T -n %{name}-%{version}
unzip -q %{SOURCE0}

%build
# No compilation required for pre-built binaries

%install
rm -rf %{buildroot}

# 1. Install the main application folder
install -d -m 0755 %{buildroot}/opt/Stoat
cp -a Stoat-linux-x64/* %{buildroot}/opt/Stoat/

# 2. Install desktop entry, icon and metainfo
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/chat.stoat.StoatDesktop.desktop
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/chat.stoat.StoatDesktop.png
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_datadir}/metainfo/chat.stoat.StoatDesktop.metainfo.xml

# 3. Create the Wayland-aware wrapper script
install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/stoat-desktop
#!/bin/sh
# Automatically force native Wayland rendering if detected
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
fi
exec /opt/Stoat/stoat-desktop "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/stoat-desktop

%files
%{_bindir}/stoat-desktop
%{_datadir}/applications/chat.stoat.StoatDesktop.desktop
%{_datadir}/icons/hicolor/256x256/apps/chat.stoat.StoatDesktop.png
%{_datadir}/metainfo/chat.stoat.StoatDesktop.metainfo.xml
/opt/Stoat/
# Enforce strict sandbox permissions natively
%attr(4755, root, root) /opt/Stoat/chrome-sandbox

%changelog
* Thu Aug 21 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.5.3-3
- Rebuild for COPR (spec validation fix)

* Tue Aug 18 2026 Ackerman-00 <quietcraft@gmail.com> - 1.5.2-3
- Fix build: disable check-rpaths for bundled prebuilt native module
  (node-pipewire index.node carries Nix-store RUNPATH; all NEEDED libs
  resolve from the system).
- Add Requires: pipewire-libs (needed by bundled node-pipewire voice module).

* Thu Aug 06 2026 Ackerman-00 <quietcraft@gmail.com> - 1.4.2-2
- Fix %install: use install -Dpm for desktop/metainfo to create parent dirs

* Wed Aug 05 2026 Ackerman-00 <quietcraft@gmail.com> - 1.4.2-1
- Initial package# Re-triggered rebuild for COPR SRPM-import outage on 2026-08-18 (spec unchanged).
