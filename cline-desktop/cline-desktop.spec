%global debug_package %{nil}
# prebuilt Bun executables
%global __strip /bin/true
%global __requires_exclude_from ^%{_prefix}/lib/Cline/bin/remote-helpers/
%global __provides_exclude_from ^%{_prefix}/lib/Cline/bin/remote-helpers/
Name:           cline-desktop
Version:        0.0.49
Release:        3%{?dist}
Summary:        The agentic coding-capable IDE desktop app (Tauri)
License:        Apache-2.0
Group:          Development/Tools/IDE
URL:            https://cline.bot
Source0:        https://github.com/cline/cline/releases/download/desktop-v0.0.49/Cline_0.0.49_amd64.deb
# sha256: 3e2c1f824fbdceaf67a8c01404e58218f8534f952318d1689807824b9ca2e2f6
Source1:        cline-desktop-rpmlintrc
Source2:        https://raw.githubusercontent.com/cline/cline/desktop-v0.0.49/LICENSE
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  zstd
Requires:       hicolor-icon-theme
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
Recommends:     xdg-desktop-portal
Recommends:     xdg-desktop-portal-gtk
ExclusiveArch:  x86_64

%description
Cline desktop (the agentic coding assistant) ships the upstream DEB payload
as-is: %{_prefix}/lib/Cline (Tauri binary bundle), %{_bindir}/cline-app and
cline-cli, and the desktop/metainfo/icons in %{_prefix}/share. This spec re-packs
those bytes without recompiling.

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
install -d %{buildroot}%{_datadir} %{buildroot}%{_prefix}/lib %{buildroot}%{_bindir}
cp -a usr/share/* %{buildroot}%{_datadir}/
if [ -d usr/lib/Cline ]; then cp -a usr/lib/Cline %{buildroot}%{_prefix}/lib/; fi
for b in usr/bin/*; do install -m 0755 "$b" %{buildroot}%{_bindir}/; done
install -Dm0644 %{SOURCE2} %{buildroot}%{_licensedir}/%{name}/LICENSE

%check
# CLI must not be bare bun
cli=%{buildroot}%{_bindir}/cline-cli
"$cli" --help | grep -q '^Cline CLI'
"$cli" hub --help | grep -q '^Usage: cline hub'
helper=%{buildroot}%{_prefix}/lib/Cline/bin/remote-helpers/cline-x86_64-unknown-linux-gnu
"$helper" --help | grep -q '^Cline CLI'

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/cline-app
%{_bindir}/cline-cli
%{_prefix}/lib/Cline/
%{_datadir}/applications/*
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/metainfo/*

%changelog
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.0.49-3
- Drop a personal address from the prior changelog entries; metadata only, no payload change.
* Tue Nov 10 2026 Ackerman-00 <no-reply> - 0.0.49-2
- Stop stripping the prebuilt Bun executables. brp-strip ran `strip -g` on
  cline-cli and the x86_64 remote helper, which removed their embedded
  entrypoint: cline-cli --version went from 3.0.74 to the Bun runtime's 1.4.2
  and `cline-cli hub ensure` failed with `Script not found "hub"`. The desktop
  window opened but the local hub never started ("No compatible hub runtime is
  available"), so the agent could not run. The shipped bytes are now identical
  to the upstream DEB payload.
- Add a %%check that fails if the staged CLI or x86_64 helper stop recognising
  their own commands, strengthen the install probe to run `cline-cli hub`, and
  move the sha256 pin below Source0 so the sweep binds it.
* Sat Nov 07 2026 Ackerman-00 <no-reply> - 0.0.49-1
- Ship the upstream Apache-2.0 LICENSE (Source2) as %license; fix the update.sh OBS/debian machinery (stray artifacts, invented email) with the repo updater pattern.
* Sat Nov 07 2026 Ackerman-00 <no-reply> - 0.0.49-0
- Initial package
