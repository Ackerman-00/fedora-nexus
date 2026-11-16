%global zooland_commit   bca0d3ce591d37ca3d670f20e4fd62ce25207148
%global shortcommit     4d6702e
%global gitdate         20261115145914
%global base_version    0.1.49

Name:           zoolander-git
Version:        %{base_version}+git%{gitdate}.%{shortcommit}
Release:        1%{?dist}
Summary:        Zoolander Wayland compositor, built from the git snapshot

License:        MIT
URL:            https://git.pika-os.com/otter-shell/zoolander
Source0:        https://git.pika-os.com/api/v1/repos/otter-shell/zoolander/archive/4d6702edcfccdb7b27650e2e994afd0c1099b478.tar.gz#/zoolander-4d6702edcfccdb7b27650e2e994afd0c1099b478.tar.gz
# sha256: 1b12da52728cbcc4d08a05d7ffb5ef641540edb8b3ac00c8deb89888c4ba00ef
Source1:        https://git.pika-os.com/api/v1/repos/otter-shell/zooland/archive/%{zooland_commit}.tar.gz#/zooland-%{zooland_commit}.tar.gz
# sha256: 875ffcfb34940e767b8e21445376ce1afecd1073e88aa09c54e6dfdd9222a4a9

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
BuildRequires:  libxcb-xfixes0-devel
BuildRequires:  libxcb-composite-devel
BuildRequires:  libxcb-sync-devel
BuildRequires:  libxcb-res-devel
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
BuildRequires:  libX11-xcb-devel

Requires:       xorg-x11-server-Xwayland
Requires:       libseat
Requires:       netcat
Requires:       libcap
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
cd otr-out
install -D -m 0755 zoolander %{buildroot}%{_bindir}/zoolander
install -D -m 0644 libzoolander_bell.so %{buildroot}%{_libdir}/zoolander/libzoolander_bell.so
install -D -m 0644 libzoolander_audio_visualizer.so %{buildroot}%{_libdir}/zoolander/libzoolander_audio_visualizer.so
install -D -m 0644 libVkLayer_zoolander_wsi.so %{buildroot}%{_libdir}/libVkLayer_zoolander_wsi.so
install -D -m 0644 zoolander_wsi.json %{buildroot}%{_datadir}/vulkan/implicit_layer.d/zoolander_wsi.x86_64.json
install -D -m 0755 ../zoolanderctl %{buildroot}%{_bindir}/zoolanderctl
install -D -m 0755 debian/zoolander-session %{buildroot}%{_bindir}/zoolander-session
sed -e 's|^Exec=/usr/local/bin/.*|Exec=/usr/bin/zoolander-session|' -e 's|^TryExec=/usr/local/bin/.*|TryExec=/usr/bin/zoolander-session|' ../zoolander.desktop > %{buildroot}%{_datadir}/wayland-sessions/zoolander.desktop
install -D -m 0644 ../zoolander-portals.conf %{buildroot}%{_datadir}/xdg-desktop-portal/zoolander-portals.conf
install -d %{buildroot}%{_datadir}/zoolander/config
install -m 0644 ../config/starter/*.lua %{buildroot}%{_datadir}/zoolander/config/


%post
if [ $1 -eq 1 ]; then
    if command -v setcap >/dev/null 2>&1; then
        if ! setcap cap_sys_nice+ep %{_bindir}/zoolander; then
            echo "zoolander: setcap cap_sys_nice+ep %{_bindir}/zoolander failed; the GPU queue stays at default priority" >&2
        fi
    else
        echo "zoolander: setcap not found (libcap); the GPU queue stays at default priority" >&2
    fi
fi
%files
%license LICENSE
%doc README.md
%{_bindir}/zoolander
%{_bindir}/zoolanderctl
%{_bindir}/zoolander-session
%{_datadir}/wayland-sessions/zoolander.desktop
%{_datadir}/xdg-desktop-portal/zoolander-portals.conf
%{_datadir}/zoolander/
%{_datadir}/vulkan/implicit_layer.d/zoolander_wsi.x86_64.json
%{_libdir}/zoolander/
%{_libdir}/libVkLayer_zoolander_wsi.so

%changelog
* Mon Nov 16 2026 Ackerman-00 <no-reply> - 0.1.49+git20261115145914.4d6702e-1
- Initial package, built from git snapshot
