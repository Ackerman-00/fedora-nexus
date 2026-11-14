%global debug_package %{nil}
%global __requires_exclude_from ^/opt/Freebuff/.*$
%global __provides_exclude_from ^/opt/Freebuff/.*$
%global __brp_mangle_shebangs_exclude_from ^/opt/Freebuff/.*$
Name:           freebuff-desktop
Version:        0.0.202
Release:        0%{?dist}
Summary:        Freebuff Desktop (Electron)
License:        SUSE-Freeware
Group:          Development/Tools/IDE
URL:            https://freebuff.com
Source0:        https://github.com/CodebuffAI/codebuff-community/releases/download/freebuff-desktop-v0.0.202/Freebuff-0.0.202-linux-amd64.deb
# sha256: 18710810039ec71e02ee8cabb76d9920af93ea5852199a2fcd9b2fff34d2fe8a
Source1:        freebuff-desktop-rpmlintrc
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  zstd
BuildRequires:  desktop-file-utils
Requires:       at-spi2-core
Requires:       libasound.so.2()(64bit)
Requires:       libatk-1.0.so.0()(64bit)
Requires:       libatk-bridge-2.0.so.0()(64bit)
Requires:       libatspi.so.0()(64bit)
Requires:       libcairo.so.2()(64bit)
Requires:       libcups.so.2()(64bit)
Requires:       libdbus-1.so.3()(64bit)
Requires:       libdrm.so.2()(64bit)
Requires:       libexpat.so.1()(64bit)
Requires:       libgcc_s.so.1()(64bit)
Requires:       libgbm.so.1()(64bit)
Requires:       libgio-2.0.so.0()(64bit)
Requires:       libglib-2.0.so.0()(64bit)
Requires:       libgobject-2.0.so.0()(64bit)
Requires:       libgtk-3.so.0()(64bit)
Requires:       libnotify.so.4()(64bit)
Requires:       libnspr4.so()(64bit)
Requires:       libnss3.so()(64bit)
Requires:       libnssutil3.so()(64bit)
Requires:       libpango-1.0.so.0()(64bit)
Requires:       libpipewire-0.3.so.0()(64bit)
Requires:       libpulse.so.0()(64bit)
Requires:       libsecret-1.so.0()(64bit)
Requires:       libsmime3.so()(64bit)
Requires:       libstdc++.so.6()(64bit)
Requires:       libudev.so.1()(64bit)
Requires:       libX11.so.6()(64bit)
Requires:       libxcb.so.1()(64bit)
Requires:       libXcomposite.so.1()(64bit)
Requires:       libXdamage.so.1()(64bit)
Requires:       libXext.so.6()(64bit)
Requires:       libXfixes.so.3()(64bit)
Requires:       libxkbcommon.so.0()(64bit)
Requires:       libXrandr.so.2()(64bit)
Requires:       libcurl.so.4()(64bit)
Requires:       libz.so.1()(64bit)
Requires:       libuuid.so.1()(64bit)
Requires:       libXtst.so.6()(64bit)
Requires:       xdg-utils
Requires:       hicolor-icon-theme
Recommends:     xdg-desktop-portal
Recommends:     xdg-desktop-portal-gtk
ExclusiveArch:  x86_64

%description
Freebuff Desktop is the graphical Freebuff coding agent. This package re-packs
the upstream .deb payload under /opt/Freebuff and installs the upstream desktop
entry and icon, so it is the only Freebuff package in the application menu.

The bundle carries its own Bun runtime, git and orchestrator, so it does not
need the freebuff command-line package. The terminal agent is packaged
separately as freebuff and keeps the /usr/bin/freebuff name; this package
provides /usr/bin/freebuff-desktop.

%prep
%setup -q -c -T
ar x %{SOURCE0}
if [ -f data.tar.xz ]; then tar xf data.tar.xz
elif [ -f data.tar.zst ]; then tar --zstd -xf data.tar.zst
elif [ -f data.tar.gz ]; then tar xzf data.tar.gz
else echo "ERROR: unexpected data.tar compression in upstream DEB" >&2; exit 1; fi

%build
:

%install
install -d %{buildroot}/opt %{buildroot}%{_bindir}
cp -a opt/Freebuff %{buildroot}/opt/

# explicit paths, no cp -a
install -Dpm0644 usr/share/applications/freebuff.desktop \
    %{buildroot}%{_datadir}/applications/freebuff.desktop
install -Dpm0644 usr/share/doc/freebuff/changelog.gz \
    %{buildroot}%{_datadir}/doc/freebuff/changelog.gz
for icon in usr/share/icons/hicolor/*/apps/freebuff.png; do
    size=${icon#usr/share/icons/hicolor/}
    install -Dpm0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/$size"
done

# GUI launcher name
ln -s /opt/Freebuff/freebuff %{buildroot}%{_bindir}/freebuff-desktop

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true
%check
desktop-file-validate %{buildroot}%{_datadir}/applications/freebuff.desktop

%files
/opt/Freebuff/
%license /opt/Freebuff/LICENSE.electron.txt
%attr(4755, root, root) /opt/Freebuff/chrome-sandbox
%{_bindir}/freebuff-desktop
%{_datadir}/applications/freebuff.desktop
%dir %{_datadir}/doc/freebuff
%{_datadir}/doc/freebuff/changelog.gz
%{_datadir}/icons/hicolor/*/apps/freebuff.png

%changelog
* Wed Nov 11 2026 Ackerman-00 <no-reply> - 0.0.202-0
- Update to upstream release 0.0.202
