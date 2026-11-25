%global debug_package %{nil}
%global __strip /bin/true
%global __requires_exclude_from ^%{_prefix}/lib/OpenClaw/desktop-runtime/bin/bun$
%global __provides_exclude_from ^%{_prefix}/lib/OpenClaw/desktop-runtime/bin/bun$

Name:           openclaw-desktop
Version:        2026.11.10
Release:        1%{?dist}
Summary:        OpenClaw companion app for the desktop
License:        MIT
URL:            https://github.com/openclaw/openclaw
Source0:        https://github.com/openclaw/openclaw/releases/download/v%{version}/OpenClaw-%{version}-amd64.deb
# sha256:  18d3ba2841c6e82acc6ccdb71cf207f1867fa0c50b9f648c6244e18e8f9d6ff3
Source1:        openclaw-desktop-rpmlintrc
Source2:        https://raw.githubusercontent.com/openclaw/openclaw/v%{version}/LICENSE
ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  zstd
BuildRequires:  desktop-file-utils
BuildRequires:  hicolor-icon-theme
BuildRequires:  python3

Requires:       hicolor-icon-theme
Requires:       libX11.so.6()(64bit)
Requires:       libayatana-appindicator3.so.1()(64bit)
Requires:       libcairo.so.2()(64bit)
Requires:       libdbus-1.so.3()(64bit)
Requires:       libgcc_s.so.1()(64bit)
Requires:       libgdk-3.so.0()(64bit)
Requires:       libgdk_pixbuf-2.0.so.0()(64bit)
Requires:       libgio-2.0.so.0()(64bit)
Requires:       libglib-2.0.so.0()(64bit)
Requires:       libgobject-2.0.so.0()(64bit)
Requires:       libgtk-3.so.0()(64bit)
Requires:       libjavascriptcoregtk-4.1.so.0()(64bit)
Requires:       libsoup-3.0.so.0()(64bit)
Requires:       libwebkit2gtk-4.1.so.0()(64bit)
Requires(post):   desktop-file-utils
Requires(postun): desktop-file-utils

Recommends:     gstreamer1-plugins-bad-free
Recommends:     gstreamer1-plugins-good
Recommends:     xdg-desktop-portal
Recommends:     xdg-desktop-portal-gtk
Suggests:       gstreamer1-libav
Suggests:       xdg-desktop-portal-gnome

%description
OpenClaw is an open-source personal AI assistant that runs on your own computer
and answers in the chats you already use. This package ships the upstream
Linux companion app: a GTK3/WebKitGTK window plus the bundled Bun runtime
that hosts the Control UI. The CLI itself comes from Fedora's openclaw
package or from the upstream installer script the payload carries.

%prep
%setup -q -c -T
ar x %{SOURCE0}
if [ -f data.tar.gz ]; then
  tar xzf data.tar.gz
elif [ -f data.tar.xz ]; then
  tar xf data.tar.xz
elif [ -f data.tar.zst ]; then
  tar --zstd -xf data.tar.zst
else
  echo "ERROR: unexpected data.tar compression in upstream DEB" >&2
  exit 1
fi

%build

%install
install -d -m 0755 %{buildroot}%{_prefix}/lib/OpenClaw
cp -a usr/lib/OpenClaw/desktop-runtime %{buildroot}%{_prefix}/lib/OpenClaw/
install -Dpm0755 usr/lib/OpenClaw/install-cli.sh %{buildroot}%{_prefix}/lib/OpenClaw/install-cli.sh
install -Dpm0755 usr/bin/openclaw-desktop %{buildroot}%{_bindir}/openclaw-desktop
install -Dpm0644 %{SOURCE2} %{buildroot}%{_licensedir}/%{name}/LICENSE

install -d %{buildroot}%{_datadir}/icons/hicolor
for icon in usr/share/icons/hicolor/*/apps/openclaw-desktop.png; do
    size=${icon#usr/share/icons/hicolor/}
    install -Dpm0644 "$icon" %{buildroot}%{_datadir}/icons/hicolor/${size}
done

install -Dpm0644 usr/share/applications/OpenClaw.desktop %{buildroot}%{_datadir}/applications/OpenClaw.desktop

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true
%check
desktop-file-validate %{buildroot}%{_datadir}/applications/OpenClaw.desktop
python3 -c "import json,sys; d=json.load(open('%{buildroot}%{_prefix}/lib/OpenClaw/desktop-runtime/manifest.json')); print('desktop-runtime manifest ok:', d.get('revision'))"

%post
update-desktop-database &> /dev/null || :
touch -- %{_datadir}/icons/hicolor &> /dev/null || :

%postun
update-desktop-database &> /dev/null || :
touch -- %{_datadir}/icons/hicolor &> /dev/null || :

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/openclaw-desktop
%{_prefix}/lib/OpenClaw/
%{_datadir}/applications/OpenClaw.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/openclaw-desktop.png

%changelog
* Wed Nov 25 2026 Ackerman-00 <no-reply> - 2026.11.10-1
- Update to upstream release 2026.11.10
