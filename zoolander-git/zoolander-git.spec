%global zooland_commit   5f4bf9a9309e6eab5f12246fdf0df7ef5b4044e0
%global shortcommit     19e99c0
%global gitdate         20261126121034
%global base_version    0.1.52

Name:           zoolander-git
Version:        %{base_version}+git%{gitdate}.%{shortcommit}
Release:        1%{?dist}
Summary:        Zoolander Wayland compositor, built from the git snapshot

License:        MIT
URL:            https://git.pika-os.com/otter-shell/zoolander
Source0:        https://git.pika-os.com/api/v1/repos/otter-shell/zoolander/archive/19e99c00e2e20ac74696c2515caa2dd7d2a29374.tar.gz#/zoolander-19e99c00e2e20ac74696c2515caa2dd7d2a29374.tar.gz
# sha256: 8e54ad30fd47005ddf96cb45d7883e2040e9fcc66362c80bff006f29e9968b71
Source1:        https://git.pika-os.com/api/v1/repos/otter-shell/zooland/archive/5f4bf9a9309e6eab5f12246fdf0df7ef5b4044e0.tar.gz#/zooland-5f4bf9a9309e6eab5f12246fdf0df7ef5b4044e0.tar.gz
# sha256: 47b09288c2209607b4f957742f880f137044454c226368d6e96f8041f0eb6f97

# built by the otr toolchain over mold: no build-id note to link
%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0
%global _build_id_links none

# Private lib provides
%global __provides_exclude_from ^%{_prefix}/lib/zoolander/.*$

ExclusiveArch:  x86_64

BuildRequires:  otr
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  git
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  libdrm-devel
BuildRequires:  libgbm-devel
BuildRequires:  libinput-devel
BuildRequires:  libseat-devel
BuildRequires:  libudev-devel
BuildRequires:  libxcb-devel
BuildRequires:  freetype-devel
BuildRequires:  harfbuzz-devel
BuildRequires:  fontconfig-devel
BuildRequires:  fribidi-devel
BuildRequires:  gdk-pixbuf2-devel
BuildRequires:  cairo-devel
BuildRequires:  libxkbcommon-devel >= 1.5.0
BuildRequires:  wayland-devel
BuildRequires:  xorg-x11-server-Xwayland
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  libX11-devel

Requires:       xorg-x11-server-Xwayland
Requires:       libseat
Requires:       netcat
Requires:       kmscon
Requires:       kitty
Requires:       zoolander-settings-git
Conflicts:      zoolander
Recommends:     mesa-vulkan-drivers

%description
Zoolander is a Wayland compositor built on the sibling zooland library:
nested, headless and DRM backends, rootless Xwayland, a native overview,
spatial window layouts, server-side decorations and a local control socket.
Configured in Lua; see the bundled starter config and the project docs.
Built from the git snapshot for the Nexus repository.

%prep
tar -xzf %{SOURCE0}
tar -xzf %{SOURCE1}

%build
cd zoolander
sh vendor/fetch-luajit.sh

mkdir -p otr-out
cd otr-out
otr build ../otr/native_main.otr --release --cpu baseline \
    -rpath '$ORIGIN/../lib/zoolander' -o zoolander
otr build ../otr/bell_player.otr ../otr/bell_audio_ffi.c --release --cpu baseline \
    --lib shared --pkg-config libpipewire-0.3 -I .. -o libzoolander_bell.so
otr build ../otr/audio_visualizer/capture_lib.otr ../otr/bell_audio_ffi.c ../otr/audio_visualizer/capture_ffi.c --release --cpu baseline \
    --lib shared --pkg-config libpipewire-0.3 -I .. -o libzoolander_audio_visualizer.so
otr build ../wsi/layer.otr --release --cpu baseline --lib shared \
    -l wayland-client -l xcb -l X11-xcb -o libVkLayer_zoolander_wsi.so
otr run ../wsi/manifest.otr -- %{_libdir}/libVkLayer_zoolander_wsi.so > zoolander_wsi.json

%install
cd zoolander/otr-out
install -D -m 0755 zoolander %{buildroot}%{_bindir}/zoolander
install -D -m 0644 libzoolander_bell.so %{buildroot}%{_prefix}/lib/zoolander/libzoolander_bell.so
install -D -m 0644 libzoolander_audio_visualizer.so %{buildroot}%{_prefix}/lib/zoolander/libzoolander_audio_visualizer.so
install -D -m 0644 libVkLayer_zoolander_wsi.so %{buildroot}%{_libdir}/libVkLayer_zoolander_wsi.so
install -D -m 0644 zoolander_wsi.json %{buildroot}%{_datadir}/vulkan/implicit_layer.d/zoolander_wsi.x86_64.json
install -D -m 0755 ../zoolanderctl %{buildroot}%{_bindir}/zoolanderctl
install -D -m 0755 ../debian/zoolander-session %{buildroot}%{_bindir}/zoolander-session
# F45 kmscon DRM master
cat > /tmp/zoolander-session-guard <<'ZSguard'
# Zoolander session identity (settings app checks this)
export XDG_CURRENT_DESKTOP=Zoolander
export XDG_SESSION_DESKTOP=Zoolander
if [ -z "${WAYLAND_DISPLAY:-}" ] && [ -z "${DISPLAY:-}" ] &&
   [ -n "${XDG_VTNR:-}" ] && [ "${ZOOLANDER_KMS_GUI:-}" != 1 ] &&
   command -v kmscon-launch-gui >/dev/null 2>&1 &&
   systemctl is-active --quiet "kmsconvt@tty${XDG_VTNR}.service" 2>/dev/null; then
    ZOOLANDER_KMS_GUI=1 exec kmscon-launch-gui "$0" "$@"
fi
ZSguard
awk '/^\/usr\/bin\/zoolander "\$@"/ && !done {while ((getline l < "/tmp/zoolander-session-guard") > 0) print l; done=1} {print}' \
    %{buildroot}%{_bindir}/zoolander-session > /tmp/zs.new
install -m 0755 /tmp/zs.new %{buildroot}%{_bindir}/zoolander-session
install -d %{buildroot}%{_datadir}/wayland-sessions
sed -e 's|^Exec=/usr/local/bin/.*|Exec=/usr/bin/zoolander-session|' -e 's|^TryExec=/usr/local/bin/.*|TryExec=/usr/bin/zoolander-session|' ../zoolander.desktop > %{buildroot}%{_datadir}/wayland-sessions/zoolander.desktop
install -D -m 0644 ../zoolander-portals.conf %{buildroot}%{_datadir}/xdg-desktop-portal/zoolander-portals.conf
install -d %{buildroot}%{_datadir}/zoolander/config
install -m 0644 ../config/starter/*.lua %{buildroot}%{_datadir}/zoolander/config/
# Working terminal keybind, raw XKB keysym for Return
sed -i -e 's|zl.exec_command("otter-term")|zl.exec_command("kitty")|' \
       -e 's|zl.KEY_RETURN|0xff0d|' \
    %{buildroot}%{_datadir}/zoolander/config/keybinds.lua
# Drop Otter autostart block (otter-shell not packaged here)
sed -i '/-- Without a shell profile/,/^end$/d' %{buildroot}%{_datadir}/zoolander/config/init.lua


%files
%license zoolander/LICENSE
%doc zoolander/README.md
%caps(cap_sys_nice+ep) %{_bindir}/zoolander
%{_bindir}/zoolanderctl
%{_bindir}/zoolander-session
%{_datadir}/wayland-sessions/zoolander.desktop
%{_datadir}/xdg-desktop-portal/zoolander-portals.conf
%{_datadir}/zoolander/
%{_datadir}/vulkan/implicit_layer.d/zoolander_wsi.x86_64.json
%{_prefix}/lib/zoolander/
%{_libdir}/libVkLayer_zoolander_wsi.so

%post
if [ "$1" -eq 1 ]; then
    echo
    echo "  Zoolander installed."
    echo "  Documentation: https://docs.otter-shell.org/zoolander/overview"
    echo
fi

%changelog
* Thu Nov 26 2026 Ackerman-00 <no-reply> - 0.1.52+git20261126121034.19e99c0-1
- Nightly sync with upstream main branch (Commit: 19e99c0)
