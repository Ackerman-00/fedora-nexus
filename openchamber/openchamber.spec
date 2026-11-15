%global debug_package %{nil}
%global __os_install_post %{nil}

%global __provides_exclude_from ^/opt/OpenChamber/.*$
%global __requires_exclude_from ^/opt/OpenChamber/.*$

Name:           openchamber
Version:        2.7.2
Release:        2%{?dist}
Summary:        AI coding agent workspace (Electron)
License:        MIT
URL:            https://github.com/openchamber/openchamber
Source0:        https://github.com/openchamber/openchamber/releases/download/v%{version}/OpenChamber-%{version}-linux-x86_64.rpm
# sha256:  6e34bac19c8af2bd48a8142a40cc70f836fd1063c5d65b30ec62157ee3823fa5
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

BuildRequires:  cpio
BuildRequires:  hicolor-icon-theme
BuildRequires:  desktop-file-utils
BuildRequires:  gawk

Requires:       gtk3
Requires:       nss
Requires:       nspr
Requires:       alsa-lib
Requires:       libnotify
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       hicolor-icon-theme
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libX11
Requires:       libxkbcommon
Requires:       libgbm
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       fontconfig
Requires:       freetype
Requires:       cups
Requires:       dbus-libs
Requires:       libsecret
Requires:       systemd-libs

%global _enable_debug_packages 0

%description
OpenChamber is an AI coding agent workspace: chat sessions, background
commands and subagents, file editing, terminal, browser panel, session
management and scheduled tasks, driven by local or remote models.
Compiled specifically for the Nexus repository via automated upstream RPM
repack.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --no-absolute-filenames

%build

%install
install -dm755 %{buildroot}/opt
cp -a opt/OpenChamber %{buildroot}/opt/
find %{buildroot}/opt/OpenChamber -type f | xargs chmod go-w 2>/dev/null || true
chmod 0755 %{buildroot}/opt/OpenChamber/chrome-sandbox

install -dm755 %{buildroot}%{_datadir}
cp -a usr/share/applications %{buildroot}%{_datadir}/
install -dm755 %{buildroot}%{_datadir}/icons
cp -a usr/share/icons/hicolor %{buildroot}%{_datadir}/icons/

install -dm755 %{buildroot}%{_licensedir}/%{name}
install -Dm644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

desktop-file-validate %{buildroot}%{_datadir}/applications/openchamber.desktop
find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license %{_licensedir}/%{name}/LICENSE
%{_datadir}/applications/openchamber.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/openchamber.png
%attr(4755, root, root) /opt/OpenChamber/chrome-sandbox
/opt/OpenChamber/

%post
if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database %{_datadir}/applications >/dev/null 2>&1 || true; fi
if ! { [ -L /proc/self/ns/user ] && unshare --user true; }; then
  chmod 4755 /opt/OpenChamber/chrome-sandbox || true
else
  chmod 0755 /opt/OpenChamber/chrome-sandbox || true
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database %{_datadir}/applications >/dev/null 2>&1 || true; fi

%changelog
* Sun Nov 15 2026 Ackerman-00 <no-reply> - 2.7.2-2
- Rebuild the native .rpm repack unchanged: COPR's importer aborted while
  fetching the 2.7.2-1 SRPM, so the same content was republished to clear
  the failed build
* Sun Nov 15 2026 Ackerman-00 <no-reply> - 2.7.2-1
- Switch the packaging from the upstream AppImage to the native upstream
  .rpm (OpenChamber-2.7.2-linux-x86_64.rpm) repacked exactly like the
  other Fedora-nexus packages. The upstream Electron runtime now installs
  flat under /opt/OpenChamber; no wrapper, no /usr/bin/openchamber link.
