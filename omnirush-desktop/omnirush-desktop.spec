%global debug_package %{nil}
# prebuilt Bun engine
%global __strip /bin/true
%global __requires_exclude_from ^/opt/omnirush/.*$
%global __provides_exclude_from ^/opt/omnirush/.*$
%global __brp_mangle_shebangs_exclude_from ^/opt/omnirush/.*$
Name:           omnirush-desktop
Version:        3.8.4
Release:        4%{?dist}
Summary:        OmniRush.ai desktop shell (Electron)
License:        SUSE-Freeware
Group:          Productivity/Networking/Talk/Clients
URL:            https://omnirush.ai
Source0:        https://github.com/omnirush-ai/omnirush-gui/releases/download/v3.8.4/omnirush-linux-amd64-3.8.4.deb
# sha256: 5749b6a3d838856d7a619b2054da35082ca9b49251e506488e80aef528f9b2b7
Source1:        omnirush-desktop-rpmlintrc
BuildRequires:  binutils
BuildRequires:  desktop-file-utils
BuildRequires:  tar
BuildRequires:  zstd
Requires:       at-spi2-core
Requires:       hicolor-icon-theme
Requires:       libX11.so.6()(64bit)
Requires:       libXcomposite.so.1()(64bit)
Requires:       libXdamage.so.1()(64bit)
Requires:       libXext.so.6()(64bit)
Requires:       libXfixes.so.3()(64bit)
Requires:       libXrandr.so.2()(64bit)
Requires:       libasound.so.2()(64bit)
Requires:       libatk-1.0.so.0()(64bit)
Requires:       libatk-bridge-2.0.so.0()(64bit)
Requires:       libatspi.so.0()(64bit)
Requires:       libcairo.so.2()(64bit)
Requires:       libcups.so.2()(64bit)
Requires:       libdbus-1.so.3()(64bit)
Requires:       libexpat.so.1()(64bit)
Requires:       libgbm.so.1()(64bit)
Requires:       libgcc_s.so.1()(64bit)
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
Requires:       libxcb.so.1()(64bit)
Requires:       libxkbcommon.so.0()(64bit)
Requires:       xdg-utils
Recommends:     xdg-desktop-portal
Recommends:     xdg-desktop-portal-gtk
ExclusiveArch:  x86_64

%description
OmniRush.ai desktop shell re-packs the upstream .deb payload under /opt.

%prep
%setup -q -c -T
ar x %{SOURCE0}
if [ -f data.tar.gz ]; then tar xzf data.tar.gz
elif [ -f data.tar.xz ]; then tar xf data.tar.xz
elif [ -f data.tar.zst ]; then tar --zstd -xf data.tar.zst
else echo "ERROR: unexpected data.tar compression" >&2; exit 1; fi

%build
:

%install
install -d %{buildroot}/opt %{buildroot}%{_datadir} %{buildroot}%{_bindir}
if [ -d opt/omnirush ]; then cp -a opt/omnirush %{buildroot}/opt/; fi
if [ -d usr/share ]; then cp -a usr/share/* %{buildroot}%{_datadir}/; fi
if [ -d usr/share/applications ]; then install -d %{buildroot}%{_datadir}/applications; fi
ln -sf /opt/omnirush/omnirush %{buildroot}%{_bindir}/omnirush

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true
%check
# engine must match the app's own manifest
sidecars=%{buildroot}/opt/omnirush/resources/sidecars
engine="$sidecars/opencode2-x86_64-unknown-linux-gnu"
want=$(sed -n 's/.*"sha256": "\([0-9a-f]\{64\}\)".*/\1/p' "$sidecars/versions.json" | head -1)
test -n "$want"
printf '%s  %s\n' "$want" "$engine" | sha256sum -c -
"$engine" --version | grep -q '^omnirush v'

%files
/opt/omnirush/
%license /opt/omnirush/LICENSE.electron.txt
%attr(4755, root, root) /opt/omnirush/chrome-sandbox
%{_bindir}/omnirush
%{_datadir}/applications/*
%{_datadir}/doc/omnirush.ai/
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/*/omnirush.png

%post
# mime-version-marker: update-mime-database skips any XML older than the marker, and RPM keeps build mtimes
if command -v update-mime-database >/dev/null 2>&1; then
  rm -f %{_datadir}/mime/version
  update-mime-database %{_datadir}/mime >/dev/null 2>&1 || \
    echo "WARNING: update-mime-database failed; MIME types may be missing" >&2
fi
if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database %{_datadir}/applications >/dev/null 2>&1 || true; fi
if [ -d %{_sysconfdir}/apparmor.d ] && [ -x /sbin/apparmor_parser ] \
   && [ -f /opt/omnirush/resources/apparmor-profile ]; then
  if /sbin/apparmor_parser --skip-kernel-load --debug \
       /opt/omnirush/resources/apparmor-profile >/dev/null 2>&1; then
    install -m 0644 /opt/omnirush/resources/apparmor-profile \
      %{_sysconfdir}/apparmor.d/omnirush
    /sbin/apparmor_parser --replace --write-cache --skip-read-cache \
      %{_sysconfdir}/apparmor.d/omnirush >/dev/null 2>&1 || true
  fi
fi

%postun
if [ "$1" = 0 ] && [ -f %{_sysconfdir}/apparmor.d/omnirush ]; then
  if [ -x /sbin/apparmor_parser ]; then
    /sbin/apparmor_parser --remove %{_sysconfdir}/apparmor.d/omnirush >/dev/null 2>&1 || true
  fi
  rm -f %{_sysconfdir}/apparmor.d/omnirush
fi

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 3.8.4-4
- Release carried no %{?dist}, so all four chroots produced the same NEVR
  (omnirush-desktop-3.8.4-3) and the rawhide/f43/f44/f45 packages were
  indistinguishable in the published repos. Restore the dist tag.

* Fri Nov 13 2026 Ackerman-00 <no-reply> - 3.8.4-3
- Rebuild for the %post MIME fix: clear the stale /usr/share/mime/version marker and re-run update-mime-database.

* Tue Nov 10 2026 Ackerman-00 <no-reply> - 3.8.4-2
- Drop a personal address from the prior changelog entries; metadata only, no payload change.
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 3.8.4-1
- Stop stripping the bundled Bun engine. brp-strip ran `strip -g` on
  resources/sidecars/opencode2-x86_64-unknown-linux-gnu, changing its sha256
  from the 9fc8e7a6... that the app's own versions.json expects to
  2cbcb5fb... and reverting it to the bare Bun runtime (--version 1.4.2
  instead of omnirush v2.0.32). The app therefore reported "Your antivirus
  may have removed omnirush.ai's engine" and refused to start. The engine is
  now byte-identical to the upstream DEB payload.
- Add a %%check that verifies the engine against versions.json, run the engine
  in the install probe, and move the sha256 pin below Source0 so the sweep
  binds it.
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 3.8.4-0
- Update to upstream release 3.8.4
